# llmunchies/memory.py

import tiktoken
from typing import List, Dict, Union, Literal

# Define a type hint for the role to ensure correctness.
Role = Literal["user", "assistant", "system"]

class MemoryManager:
    """
    A model-agnostic context engine to store, manage, and format conversational history for LLMs.

    LLMunchies is the middleware between your application and the model API. It handles
    prompt formatting and context length management so you can swap models like GPT and Claude
    without rewriting your code.

    V2 adds token-aware context limiting with the .limit_tokens() method.

    Attributes:
        system_prompt (str, optional): The system prompt to guide the model's behavior.
        history (List[Dict[str, str]]): A list of messages, each a dictionary with 'role' and 'content'.
    """

    def __init__(self, system_prompt: str = None):
        """
        Initializes the MemoryManager.

        Args:
            system_prompt (str, optional): A system prompt that sets the context for the
                                           entire conversation. Defaults to None.
        """
        self.system_prompt = system_prompt
        # The history is stored in the universal OpenAI format {'role': ..., 'content': ...}
        # and converted to other formats on the fly.
        self.history: List[Dict[str, str]] = []
        print("🧠 LLMunchies MemoryManager initialized.")

    def add(self, role: Role, content: str):
        """
        Adds a new message to the conversation history.

        Args:
            role (Role): The role of the message sender. Must be 'user' or 'assistant'.
            content (str): The content of the message.
        
        Raises:
            ValueError: If the role is not 'user' or 'assistant'.
        """
        if role not in ["user", "assistant"]:
            raise ValueError("Role must be either 'user' or 'assistant'.")
        
        message = {"role": role, "content": content}
        self.history.append(message)

    def format(self, model: str) -> Union[List[Dict[str, str]], str]:
        """
        Formats the conversation history for a specified model.

        Args:
            model (str): The target model family. Supported: 'gpt', 'openai', 'claude', 'anthropic'.
                         The check is case-insensitive.

        Returns:
            Union[List[Dict[str, str]], str]: The formatted prompt.
                                              - List of dicts for GPT-style models.
                                              - A single string for Claude-style models.

        Raises:
            ValueError: If the specified model format is not supported.
        """
        model_family = model.lower()

        if "gpt" in model_family or "openai" in model_family:
            return self._format_gpt()
        
        if "claude" in model_family or "anthropic" in model_family:
            return self._format_claude()
            
        raise ValueError(f"Unsupported model format: '{model}'. Supported: 'gpt', 'claude'.")

    def _format_gpt(self) -> List[Dict[str, str]]:
        """Formats the history for GPT-style models (OpenAI API standard)."""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        messages.extend(self.history)
        return messages

    def _format_claude(self) -> str:
        """Formats the history for Claude's legacy message block format."""
        prompt_str = ""
        if self.system_prompt:
            prompt_str += f"{self.system_prompt}\n\n"

        for message in self.history:
            role_tag = "Human" if message["role"] == "user" else "Assistant"
            prompt_str += f"{role_tag}: {message['content']}\n\n"
        
        prompt_str += "Assistant:"
        return prompt_str

    def clear(self):
        """Resets the conversation history, but keeps the system prompt."""
        self.history.clear()
        print("🍔 Memory cleared. Ready for a new conversation!")

    def limit(self, n: int):
        """
        Limits the conversation history to the last 'n' interactions.
        An interaction is a user message and its corresponding assistant response.

        Args:
            n (int): The number of user/assistant interaction pairs to keep.
        """
        num_messages_to_keep = n * 2
        if len(self.history) > num_messages_to_keep:
            self.history = self.history[-num_messages_to_keep:]
            
    # --- V2 FEATURE: TOKEN-BASED LIMITING ---

    def _get_tokenizer(self, model: str) -> tiktoken.Encoding:
        """Gets the appropriate tokenizer for a given model."""
        try:
            return tiktoken.encoding_for_model(model)
        except KeyError:
            # If the model is not found, default to a common tokenizer and warn the user.
            print(f"Warning: Model '{model}' not found. Using 'cl100k_base' tokenizer.")
            return tiktoken.get_encoding("cl100k_base")

    def limit_tokens(self, model: str, max_tokens: int):
        """
        Truncates the conversation history to fit within a specified token limit.

        This method preserves the system prompt and the most recent messages, ensuring
        the total token count is less than or equal to `max_tokens`. It works backwards
        from the newest message.

        Args:
            model (str): The model name (e.g., 'gpt-4-turbo') to use for tokenization.
            max_tokens (int): The maximum number of tokens allowed in the context.
        """
        tokenizer = self._get_tokenizer(model)
        
        # Calculate tokens for the system prompt first, as it's always present.
        # Add a small buffer for message structure.
        system_prompt_tokens = 0
        if self.system_prompt:
            system_prompt_tokens = len(tokenizer.encode(self.system_prompt)) + 4

        current_tokens = system_prompt_tokens
        truncated_history = []

        # Iterate through history in reverse (from newest to oldest).
        for message in reversed(self.history):
            # Estimate tokens for the current message. Add ~4 tokens for role/formatting.
            message_content_tokens = len(tokenizer.encode(message['content']))
            message_tokens = message_content_tokens + 4

            if current_tokens + message_tokens > max_tokens:
                # This message would exceed the limit, so we stop here.
                break
            
            # The message fits, add it to our new history and update token count.
            current_tokens += message_tokens
            truncated_history.append(message)
        
        # The new history was built in reverse, so flip it back to chronological order.
        self.history = truncated_history[::-1]


    def __repr__(self) -> str:
        """Provides a developer-friendly representation of the memory state."""
        return (f"MemoryManager(system_prompt='{self.system_prompt}', "
                f"history_length={len(self.history)})")