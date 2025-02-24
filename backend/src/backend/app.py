from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import openai_helper

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
csrf = CSRFProtect(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lendees.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define the Lendee model (with name as primary key)
class Lendee(db.Model):
    name = db.Column(db.String(100), primary_key=True)  # Name as primary key
    def to_dict(self):
        return {"name": self.name}

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
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    response = openai_helper.upload_pdf_to_openai(file)
    return jsonify(response)

@app.route("/api/lendees", methods=["GET"])
def get_lendees():
    lendees = Lendee.query.all()
    return jsonify({"lendees": [lendee.to_dict() for lendee in lendees]})

if __name__ == '__main__':
    app.run(debug=True)
