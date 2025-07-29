# llmunchies/adapter_openai.py

import os
from openai import OpenAI
from llmunchies.memory import MemoryManager

# We create a single client instance to be reused.
# It's configured using an environment variable for security.
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except TypeError:
    # This provides a helpful error if the API key is not set.
    print("ERROR: OPENAI_API_KEY environment variable not found.")
    print("Please set the key to use the OpenAI adapter.")
    client = None

def ask_openai(memory: MemoryManager, model: str = "gpt-4-turbo") -> str:
    """
    A simple adapter to send a MemoryManager's context to the OpenAI API.

    This function relies on the `openai` library and an `OPENAI_API_KEY`
    environment variable.

    Args:
        memory (MemoryManager): An instance of MemoryManager containing the conversation history.
        model (str): The specific OpenAI model to use (e.g., "gpt-4", "gpt-3.5-turbo").

    Returns:
        str: The text content of the assistant's response.
             Returns an error message if the API key is not configured.
    """
    if not client:
        return "OpenAI client is not configured. Please set your OPENAI_API_KEY."

    # 1. Use our MemoryManager to format the prompt correctly for GPT.
    messages = memory.format(model="gpt")

    # 2. Send the formatted prompt to the OpenAI API.
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        # 3. Extract the response text.
        assistant_response = response.choices[0].message.content
        return assistant_response
    
    except Exception as e:
        # Handle potential API errors gracefully.
        print(f"An error occurred with the OpenAI API: {e}")
        return f"Error: Could not get a response from OpenAI. Details: {e}"