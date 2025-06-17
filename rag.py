import os
import json
from dotenv import load_dotenv, find_dotenv, set_key
from openai import OpenAI
from chat import ask
from vector_store import get_or_create_vector_store_id

# Load environment variables. Create a .env file if it doesn't exist.
load_dotenv()
dotenv_path = find_dotenv()
if dotenv_path == "":
    with open(".env", "w") as f:
        pass
    dotenv_path = find_dotenv()

client = OpenAI()


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


def load_system_prompt():
    """Loads the system prompt from the markdown file."""
    try:
        with open("cardsense_system_prompt.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Error: `cardsense_system_prompt.md` not found.")
        print("Please make sure the system prompt file is in the same directory.")
        exit(1)


# --- Global Variables ---
vector_store_id = get_or_create_vector_store_id()
system_prompt = load_system_prompt()
# --- End of Global Variables ---


def ask(q, previous_response_id=None):
    """
    Asks a question using the Responses API, maintaining conversation history.
    """
    print("\\nThinking...")
    try:
        # The tool_resources parameter is not supported in all SDK versions.
        # Instead, we pass the vector_store_id directly within the tool definition.
        response = client.responses.create(
            model="gpt-4o-mini",
            instructions=system_prompt,
            tools=[
                {
                    "type": "file_search",
                    "vector_store_ids": [vector_store_id],
                }
            ],
            input=[
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": q}],
                }
            ],
            store=True,
            previous_response_id=previous_response_id,
        )

        if response.output_text:
            return response.output_text, response.id
        else:
            # Fallback for unexpected API response structure
            print(f"Debug - API Response: {response}")
            return "I couldn't process that request. Please try again.", previous_response_id

    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred while processing your request: {e}", previous_response_id


def main():
    """
    Main function to run the CardSense AI chat loop.
    """
    print("\\nStarting CardSense AI...")
    # This call ensures the vector store is set up before we start the chat loop.
    get_or_create_vector_store_id()

    # Store the response ID to maintain conversation context
    previous_response_id = None
    print("\\nWelcome to CardSense AI! Ask me about credit card questions.")
    print("Type 'exit' or 'quit' to end the conversation.")

    while True:
        try:
            question = input("\\nYour question: ")
            if question.lower().strip() in ["exit", "quit"]:
                print("Exiting assistant. Goodbye!")
                break

            if not question.strip():
                continue

            response_text, new_response_id = ask(question, previous_response_id=previous_response_id)
            previous_response_id = new_response_id

            if response_text:
                print(f"\\nAssistant:\\n{response_text}")
            else:
                print("\\nAssistant: I couldn't find an answer to your question. Please try again.")

        except (KeyboardInterrupt, EOFError):
            print("\\nExiting assistant. Goodbye!")
            break


if __name__ == "__main__":
    main()
