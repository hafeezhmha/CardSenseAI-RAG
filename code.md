# RAG System with Assistants API

This document explains the implementation of the RAG (Retrieval-Augmented Generation) system in `rag.py`.

## `rag.py`

The `rag.py` script is designed to answer questions based on a collection of text files using OpenAI's Assistants API.

### How it Works

1.  **Initialization**:
    *   It loads environment variables from a `.env` file. If the file doesn't exist, it creates one.
    *   It initializes the OpenAI client.

2.  **Assistant Setup (`get_or_create_assistant_id` and `setup_assistant`)**:
    *   On the first run, the script checks if an `ASSISTANT_ID` is present in the `.env` file.
    *   If not found, it triggers a one-time setup process:
        1.  **Vector Store Creation**: A new vector store is created to hold the file embeddings for efficient searching.
        2.  **File Upload**: All `.txt` files from the `txt_docs/` directory are uploaded to OpenAI.
        3.  **File Batching**: The uploaded files are added to the vector store. The script polls until the files are processed.
        4.  **Assistant Creation**: A new Assistant is created with the `file_search` tool enabled and linked to the vector store.
        5.  **Saving IDs**: The IDs of the new Assistant and Vector Store are saved into the `.env` file to avoid re-running the setup process on subsequent executions.
    *   If an `ASSISTANT_ID` is found, it skips the setup and uses the existing assistant.

3.  **Asking Questions (`ask` function)**:
    *   This function takes a user's question (`q`) and an optional `thread_id`.
    *   It creates a new conversation `Thread` if one doesn't exist.
    *   It adds the user's question as a `Message` to the thread.
    *   It creates a `Run` to process the thread with the Assistant. The `create_and_poll` method waits for the run to complete.
    *   Once the run is complete, it retrieves the messages from the thread.
    *   It finds the latest message from the assistant and returns its content.

4.  **Main Execution Block**:
    *   The `if __name__ == "__main__":` block demonstrates how to use the system.
    *   It calls `get_or_create_assistant_id()` to ensure the assistant is ready.
    *   It defines a sample question and calls the `ask` function.
    *   Finally, it prints the assistant's response to the console.

This setup ensures that the expensive operations (file uploading and assistant creation) are only performed once, making subsequent interactions fast and efficient. 