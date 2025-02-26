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

def get_or_create_thread(lendee_name):
    """Retrieve an existing thread for the lendee or create a new one."""
    lendee = Lendee.query.filter_by(name=lendee_name).first()

    if lendee and lendee.thread_id:
        return lendee.thread_id  # Return existing thread ID

    # If no thread exists, create a new one
    thread_id = openai_helper.create_openai_thread()

    # Save thread_id in the database
    if lendee:
        lendee.thread_id = thread_id
        db.session.commit()


def query_for_verdict(lendee_name):
    bank_statements = BankStatement.query.filter_by(lendee_name=lendee_name).all()

    # Extract file_ids from all bank_statements to give to OpenAI assistant
    file_ids = [statement.file_id for statement in bank_statements]

    # Pass all file_ids to assistant
    thread_id = get_or_create_thread(lendee_name)
    if not thread_id:
        return jsonify({"error": "Failed to create OpenAI thread"}), 500
    file_attachment_error = openai_helper.attach_files_to_thread(thread_id, file_ids)
    if file_attachment_error:
        return jsonify({"error": file_attachment_error}), 500

    # Send query to assistant to analyze bank statements
    query = (f"""
    You are an AI financial analyst responsible for reviewing bank statements.
    
    Before providing a loan assessment, first verify that all uploaded PDFs contain financial information **belonging to the same individual**.
    
    **Steps to follow:**
    1. **Check consistency:** Ensure that all PDFs have transactions tied to a single lendee. If there exist statements 
    where the name is redacted, assume it is tied to the single lendee, granted that all other statements with names are tied to a single lendee
    2. **Look for mismatched names or account details:** If documents appear to be unrelated (e.g., different account holders or unrelated transactions), **explicitly state that they are unrelated**.
    3. If all statements are valid and belong to the single lendee, proceed with generating the **pros and cons list**.
    
    ### Important Instructions:
    - **Do NOT include citations, footnotes, or source markers (e.g.,  ) in your - **Only return a clean JSON object without any additional formatting.**
    - **Extract and use information from ALL uploaded files but do NOT attempt to reference them using in-text citations.**
    - **Make the output a JSON string, such that I can run json.loads(output) to index into the "pros_cons" list.**
    
    **Output Format:**
    {{
    "valid_documents": <true/false>,
    "reason": "<Explanation if unrelated>",
    "pros_cons": {{
        "pros": [<List of financial strengths>],
        "cons": [<List of financial weaknesses>]
        }}
    }}
    """)
    openai_helper.send_message_to_assistant(thread_id, query)

    # Retrieve response
    response = openai_helper.get_assistant_verdict(thread_id)
    return response

def query_for_graph_stats(lendee_name):
    # Get existing lendee thread_id
    thread_id = get_or_create_thread(lendee_name)

    query = ("""
        Pass 
    """)
    # Retrieve response
    response = openai_helper.get_assistant_graph_stats(thread_id)
    return response