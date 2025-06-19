# Project Overview

This project aims to build an **agentic chatbot workflow** that guides a user through the process of generating
embedded systems application ideas using ESP32-compatible components. The chatbot is structured as a series of subtasks, each handled by its own prompt and LangChain chain.

We're using **LangChain** (v0.2 and v0.3 syntax) to implement this. LangChain is a popular framework
that helps structure prompt workflows and memory in LLM apps.

Each subtask is implemented as a **separate chain**. Once all subtasks are working correctly, we'll connect them
using LangChain’s `SequentialChain` to form a complete end-to-end pipeline.

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

## What's Done So Far

- Subtask 1: Input Collection (gets user components + protocol)
- Subtask 2: Input Validation (checks compatibility of components with the selected protocol)
  - Subtask 2 includes support for memory
  - User can request manual review and revise their input

_NOTE_: Subtasks are currently tested in isolation with hardcoded inputs

## What Still Needs Work

- Subtask 1 and 2 are not yet connected into a sequential chain
- Prompts for both tasks still need refinement (less verbose, more LLM-consistent formatting)
- Subtasks 3–6 still need to be implemented (e.g. board/application domain, application idea generation, application validation)
- Final `SequentialChain` wiring will happen after all chains are working and returning expected outputs

## Notes

- We're using both **LangChain v0.2 style** (LLMChain, SequentialChain) and newer **v0.3 LCEL** (Runnable-style syntax)
- Memory is currently managed using `RunnableWithMessageHistory` with a custom `store` object for session tracking
  - This works well for testing
  - But LangChain recommends **LangGraph** for managing memory over multiple turns in real chatbots
- Subtask 2 is where memory becomes important — it supports a loop where the user may edit their inputs after
  seeing validation results. Eventually, this should loop back to Subtask 1 in the full flow.

## Next Steps

- Finalize prompts for Subtask 1 and 2 to improve clarity + JSON consistency
- Implement Subtask 3 and so on

# Resources

- [Memory in LangChain](www.comet.com/site/blog/memory-in-langchain-a-deep-dive-into-persistent-context/)
- [Build a Chatbot - LangChain v0.3 Documentation](https://python.langchain.com/docs/tutorials/chatbot/)
- [Build a Chatbot - LangChain v0.2 Documentation](https://python.langchain.com/v0.2/docs/tutorials/chatbot/)
- [Prompt Chaining with LangChain - IBM Documentation](https://www.ibm.com/think/tutorials/prompt-chaining-langchain)
- [LangChain + Groq - Groq Documentation](https://console.groq.com/docs/langchain)
- [RunnableWithMessageHistory - LangChain Documentation](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html)
- [LangGraph Memory - Concept](https://langchain-ai.github.io/langgraph/concepts/memory)
