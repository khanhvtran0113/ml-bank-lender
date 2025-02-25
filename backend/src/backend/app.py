from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from models import db, Lendee, BankStatement
import openai_helper
import utils

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

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files or "lendee_name" not in request.form:
        return jsonify({"error": "File and lendee name are required"}), 400

    file = request.files["file"]
    lendee_name = request.form["lendee_name"]

    lendee = Lendee.query.filter_by(name=lendee_name).first()
    if not lendee:
        return jsonify({"error": "Lendee not found"}), 404

    response = openai_helper.upload_pdf_to_openai(file)

    # Store in database
    new_statement = BankStatement(
        filename=file.filename,
        file_id=response["file_id"],  # Store OpenAI's file ID
        lendee_name=lendee_name
    )
    db.session.add(new_statement)
    db.session.commit()

    return jsonify({"message": "File uploaded successfully!", "bank_statement": new_statement.to_dict()}), 201
csrf.exempt(upload_file)

@app.route("/getverdict", methods=["POST"])
def get_verdict():
    data = request.json
    lendee_name = data.get("lendee_name")

    if not lendee_name:
        return jsonify({"error": "Missing lendee name"}), 400

    if not utils.check_user_and_statements(lendee_name):
        return jsonify({"error": "User not found or no bank statements available"}), 404

    return jsonify({"message": "User validated successfully!"})
csrf.exempt(get_verdict)

if __name__ == '__main__':
    app.run(debug=True)
