from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Lendee(db.Model):
    name = db.Column(db.String(100), primary_key=True)  # Name as primary key
    def to_dict(self):
        return {"name": self.name,
                "bank_statements": [statement.to_dict() for statement in self.bank_statements]}

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
