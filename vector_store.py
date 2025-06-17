import os
from dotenv import set_key, load_dotenv
from config import client, dotenv_path

def setup_vector_store():
    """
    Performs one-time setup for the RAG system.
    1. Creates a vector store.
    2. Uploads and polls files from txt_docs to the vector store.
    3. Saves the vector store ID to the .env file.
    """
    print("Performing one-time setup for the vector store...")

    # 1. Create a Vector Store
    print("Creating a new vector store...")
    vector_store = client.beta.vector_stores.create(name="Bank Information")

    # 2. Upload files from txt_docs/
    print("Uploading files to the vector store...")
    txt_docs_path = "txt_docs"
    file_paths = [
        os.path.join(txt_docs_path, f)
        for f in os.listdir(txt_docs_path)
        if f.endswith(".txt")
    ]
    if not file_paths:
        print(f"No .txt files found in '{txt_docs_path}'. Skipping file upload.")
    else:
        file_streams = [open(path, "rb") for path in file_paths]
        try:
            file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id, files=file_streams
            )
            print(f"File batch status: {file_batch.status}")
        finally:
            for stream in file_streams:
                stream.close()

    # 3. Save Vector Store ID to .env file
    print("Saving Vector Store ID to .env file...")
    set_key(dotenv_path, "VECTOR_STORE_ID", vector_store.id)
    # Remove old ASSISTANT_ID if it exists
    set_key(dotenv_path, "ASSISTANT_ID", "")


    print("Setup complete.")
    return vector_store.id


def get_or_create_vector_store_id():
    """
    Returns the vector store ID from environment variables.
    If not found, runs the setup process.
    """
    vector_store_id = os.getenv("VECTOR_STORE_ID")
    if not vector_store_id:
        print("Vector Store ID not found. Running setup...")
        vector_store_id = setup_vector_store()
        # Reload dotenv to get the new variables for the current run
        load_dotenv(override=True)
    else:
        print(f"Found existing Vector Store ID: {vector_store_id}")

    return vector_store_id 