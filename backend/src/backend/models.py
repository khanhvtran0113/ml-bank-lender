from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Lendee(db.Model):
    name = db.Column(db.String(100), primary_key=True)  # Name as primary key
    verdict_json = db.Column(db.Text, nullable=True)  # Stores verdict output JSON
    balance_json = db.Column(db.Text, nullable=True)  # Stores balance over time JSON
    bank_statements = db.relationship("BankStatement", backref="lendee", lazy=True)

    def to_dict(self):
        """Convert Lendee object to a dictionary for API response."""
        return {
            "name": self.name,
            "verdict_json": self.verdict_json if self.verdict_json else None,
            "balance_json": self.balance_json if self.balance_json else None
        }

class BankStatement(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False)
    file_id = db.Column(db.String(255), nullable=False)  # OpenAI file ID
    lendee_name = db.Column(db.String(100), db.ForeignKey("lendee.name"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "file_id": self.file_id,
            "lendee_name": self.lendee_name
        }
