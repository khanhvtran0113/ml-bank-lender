from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Lendee(db.Model):
    name = db.Column(db.String(100), primary_key=True)  # Name as primary key
    verdict_json = db.Column(db.Text, nullable=True)  # Stores verdict output JSON
    balance_json = db.Column(db.Text, nullable=True)  # Stores balance over time JSON
    bank_statement_id = db.Column(db.Integer, db.ForeignKey("bank_statement.id"), unique=True, nullable=True)
    interactive_thread_id = db.Column(db.String(255), unique=True, nullable=True)  # Store thread ID

    # One-to-One relationship
    bank_statement = db.relationship("BankStatement", backref="lendee", uselist=False)

    def to_dict(self):
        """Convert Lendee object to a dictionary for API response."""
        return {
            "name": self.name,
            "verdict_json": self.verdict_json if self.verdict_json else None,
            "balance_json": self.balance_json if self.balance_json else None,
            "bank_statement": self.bank_statement.to_dict() if self.bank_statement else None,
            "interactive_thread_id": self.interactive_thread_id if self.interactive_thread_id else None
        }


class BankStatement(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False)
    file_id = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        """Convert BankStatement object to a dictionary for API response."""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_id": self.file_id
        }