# Project Overview

This project aims to build an **agentic chatbot workflow** that guides a user through the process of generating embedded systems application ideas using ESP32-compatible components. The chatbot is structured as a series of subtasks, each handled by its own LangGraph node with persistent memory..

We're using **LangChain v0.3 and LangGraph** to implement this. LangChain provides a powerful framework for structuring prompt workflows and memory in LLM applications.

Each subtask is implemented as a **graph node** in LangGraph. Nodes are connected in a memory-aware graph that maintains the conversation state across turns.

## Getting Started

1. Create virtual environment

```
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Set up environment variables. Create a `.env` file in the project root:

```
GROQ_API_KEY=your-groq-api-key
```

4. Run the script

```
python llm_logic.py
```

## Current Objective

Build the foundation of this system by:

- Writing and testing each subtask **individually**
- Using this modular approach to:
  - Make debugging easier
  - Get familiar with LangChain
  - Tweak and improve prompt design based on real model behavior

This is important because different LLMs (e.g. Groq’s `llama-3.1-8b-instant` vs `llama-3.3-70b-versatile`) may produce very different outputs, and chaining only works well if each step’s output is predictable.

### Where We Are

The core system is now:

- Built using LangGraph with memory persistence (`MemorySaver`)
- Running with a multi-node graph: input collection → input validation
- State keys are successfully carried across nodes

## What's Done So Far

- Subtask 1: Input Collection (user provides components + protocol)
- Subtask 2: Input Validation (checks component compatibility)
  - Subtask 2 correctly **tracks memory and state**
  - User can request manual review to revise inputs
- Graph nodes and memory management work as intended

_Note:_ Currently tested in isolation using hardcoded inputs.

## What Still Needs Work

- Add **branching logic** to loop back to input collection if manual review is requested
- Finalize prompt wording to make it less verbose and more LLM-consistent
- Implement remaining subtasks:
  - Application Domain/Industry Input
  - Application idea generation
  - Application validation

## Notes

- The project now uses **LangChain v0.3 and LangGraph.**
- Memory is handled via `MemorySaver` (in-memory checkpointing).
- Session persistence is supported via `thread_id`.
- Branching behavior will allow dynamic control over conversation flow based on user choices.
- Without passing `**state`, the output doesn't generate a response (**look into this**)

## Next Steps

- Add branching logic for manual review loop
- Refine prompts for consistency and LLM clarity
- Implement remaining subtasks (Subtask 3 and beyond)
- Add multi-session support

# Resources

- [Memory in LangChain](https://www.comet.com/site/blog/memory-in-langchain-a-deep-dive-into-persistent-context/)
- [Build a Chatbot - LangChain v0.3 Documentation](https://python.langchain.com/docs/tutorials/chatbot/)
- [Build a Chatbot - LangChain v0.2 Documentation](https://python.langchain.com/v0.2/docs/tutorials/chatbot/)
- [Prompt Chaining with LangChain - IBM Documentation](https://www.ibm.com/think/tutorials/prompt-chaining-langchain)
- [LangChain + Groq - Groq Documentation](https://console.groq.com/docs/langchain)
- [RunnableWithMessageHistory - LangChain Documentation](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html)
- [LangGraph Memory - Concept](https://langchain-ai.github.io/langgraph/concepts/memory)
- [Could be useful](https://github.com/NirDiamant/agents-towards-production)
