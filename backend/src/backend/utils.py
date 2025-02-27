from app import db
from app import Lendee, BankStatement
from flask import jsonify
import openai_helper
import os
from dotenv import load_dotenv

load_dotenv()
SUMMARIZING_ASSISTANT_ID = os.getenv("SUMMARIZING_ASSISTANT_ID")
BALANCE_ASSISTANT_ID = os.getenv("BALANCE_ASSISTANT_ID")
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
    file_attachment_error = openai_helper.attach_files_to_thread(thread_id, file_ids)
    if file_attachment_error:
        return jsonify({"error": file_attachment_error}), 500

    # Send query to assistant to analyze bank statements
    query = (f"""
    You are an AI financial analyst responsible for reviewing bank statements from a small business requesting a loan.
    
    Before providing a loan assessment, first verify that all uploaded PDFs contain financial information **belonging to the same individual**.
    
    **Steps to follow:**
    1. **Check consistency:** Ensure that all PDFs have transactions tied to a single lendee. If there exist statements 
    where the name is redacted, assume it is tied to the single lendee, granted that all other statements with names are tied to a single lendee
    2. **Look for mismatched names or account details:** If documents appear to be unrelated (e.g., different account holders or irrelevant documents), **explicitly state that they are unrelated**.
    3. If all statements are valid and belong to the single lendee, proceed with generating the **pros and cons list**.
    
    ### Important Instructions:
    - **Do NOT include citations, footnotes, or source markers (e.g.,  ) in your - **Only return a clean JSON object without any additional formatting.**
    - **Extract and use information from ALL uploaded files but do NOT attempt to reference them using in-text citations.**
    - **Make the output a JSON string, such that I can run json.loads(output) to index into the "pros_cons" list.**
    
    **Output Format:**
    {{
    "query_flag": "verdict",
    "valid_documents": <true/false>,
    "reason": "<Explanation if unrelated or irrelevant documents>",
    "pros_cons": {{
        "pros": [<List of financial strengths>],
        "cons": [<List of financial weaknesses>]
        }}
    }}
    """)
    run_id = openai_helper.send_message_to_assistant(thread_id, query, assistant_type="summarizing")

    # Retrieve response
    response = openai_helper.get_assistant_verdict(thread_id, run_id)
    return response

def all_balances_over_time(lendee_name):
    """Generates balance over time for all bank statements associated with lendee. """
    # Query all bank statements for this lendee
    bank_statements = BankStatement.query.filter_by(lendee_name=lendee_name).all()

    if not bank_statements:
        return jsonify({"error": "No bank statements found for this lendee"}), 404

    # Parse out
def balance_over_time(lendee_name):
    """Generates balance over time for single page from bank statement. """
    # Get thread ID for this lendee (reuse or create new)
    thread_id = openai_helper.create_openai_thread()

    # Define query to extract end-of-day balances grouped by bank
    query = ("""
            Respond with a JSON list of every balance found in the bank statement in the format ({date}, {balance}). 
            Look at every balance. Only respond with this list. Do not respond with anything else. If this provided PDF 
            does not have a balance sheet, simply respond with an empty list in the "balances" field. 

            ### **Output Format (Replace <transaction date>, and <balance on transaction date> and Populate Data Correctly)**
            {
                "balances": [
                        { "date": "<transaction date>", "balance": <balance on transaction date> },
                        { "date": "<transaction date>", "balance": <balance on transaction date> }
                    ]
            }

            Ensure the response is a properly formatted JSON string that can be processed with `json.loads(output)`. No additional text, explanations, or formatting should be included in the response.
            """)

    # Send request to OpenAI Assistant
    run_id = openai_helper.send_message_to_assistant(thread_id, query, assistant_type="balancing")

    # Retrieve response
    response = openai_helper.get_assistant_verdict(thread_id, run_id)
    return response