import openai
import os
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