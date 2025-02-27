import openai
import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()  # Load API keys from .env file

openai.api_key = os.getenv("OPENAI_API_KEY")
SUMMARIZING_ASSISTANT_ID = os.getenv("SUMMARIZING_ASSISTANT_ID")
BALANCE_ASSISTANT_ID = os.getenv("BALANCE_ASSISTANT_ID")

# Store uploaded file IDs
uploaded_file_id = None

def upload_pdf_to_openai(file_stream):
    """Uploads a PDF file to OpenAI Assistants API and stores the file ID."""
    global uploaded_file_id

    file_response = openai.files.create(
        file=("document.pdf", file_stream, "application/pdf"),  # Correct format
        purpose="assistants"
    )

    return file_response.id
def create_openai_thread():
    """Creates an internal conversation thread with OpenAI Assistant."""
    url = "https://api.openai.com/v1/threads"
    headers = {"Authorization": f"Bearer {openai.api_key}", "Content-Type": "application/json", "OpenAI-Beta": "assistants=v2"}

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()["id"]
    return None

def attach_file_to_thread(thread_id, file_id):
    """Attach bank statements to the OpenAI thread (internal process)."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {"Authorization": f"Bearer {openai.api_key}", "Content-Type": "application/json", "OpenAI-Beta": "assistants=v2"}

    payload = {"attachments": [{"file_id": file_id, "tools": [{"type": "file_search"}]}], "role": "user", "content": f"Attaching file {file_id}",}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed to attach file {file_id}: {response.text}")
        return response.text
    return None

def attach_files_to_thread(thread_id, file_ids):
    """Attach bank statements to the OpenAI thread (internal process)."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {"Authorization": f"Bearer {openai.api_key}", "Content-Type": "application/json", "OpenAI-Beta": "assistants=v2"}

    payload = {"attachments": [{"file_id": file_id, "tools": [{"type": "file_search"}]} for file_id in file_ids], "role": "user", "content": f"Attaching files {file_ids}",}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Failed to attach file {file_ids}: {response.text}")
        return response.text
    return None

def send_message_to_assistant(thread_id, query, assistant_type):
    """Send a message to OpenAI Assistant within the internal thread."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {"Authorization": f"Bearer {openai.api_key}", "Content-Type": "application/json", "OpenAI-Beta": "assistants=v2"}

    payload = {"role": "user", "content": query}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print("Error sending message:", response.text)
    if assistant_type == "summarizing":
        run_id = create_summarizing_run(thread_id)
    elif assistant_type == "balancing":
        run_id = create_balance_run(thread_id)
    return run_id

def create_summarizing_run(thread_id):
    """Create a run to process the assistant response when generating pros and cons OR user Q & A."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    headers = {"Authorization": f"Bearer {openai.api_key}", "Content-Type": "application/json", "OpenAI-Beta": "assistants=v2"}
    payload = {
        "assistant_id": SUMMARIZING_ASSISTANT_ID
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json().get("id")

def create_balance_run(thread_id):
    """Create a run to process the assistant response when generating balances over time."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    headers = {"Authorization": f"Bearer {openai.api_key}", "Content-Type": "application/json", "OpenAI-Beta": "assistants=v2"}
    payload = {
        "assistant_id": BALANCE_ASSISTANT_ID
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json().get("id")


def get_assistant_verdict(thread_id, run_id):
    """Retrieve the assistant's response from OpenAI."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {"Authorization": f"Bearer {openai.api_key}", "OpenAI-Beta": "assistants=v2"}

    while True:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("Error retrieving messages:", response.text)
            return None

        response_data = response.json()
        for item in response_data.get("data", []):
            if item.get("role") == "assistant" and item.get("run_id") == run_id:
                content = item.get("content", [])
                print("it was found")
                if content:
                    content = content[0]
                    if "text" in content and "value" in content["text"]:
                        response = content["text"]["value"]
                        try:
                            return json.loads(response)  # Convert response to JSON
                        except:
                            continue
        time.sleep(5)

def delete_assistant_thread(thread_id):
    """Deletes an OpenAI Assistant thread"""
    url = f"https://api.openai.com/v1/threads/{thread_id}"
    headers = {"Authorization": f"Bearer {openai.api_key}"}

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        print(f"Thread {thread_id} successfully deleted.")
        return True
    else:
        print(f"Failed to delete thread {thread_id}: {response.text}")
        return False