import os
from dotenv import set_key, load_dotenv
from config import client, dotenv_path

def setup_vector_store():
    """
    Performs one-time setup for the RAG system.
    1. Creates a vector store.
    2. Uploads and polls files from txt_docs to the vector store.
    3. Saves the vector store ID to the .env file for local use.
    """
    print("Performing one-time setup for the vector store...")

    # 1. Create a Vector Store
    print("Creating a new vector store...")
    vector_store = client.beta.vector_stores.create(name="Bank Information")

    # 2. Upload files from txt_docs/
    print("Uploading files to the vector store...")
    txt_docs_path = "txt_docs"
    # Ensure this path is correct for serverless context
    if not os.path.exists(txt_docs_path):
        print(f"Warning: '{txt_docs_path}' directory not found. Skipping file upload.")
        # In a serverless function, files might not be at this relative path.
        # It's better to pre-upload files to the vector store via OpenAI's dashboard
        # or a local script run. For now, we'll allow it to proceed without files.
    else:
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

    # 3. Save Vector Store ID to .env file for local development
    # This part should not run in production.
    print("Saving Vector Store ID to .env file for local use...")
    set_key(dotenv_path, "VECTOR_STORE_ID", vector_store.id)

    print("Setup complete.")
    return vector_store.id


def get_or_create_vector_store_id():
    """
    Returns the vector store ID from environment variables.
    In a deployed (Vercel) environment, it requires the ID to be set.
    In a local environment, it runs the setup process if the ID is not found.
    """
    # Vercel sets the 'VERCEL' environment variable to '1'
    is_production = os.getenv("VERCEL") == "1"
    vector_store_id = os.getenv("VECTOR_STORE_ID")

    if is_production:
        if not vector_store_id:
            # In production, the VECTOR_STORE_ID must be pre-set.
            raise ValueError("VECTOR_STORE_ID environment variable not set in production.")
        print(f"Found production Vector Store ID: {vector_store_id}")
        return vector_store_id
    else:
        # Local development logic
        if not vector_store_id:
            print("Vector Store ID not found. Running local setup...")
            vector_store_id = setup_vector_store()
            # Reload dotenv to get the new variables for the current run
            load_dotenv(override=True)
        else:
            print(f"Found local Vector Store ID: {vector_store_id}")
        
        return vector_store_id 