from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from models import db, Lendee, BankStatement
import openai_helper
import utils
import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()
SUMMARIZING_ASSISTANT_ID = os.getenv("SUMMARIZING_ASSISTANT_ID")
BALANCE_ASSISTANT_ID = os.getenv("BALANCE_ASSISTANT_ID")

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
csrf = CSRFProtect(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lendees.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    all_threads = openai.beta.threads.list()
    for thread in all_threads:
        if thread["assistant_id"] == SUMMARIZING_ASSISTANT_ID or thread["assistant_id"] == BALANCE_ASSISTANT_ID:
            try:
                openai.beta.threads.delete(thread["id"])
                print(f"Deleted thread {thread["id"]}")
            except Exception as e:
                print(f"Error deleting thread {thread["id"]}: {e}")

    return jsonify({"message": "Welcome to the Loan Management API!"})

# Route to add a new lendee
@app.route("/api/lendees", methods=["POST"])
def add_lendee():
    data = request.json
    if "name" not in data or not data["name"]:
        return jsonify({"error": "Name is required"}), 400

    # Check if the lendee already exists
    existing_lendee = Lendee.query.filter_by(name=data["name"]).first()
    if existing_lendee:
        return jsonify({"error": "Lendee already exists"}), 409

    new_lendee = Lendee(name=data["name"])
    db.session.add(new_lendee)
    db.session.commit()
    return jsonify({"message": "Lendee added successfully!", "lendee": new_lendee.to_dict()}), 201
csrf.exempt(add_lendee)

@app.route("/api/bank_statements", methods=["GET"])
def get_all_bank_statements():
    """Retrieve all uploaded bank statements from the database."""
    bank_statements = BankStatement.query.all()  # Fetch all records

    if not bank_statements:
        return jsonify({"message": "No bank statements found"}), 404

    # Convert each BankStatement object into a dictionary
    statements_data = [statement.to_dict() for statement in bank_statements]

    return jsonify({"bank_statements": statements_data}), 200

@app.route("/api/lendees", methods=["GET"])
def list_lendees():
    """Retrieve and return a list of all lendees."""
    lendees = Lendee.query.all()

    if not lendees:
        return jsonify({"message": "No lendees found"}), 404

    # Convert lendees to a JSON-compatible format
    lendee_list = [lendee.to_dict() for lendee in lendees]

    return jsonify({"lendees": lendee_list}), 200

@app.route("/upload", methods=["POST"])
def upload_files():
    # Get the uploaded file and lendee name
    if "file" not in request.files or "lendee_name" not in request.form:
        return jsonify({"error": "File and lendee name are required"}), 400
    files = request.files.getlist("file")
    file = files[0]
    lendee_name = request.form["lendee_name"]

    lendee = Lendee.query.filter_by(name=lendee_name).first()
    if not lendee:
        return jsonify({"error": "Lendee not found"}), 404

    # Check if the lendee already has a bank statement
    if lendee.bank_statement:
        # If a statement exists, delete it before adding a new one
        db.session.delete(lendee.bank_statement)
        db.session.commit()

    # Upload entire pdf and store that in database
    file_id = openai_helper.upload_pdf_to_openai(file)
    new_statement = BankStatement(
        filename=file.filename,
        file_id=file_id
    )
    db.session.add(new_statement)
    db.session.commit()
    lendee.bank_statement_id = new_statement.id
    db.session.commit()

    print("QUERY FOR VERDICT")
    # Query for verdict
    thread_id = openai_helper.create_openai_thread()
    if not thread_id:
        return jsonify({"error": "Failed to create OpenAI thread"}), 500
    file_attachment_error = openai_helper.attach_file_to_thread(thread_id, file_id)

    if file_attachment_error:
        return jsonify({"error": file_attachment_error}), 500

    response = utils.query_for_verdict(thread_id)
    if response["valid_documents"] == False:
        return jsonify({"error": response["reason"]}), 400

    print("STORING VERDICT IN DATABASE")
    # Store verdict in database
    lendee.verdict_json = json.dumps(response["pros_cons"])
    db.session.commit()

    print("SPLITTING PAGES")
    # Get list of byte streams for each page
    pages = utils.split_pdf_pages(file)

    # Get list of media ids from open ai
    page_ids = [openai_helper.upload_pdf_to_openai(page) for page in pages]

    print("CREATING THREADS FOR EACH PAGE")
    # Create threads
    thread_ids = [utils.create_thread() for _ in page_ids]

    # Attach media to all the threads
    print("ATTACHING MEDIA TO THREADS")
    for thread, page_id in zip(thread_ids, page_ids):
        utils.attach_media(thread, page_id)

    # Get balances
    print("GETTING BALANCES")
    balances = [utils.query_for_balance(thread_id) for thread_id in thread_ids]

    # Merge balances
    merged_balances = {"balances": []}
    for response in balances:
        if "balances" in response:
            merged_balances["balances"].extend(response["balances"])
    print(merged_balances)
    print("MERGED BALANCES")
    # Store the combined results in the database
    lendee.balance_json = json.dumps(merged_balances)
    db.session.commit()

    # Clean up file uploads for single page files on OpenAI
    for page_id in page_ids:
        openai_helper.delete_openai_file(page_id)

    return jsonify({
        "message": "Files uploaded successfully!"
    }), 201
csrf.exempt(upload_files)

@app.route("/ask_question", methods=["POST"])
def ask_question():
    """Allows users to ask a question and get an answer from the assistant."""
    data = request.json
    lendee_name = data.get("lendee_name")
    question = data.get("question")

    if not lendee_name or not question:
        return jsonify({"error": "Both lendee_name and question are required"}), 400

    lendee = Lendee.query.filter_by(name=lendee_name).first()

    if not lendee:
        return jsonify({"error": "Lendee not found"}), 404

    # Ensure the lendee has an associated bank statement
    if not lendee.bank_statement:
        return jsonify({"error": "No bank statement found for this lendee"}), 404

    # Retrieve the file_id of the associated bank statement
    file_id = lendee.bank_statement.file_id

    # If no thread exists for Q&A, create a new one and store it
    if not lendee.interactive_thread_id:
        thread_id = openai_helper.create_openai_thread()
        lendee.interactive_thread_id = thread_id
        db.session.commit()
    else:
        thread_id = lendee.interactive_thread_id  # Use the existing thread

    print("ATTACHING BANK STATEMENT TO THREAD")
    utils.attach_media(thread_id, file_id)  # Attach bank statement to thread

    print("SENDING MESSAGE")
    openai_helper.send_message(thread_id, question)

    # Run and poll until successful message
    print("CREATING RUN")
    run = openai_helper.run_thread_until_success(thread_id, "summarizing")

    # Get message
    return openai_helper.get_message_from_interactive_run(thread_id, run)
csrf.exempt(ask_question)

@app.route("/clear_thread", methods=["POST"])
def clear_thread():
    """Clears all messages for a given lendee's assistant thread by deleting and recreating the thread."""
    data = request.json
    lendee_name = data.get("lendee_name")

    if not lendee_name:
        return jsonify({"error": "lendee_name is required"}), 400

    lendee = Lendee.query.filter_by(name=lendee_name).first()

    if not lendee:
        return jsonify({"error": "Lendee not found"}), 404

    if not lendee.interactive_thread_id:
        return jsonify({"error": "No existing thread found for this lendee"}), 404

    # Step 1: Delete the existing thread from OpenAI
    thread_id = lendee.interactive_thread_id
    delete_success = openai_helper.delete_assistant_thread(thread_id)

    if not delete_success:
        return jsonify({"error": "Failed to delete the existing thread"}), 500

    # Step 2: Create a new thread and update the database
    new_thread_id = openai_helper.create_openai_thread()
    lendee.interactive_thread_id = new_thread_id
    db.session.commit()

    return jsonify({
        "message": "Thread cleared successfully",
        "new_thread_id": new_thread_id
    }), 200
csrf.exempt(clear_thread)
@app.route("/lendees/<string:lendee_name>", methods=["GET"])
def get_lendee_data(lendee_name):
    """Retrieve all stored information for a given lendee."""
    lendee = Lendee.query.filter_by(name=lendee_name).first()

    if not lendee:
        return jsonify({"error": "Lendee not found"}), 404

    # Convert stored JSON strings back into dictionaries before returning
    lendee_data = {
        "name": lendee.name,
        "verdict_json": json.loads(lendee.verdict_json) if lendee.verdict_json else None,
        "balance_json": json.loads(lendee.balance_json) if lendee.balance_json else None
    }

    return jsonify(lendee_data), 200

if __name__ == '__main__':
    app.run(debug=True)
