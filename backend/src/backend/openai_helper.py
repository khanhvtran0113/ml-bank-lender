import openai
import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()  # Load API keys from .env file

openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

# Store uploaded file IDs
uploaded_file_id = None

def upload_pdf_to_openai(file):
    """Uploads a PDF file to OpenAI Assistants API and stores the file ID."""
    global uploaded_file_id
    file_stream = file.stream

    file_response = openai.files.create(
        file=("document.pdf", file_stream, "application/pdf"),  # Correct format
        purpose="assistants"
    )

    uploaded_file_id = file_response.id
    return {"message": "File uploaded successfully!", "file_id": uploaded_file_id}

def create_openai_thread():
    """Creates an internal conversation thread with OpenAI Assistant."""
    url = "https://api.openai.com/v1/threads"
    headers = {"Authorization": f"Bearer {openai.api_key}", "Content-Type": "application/json", "OpenAI-Beta": "assistants=v2"}

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()["id"]
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

def send_message_to_assistant(thread_id, query):
    """Send a message to OpenAI Assistant within the internal thread."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {"Authorization": f"Bearer {openai.api_key}", "Content-Type": "application/json", "OpenAI-Beta": "assistants=v2"}

    payload = {"role": "user", "content": query}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print("Error sending message:", response.text)

    create_run(thread_id)

def create_run(thread_id):
    """Create a run to process the assistant response."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    headers = {"Authorization": f"Bearer {openai.api_key}", "Content-Type": "application/json", "OpenAI-Beta": "assistants=v2"}
    payload = {"assistant_id": ASSISTANT_ID}

    requests.post(url, headers=headers, json=payload)


def get_assistant_response(thread_id):
    """Retrieve the assistant's response from OpenAI."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {"Authorization": f"Bearer {openai.api_key}", "OpenAI-Beta": "assistants=v2"}

    while True:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("Error retrieving messages:", response.text)
            return None

        response_data = response.json()

        # Find the assistant's response dynamically
        assistant_response = next(
            (item for item in response_data.get("data", []) if item.get("assistant_id") == ASSISTANT_ID and item.get("content")),
            None
        )

        if assistant_response:
            content = assistant_response["content"][0]  # First content item

            if "text" in content and "value" in content["text"]:
                response = content["text"]["value"]
                return response # Return the response text

        time.sleep(1)