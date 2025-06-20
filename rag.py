import os
import time
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI


# Load environment variables without trying to create a .env file
try:
    load_dotenv()
except Exception:
    # Silently continue if .env cannot be loaded
    pass

client = OpenAI()

# --- Assistant & Vector Store Setup ---

def load_system_prompt():
    """Loads the system prompt from the markdown file."""
    try:
        with open("cardsense_system_prompt.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Error: `cardsense_system_prompt.md` not found.")
        return "You are CardSense AI, a helpful assistant for credit card information."

def get_or_create_assistant():
    """
    Retrieves the assistant ID from environment or creates a new assistant if not found.
    """
    assistant_id = os.getenv("ASSISTANT_ID")
    vector_store_id = get_or_create_vector_store()

    if assistant_id:
        print(f"Found existing assistant ID: {assistant_id}")
        # Optional: Update assistant if needed
        # client.beta.assistants.update(assistant_id, tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}})
        return assistant_id

    print("Assistant ID not found. Creating a new assistant...")
    system_prompt = load_system_prompt()
    assistant = client.beta.assistants.create(
        name="CardSense AI",
        instructions=system_prompt,
        model="gpt-4o-mini",
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )
    assistant_id = assistant.id
    print(f"New assistant created with ID: {assistant_id}")
    return assistant_id

def get_or_create_vector_store():
    """
    Retrieves the vector store ID from environment or creates a new one if not found.
    """
    vector_store_id = os.getenv("VECTOR_STORE_ID")
    if vector_store_id:
        print(f"Found existing vector store ID: {vector_store_id}")
        return vector_store_id

    print("Vector Store ID not found. Creating a new vector store...")
    vector_store = client.vector_stores.create(name="CardSense Knowledge Base")
    
    # Upload files
    txt_docs_path = "txt_docs"
    try:
        file_paths = [os.path.join(txt_docs_path, f) for f in os.listdir(txt_docs_path) if f.endswith(".txt")]
        if file_paths:
            file_streams = [open(path, "rb") for path in file_paths]
            client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id, files=file_streams
            )
            for stream in file_streams:
                stream.close()
            print(f"Uploaded {len(file_paths)} files to vector store.")
        else:
            print("No .txt files found in 'txt_docs' to upload.")
    except Exception as e:
        print(f"Error during file upload: {e}")

    vector_store_id = vector_store.id
    print(f"New vector store created with ID: {vector_store_id}")
    return vector_store_id

# --- Chat Functionality ---

def ask(q, user_context=None, previous_response_id=None):
    """
    Asks a question using the Responses API, maintaining conversation history.
    """
    vector_store_id = get_or_create_vector_store()
    system_prompt = load_system_prompt()

    # Combine user question with their context
    if user_context:
        q = f"User Context:\n{user_context}\n\nQuestion:\n{q}"

    print("\nThinking...")
    try:
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


# --- Main Application ---

def main():
    """Main chat loop for CardSense AI."""
    print("\nInitializing CardSense AI...")
    # This call ensures the vector store and assistant are set up before the chat.
    get_or_create_assistant()
    
    print("\nWelcome to CardSense AI! Ask me about your credit cards.")
    print("Type 'exit' or 'quit' to end the conversation.")
    
    previous_response_id = None
    while True:
        try:
            question = input("\nYour question: ")
            if question.lower().strip() in ["exit", "quit"]:
                print("Exiting assistant. Goodbye!")
                break
            if not question.strip():
                continue

            # For local testing, we don't have user_context
            response_text, new_response_id = ask(question, previous_response_id=previous_response_id)
            previous_response_id = new_response_id

            if response_text:
                print(f"\nAssistant:\n{response_text}")
            else:
                 print("\nAssistant: I couldn't find an answer. Please try again.")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting assistant. Goodbye!")
            break

def reset_and_recreate():
    """Resets the environment by clearing IDs and recreating the assistant and vector store."""
    print("This function is not available in production environments.")
    print("Recreating assistant and vector store...")
    get_or_create_assistant() # This will trigger the creation logic
    print("Reset complete. You can now run the chat.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the CardSense AI chat assistant.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset and recreate the assistant and vector store.",
    )
    args = parser.parse_args()

    if args.reset:
        reset_and_recreate()
    else:
        main()
