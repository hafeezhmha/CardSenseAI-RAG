# CardSense AI

CardSense AI is a smart, trustworthy, and helpful virtual assistant focused exclusively on helping users understand, compare, and make the most of credit cards.

This repository contains the backend API for CardSense AI, built with Python and FastAPI, ready for deployment on Vercel.

## ✨ Features

- **Conversational AI:** Powered by OpenAI's `gpt-4o-mini` for natural and helpful conversations.
- **RAG Architecture:** Uses a Retrieval-Augmented Generation (RAG) system to answer questions based on a provided knowledge base of bank information.
- **Context-Aware:** Maintains conversation history for follow-up questions.
- **Custom Persona:** Guided by a detailed system prompt to act as a professional yet friendly financial assistant.
- **Scalable Backend:** Built with FastAPI and designed for serverless deployment on Vercel.

## 📂 Project Structure

```
.
├── api/
│   └── index.py        # FastAPI application logic for Vercel
├── docs/               # Original JSON data for banks
├── txt_docs/           # Processed .txt files for the knowledge base
├── .env.example        # Example environment variables
├── .gitignore          # Files to ignore in git
├── cardsense_system_prompt.md # The AI's personality and rules
├── chat.py             # Core chat logic
├── config.py           # Configuration (OpenAI client, env vars)
├── json2txt.py         # Script to convert JSON docs to .txt
├── rag.py              # Main script for local command-line testing
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── vector_store.py     # Logic for setting up the OpenAI Vector Store
└── vercel.json         # Vercel deployment configuration
```

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.9+
- An OpenAI API key

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd <repository-name>
```

### 3. Set Up Environment

- Create a virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
  ```
- Install the required packages:
  ```bash
  pip install -r requirements.txt
  ```
- Create a `.env` file from the example and add your OpenAI API key:
  ```bash
  # In the terminal, create the .env file. You can also do this manually.
  # For Linux/macOS:
  cp .env.example .env
  # For Windows:
  copy .env.example .env
  ```
  Now, edit the `.env` file with your secret key:
  ```
  OPENAI_API_KEY="sk-..."
  ```

### 4. Prepare the Knowledge Base

If you have local JSON files in the `docs/` folder, run the `json2txt.py` script to process them into the `txt_docs/` directory:
```bash
python json2txt.py
```
The first time you run the application, it will automatically create and populate a vector store on your OpenAI account. The ID will be saved to your `.env` file for future runs.

## 🛠️ Local Development

### Running the Command-Line Chat

To test the bot's logic directly in your terminal, run `rag.py`. **The first time you run this, it will create a new Vector Store on your OpenAI account and save its ID to your `.env` file.**

```bash
# This command will also perform the one-time setup for the vector store.
python rag.py
```
After running this, your `.env` file will be updated with the `VECTOR_STORE_ID`. You will need this for deployment.

### Running the API Server

To test the FastAPI server locally, use `uvicorn`:
```bash
uvicorn api.index:app --reload
```
The API will be available at `http://127.0.0.1:8000`. You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

## ☁️ Deployment to Vercel

This project is configured for easy deployment to Vercel.

1.  **Get Your Vector Store ID:** Run the application locally one time to perform the initial setup and get your `VECTOR_STORE_ID`.
    ```bash
    python rag.py
    ```
    Copy the `VECTOR_STORE_ID` value from your `.env` file.

2.  **Push to GitHub:** Commit and push all your latest code to a GitHub repository.

3.  **Import to Vercel:** Go to your Vercel dashboard and import the project from GitHub. Vercel will automatically detect the `vercel.json` configuration.

4.  **Add Environment Variables:** In the project settings on Vercel, navigate to the "Environment Variables" section. You **must** add the following two variables:
    - `OPENAI_API_KEY`: Your secret key from OpenAI.
    - `VECTOR_STORE_ID`: The ID you copied from your `.env` file in step 1.

5.  **Deploy:** Click "Deploy". Vercel will build and host your API.

## 🔌 API Endpoint

Once deployed, your Flutter app can interact with the backend using the following endpoint.

- **Endpoint:** `/chat`
- **Method:** `POST`
- **Body (JSON):**
  ```json
  {
    "question": "What is the best card for travel?",
    "previous_response_id": "resp_12345"
  }
  ```
  * `previous_response_id` is optional and used to maintain conversation history.

- **Success Response (JSON):**
  ```json
  {
    "response_text": "The SBI Elite card offers great travel benefits...",
    "response_id": "resp_67890"
  }
  ```

## 📱 Flutter Integration Example

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> getChatResponse(String question, String? previousId) async {
  // Replace with your deployed Vercel URL
  final String apiUrl = 'https://your-project-name.vercel.app/chat';

  try {
    final response = await http.post(
      Uri.parse(apiUrl),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'question': question,
        'previous_response_id': previousId,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      print('Assistant: ${data['response_text']}');
      // Update your UI and store the new response ID: data['response_id']
    } else {
      print('Error: ${response.body}');
    }
  } catch (e) {
    print('Error: Failed to connect to the server.');
  }
}
``` 