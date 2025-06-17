from config import client, system_prompt
from vector_store import get_or_create_vector_store_id

vector_store_id = get_or_create_vector_store_id()

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