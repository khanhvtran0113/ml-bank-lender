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

def query_for_verdict(file_id):
    # Pass all file_ids to assistant
    thread_id = openai_helper.create_openai_thread()
    if not thread_id:
        return jsonify({"error": "Failed to create OpenAI thread"}), 500
    file_attachment_error = openai_helper.attach_file_to_thread(thread_id, file_id)
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
    "currency": "<currency of balance>",
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

def query_for_balance(thread_ids):
    single_page_query = ("""
       Respond with a JSON list of every balance found in the bank statement in the format ({date}, {balance}). 
       Look at every single transaction in the included table. Only respond with this list. Do not respond with anything else. If this provided PDF 
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

    # Send message to all the threads
    threads_to_run_ids = {}
    for thread in thread_ids:
        threads_to_run_ids[thread] = openai_helper.send_message_to_assistant(thread, single_page_query,
                                                                             assistant_type="balancing")

    # Poll on all the threads
    responses = []
    page_num = 1
    areAllDone = False
    while not areAllDone:
        areAllDone = True
        for thread_id in threads_to_run_ids.keys():
            run_id = threads_to_run_ids[thread_id]
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.status == "failed" or run.status == "cancelling" or run.status == "cancelled" or run.status == "expired" or run.status == "requires_action":
                print("RESTARTING RUN")
                # Cancel run and restart
                client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)
                threads_to_run_ids[thread_id] = openai_helper.send_message_to_assistant(thread, single_page_query,
                                                                             assistant_type="balancing")
            if run.status != "completed":
                areAllDone = False
            else:
                print("RUN COMPLETED")
        time.sleep(5)

    page_num = 1
    for thread_id in threads_to_run_ids.keys():
        print(f"NOW READING RESPONSE PAGE {page_num}")
        run_id = threads_to_run_ids[thread_id]
        response = openai_helper.get_assistant_verdict(thread_id, run_id)
        print(response)
        responses.append(response)
        page_num += 1

    # Combine all dictionaries
    merged_balances = {"balances": []}
    for response in responses:
        if "balances" in response:
            merged_balances["balances"].extend(response["balances"])
    return merged_balances