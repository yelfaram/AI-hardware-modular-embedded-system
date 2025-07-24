# Project Overview

This project aims to build an **agentic chatbot workflow** that guides users through the process of generating embedded systems application ideas using **ESP32-compatible components**.

The assistant is structured as a memory-aware graph using **LangGraph** and **LangChain v0.3**, with each subtask implemented as an independent node.

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

## Documentation

- Workflow design and node structure: [docs/workflow.md](docs/workflow.md)
- System design decisions: [docs/system_design.md](docs/system_design.md)

## Key Technologies

- LangChain v0.3
- LangGraph
- Groq LLM API
- MemorySaver for persistent in-memory state

# Resources

- [Memory in LangChain](https://www.comet.com/site/blog/memory-in-langchain-a-deep-dive-into-persistent-context/)
- [Build a Chatbot - LangChain v0.3 Documentation](https://python.langchain.com/docs/tutorials/chatbot/)
- [Build a Chatbot - LangChain v0.2 Documentation](https://python.langchain.com/v0.2/docs/tutorials/chatbot/)
- [Prompt Chaining with LangChain - IBM Documentation](https://www.ibm.com/think/tutorials/prompt-chaining-langchain)
- [LangChain + Groq - Groq Documentation](https://console.groq.com/docs/langchain)
- [RunnableWithMessageHistory - LangChain Documentation](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html)
- [LangGraph Memory - Concept](https://langchain-ai.github.io/langgraph/concepts/memory)
- [Could be useful](https://github.com/NirDiamant/agents-towards-production)
