# llmunchies/adapter_anthropic.py

import os
from anthropic import Anthropic
from llmunchies.memory import MemoryManager

# Configure the client using the ANTHROPIC_API_KEY environment variable.
try:
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
except TypeError:
    print("ERROR: ANTHROPIC_API_KEY environment variable not found.")
    print("Please set the key to use the Anthropic adapter.")
    client = None

def ask_claude(memory: MemoryManager, model: str = "claude-2.1") -> str:
    """
    A simple adapter to send a MemoryManager's context to the Anthropic API.

    This function relies on the `anthropic` library and an `ANTHROPIC_API_KEY`
    environment variable.

    Args:
        memory (MemoryManager): An instance of MemoryManager with the conversation history.
        model (str): The specific Anthropic model to use.

    Returns:
        str: The text content of the assistant's response.
    """
    if not client:
        return "Anthropic client is not configured. Please set your ANTHROPIC_API_KEY."

    # 1. Use MemoryManager to format the prompt in Claude's style.
    # This is where the magic happens! We just change the model name.
    prompt = memory.format(model="claude")

    # 2. Send the formatted prompt to the Anthropic API.
    try:
        response = client.completions.create(
            model=model,
            max_tokens_to_sample=1024, # This parameter is required by this endpoint
            prompt=prompt,
        )
        # 3. Extract the response text.
        assistant_response = response.completion
        return assistant_response

    except Exception as e:
        print(f"An error occurred with the Anthropic API: {e}")
        return f"Error: Could not get a response from Anthropic. Details: {e}"