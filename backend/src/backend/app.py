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
    response = utils.query_for_verdict(file_id)
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
    for thread, page_id in zip(thread_ids, page_ids):
        utils.attach_media(thread, page_id)

    merged_balances = utils.query_for_balance(thread_ids)
    print(merged_balances)
    print("MERGED BALANCES")
    # Store the combined results in the database
    lendee.balance_json = json.dumps(merged_balances)
    db.session.commit()

    return jsonify({
        "message": "Files uploaded successfully!"
    }), 201
csrf.exempt(upload_files)

@app.route("/get_verdict", methods=["POST"])
def get_verdict():
    data = request.json
    lendee_name = data.get("lendee_name")

    if not lendee_name:
        return jsonify({"error": "Missing lendee name"}), 400

    lendee = Lendee.query.filter_by(name=lendee_name).first()

    if not utils.check_user_and_statements(lendee_name):
        return jsonify({"error": "User not found or no bank statements available"}), 404

    response = utils.query_for_verdict(lendee_name)
    if response["valid_documents"] == False:
        return jsonify({"error": response["reason"]}), 400

    # Store verdict in database
    lendee.verdict_json = json.dumps(response["pros_cons"])
    db.session.commit()

    return response["pros_cons"], 200
csrf.exempt(get_verdict)

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
