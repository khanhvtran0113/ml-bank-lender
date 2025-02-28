import fitz
from werkzeug.datastructures import FileStorage
from app import db
from app import Lendee, BankStatement
from flask import jsonify
import openai_helper
import time
import openai
import os
from dotenv import load_dotenv

load_dotenv()
SUMMARIZING_ASSISTANT_ID = os.getenv("SUMMARIZING_ASSISTANT_ID")
BALANCE_ASSISTANT_ID = os.getenv("BALANCE_ASSISTANT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.Client(api_key=OPENAI_API_KEY)
def check_user_and_statements(lendee_name):
    """Check if a user exists and has at least one bank statement."""
    user = Lendee.query.get(lendee_name)
    if not user:
        return False
    return db.session.query(BankStatement.lendee_name).filter_by(lendee_name=lendee_name).count() > 0

def split_pdf_pages(file: FileStorage):
    """Splits a PDF into separate pages and returns a list of byte streams."""
    file.seek(0)
    file_bytes = file.read()
    pdf_document = fitz.open(stream=file_bytes, filetype="pdf")  # Load PDF from memory
    pages = []

    for page_number in range(len(pdf_document)):
        new_pdf = fitz.open()  # Create a new blank PDF
        new_pdf.insert_pdf(pdf_document, from_page=page_number, to_page=page_number)

        # Convert single-page PDF to bytes
        pdf_bytes = new_pdf.write()
        pages.append(pdf_bytes)

    return pages  # List of byte streams, each representing a page


def create_thread():
    thread_id = openai_helper.create_openai_thread()
    if not thread_id:
        return jsonify({"error": "Failed to create OpenAI thread"}), 500
    return thread_id

def attach_media(thread_id, file_id):
    file_attachment_error = openai_helper.attach_file_to_thread(thread_id, file_id)
    if file_attachment_error:
        return jsonify({"error": file_attachment_error}), 500

def query_for_verdict(thread_id):
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
        "currency": "<currency of balance>",
        "pros": [<List of financial strengths>],
        "cons": [<List of financial weaknesses>]
        }}
    }}
    """)
    print("SENDING VERDICT MESSAGE")
    openai_helper.send_message(thread_id, query)

    # Retrieve response
    print("CREATING VERDICT RUN")
    run = openai_helper.run_thread_until_success(thread_id, "summarizing")
    return openai_helper.get_message_from_run(thread_id, run, "summarizing")


def query_for_balance(thread_id):
    single_page_query = ("""
       Respond with a JSON list of every balance found in the bank statement in the format ({date}, {balance}). 
       Look at every single transaction in the included table. Only respond with this list. Do not respond with anything else. If this provided PDF 
       does not have a balance sheet, simply respond with an empty list in the "balances" field. 

        ### Important Instructions:
        - **Do NOT include citations, footnotes, or source markers (e.g.,  ) in your - **Only return a CLEAN JSON object without any additional formatting.**
        - **Ignore entries in the statement not explicitly in a "Balance" or "Balances" column. For example, don't include 
        information in an "Amounts" column.**
        - **If you see an OVERALL balance at the start of the document, ignore. Look only for numbers under a column with 
        the word "Balance".**
       ### **Output Format (Replace <transaction date>, and <balance on transaction date> and Populate Data Correctly)**
       {
           "balances": [
                   { "date": "<transaction date in DAY-MONTH NAME-YEAR>", "balance": <balance on transaction date> },
                   { "date": "<transaction date in DAY-MONTH NAME-YEAR>", "balance": <balance on transaction date> }
               ]
       }

       Ensure the response is a properly formatted JSON string that can be processed with `json.loads(output)`. No additional text, explanations, or formatting should be included in the response.
       """)

    # Send message to the thread
    print("SENDING MESSAGE")
    openai_helper.send_message(thread_id, single_page_query)

    # Run and poll until successful message
    print("CREATING RUN")
    run = openai_helper.run_thread_until_success(thread_id, "balancing")

    # Get message
    return openai_helper.get_message_from_run(thread_id, run, "balancing")

