# 🧠 LLMunchies
*Feeding your model tasty context.*

LLMunchies is a lightweight, model-agnostic context engine for developers. It lets you store conversation history, format it for different models like GPT and Claude, and swap models on the fly without rewriting your prompt logic.

It is **NOT** a chatbot framework or a full AI agent platform. It's the simple, pluggable memory layer that sits between your app and the model API.

## Mission
Let developers format, swap, and manage LLM context without prompt PTSD.

## Installation
Currently, LLMunchies is not on PyPI. To use it, simply place the `llmunchies` folder into your project and import the `MemoryManager`. You will also need `tiktoken` for V2 functionality.

```bash
pip install tiktoken