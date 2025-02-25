from app import db
from app import Lendee, BankStatement
from flask import jsonify
import openai_helper
import os
from dotenv import load_dotenv

load_dotenv()
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
def check_user_and_statements(lendee_name):
    """Check if a user exists and has at least one bank statement."""
    user = Lendee.query.get(lendee_name)
    if not user:
        return False
    return db.session.query(BankStatement.lendee_name).filter_by(lendee_name=lendee_name).count() > 0

def query_for_verdict(lendee_name):
    bank_statements = BankStatement.query.filter_by(lendee_name=lendee_name).all()

    # Extract file_ids from all bank_statements to give to OpenAI assistant
    file_ids = [statement.file_id for statement in bank_statements]

    # Pass all file_ids to assistant
    thread_id = openai_helper.create_openai_thread()
    if not thread_id:
        return jsonify({"error": "Failed to create OpenAI thread"}), 500
    openai_helper.attach_files_to_thread(thread_id, file_ids)

    # Send query to assistant to analyze bank statements
    query = ("""
                Analyze these bank statements to provide a detailed pros and cons list to a bank as to why a prospective 
                lendee should or should not get a loan. Please reply only in the form of a dictionary, where there are two
                keys: "pros" and "cons". For each key, please make the value a list of strings, where each string would 
                be a bullet point "pro" or "con". 
            """)
    openai_helper.send_message_to_assistant(thread_id, query)

    # Retrieve response from JSON
    # response = openai_helper.get_assistant_response(thread_id)["content"][0]["text"]["value"]
    response = openai_helper.get_assistant_response(thread_id)
    return response
