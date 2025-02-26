from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from models import db, Lendee, BankStatement
import openai_helper
import utils
import json


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
    if "file" not in request.files or "lendee_name" not in request.form:
        return jsonify({"error": "File and lendee name are required"}), 400

    files = request.files.getlist("file")  # Get multiple files
    lendee_name = request.form["lendee_name"]

    lendee = Lendee.query.filter_by(name=lendee_name).first()
    if not lendee:
        return jsonify({"error": "Lendee not found"}), 404

    uploaded_files = []

    for file in files:
        response = openai_helper.upload_pdf_to_openai(file)

        # Store in database
        new_statement = BankStatement(
            filename=file.filename,
            file_id=response["file_id"],  # Store OpenAI's file ID
            lendee_name=lendee_name
        )
        db.session.add(new_statement)
        uploaded_files.append(new_statement.to_dict())  # Append file info

    db.session.commit()

    return jsonify({
        "message": "Files uploaded successfully!",
        "bank_statements": uploaded_files
    }), 201
csrf.exempt(upload_files)

@app.route("/get_verdict", methods=["POST"])
def get_verdict():
    data = request.json
    lendee_name = data.get("lendee_name")

    if not lendee_name:
        return jsonify({"error": "Missing lendee name"}), 400

    if not utils.check_user_and_statements(lendee_name):
        return jsonify({"error": "User not found or no bank statements available"}), 404

    response = utils.query_for_verdict(lendee_name)

    if response["valid_documents"] == False:
        return jsonify({"error": response["reason"]}), 400
    return response["pros_cons"], 200
csrf.exempt(get_verdict)

@app.route("/graph_stats", methods=["POST"])
def graph_stats():
    data = request.json
    lendee_name = data.get("lendee_name")

    # Doesn't perform checks on lendee_name or bank statements due to being called in conjunction with get_verdict()
    response = utils.query_for_graph_stats(lendee_name)


csrf.exempt(graph_stats)

if __name__ == '__main__':
    app.run(debug=True)
