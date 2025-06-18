"""
AI Agent Workflow - ESP32 Application Idea Generator

This script implements the first two subtasks of a LangChain-based agent workflow:
1. Input Collection
2. Input Validation (with memory for back-and-forth dialog)

Each subtask is modular and designed for independent testing. Prompts are kept separate from code for clarity. 
We're using LangChain's Runnable interface (v0.3 style) along with `RunnableWithMessageHistory` to enable 
conversation memory across turns.

"""

import os
import json
from dotenv import load_dotenv

from langchain_groq import ChatGroq                                     # Groq-backed LLM
from langchain.prompts import ChatPromptTemplate                        # Supports multi-message prompt formatting
from langchain_core.output_parsers import JsonOutputParser              # Extracts structured output from LLM
from langchain_core.exceptions import OutputParserException             # Catch invalid model output

from langchain_core.chat_history import BaseChatMessageHistory          # Interface for memory objects 
from langchain_core.runnables.history import RunnableWithMessageHistory # Adds memory to LCEL pipelines
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from langchain.chains.sequential import SequentialChain                 # chain where the output of one chain is fed as input to the other

from prompts import (
    system_prompt, 
    first_task_prompt, 
    second_task_prompt
)

load_dotenv()

# -----------------------------
# Configuration
# -----------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")                                # Replace with Groq key
GROQ_MODELS  = {
    "fast": "llama-3.1-8b-instant",
    "balanced": "deepseek-r1-distill-llama-70b",
    "powerful": "llama-3.3-70b-versatile"
}
GROQ_MODEL   = GROQ_MODELS["powerful"]      

# Initialize Groq LLM
llm = ChatGroq(
    model_name=GROQ_MODEL,
    temperature=0.3,
)

# ------------------------------------------
# Chain 1: Input Collection
# ------------------------------------------
# Collects initial input from user: hardware components and preferred protocol
input_collection_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("system", first_task_prompt),
    ("user", "{input}")
])

input_collection_parser = JsonOutputParser(pydantic_object={
    "type": "object",
    "properties": {
        "component_list": {
            "type": "array",
            "items": {"type": "string"}
        },
        "protocol": {"type": "string"}
    }
})

input_collection_chain = (
    input_collection_prompt 
    | llm 
    | input_collection_parser
)

def collect_user_input(user_input: str) -> dict:
    """Run Chain 1: component collection from user."""
    try:
        result = input_collection_chain.invoke({"input": user_input})
        print(json.dumps(result, indent=2))
    except (OutputParserException, ValueError) as e:
        print(e)

# Example test run for Chain 1
user_input = """#### bme280, mpu6050 i2c ####""" # feel free to modify this (can see differences when protocol missing or less than 2 components given)
collect_user_input(user_input)

# ------------------------------------------
# Chain 2: Input Validation
# ------------------------------------------
# Checks if the components are compatible with the given protocol.
# Adds memory support to handle user corrections or manual review.

input_validation_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("system", second_task_prompt),
    ("placeholder", "{conversation}"),                          # memory placeholder
    ("user", "{input}"),
    ("user", "Manual review requested? {manual_review_flag}")
])

input_validation_parser = JsonOutputParser(pydantic_object={
    "type": "object",
    "properties": {
        "component_list": {
            "type": "array",
            "items": {"type": "string"}
        },
        "protocol": {"type": "string"},
        "incompatible_components_detected": {"type": "bool"},
        "csv_report": {"type": "string"}
    },
    "required": ["component_list", "protocol"]
})

input_validation_chain = (
    input_validation_prompt
    | llm 
    | input_validation_parser
)

# -----------------------------
# Session-Aware Memory for Chain 2
# -----------------------------
# Simple in-memory message store to simulate session-based conversation state. (copied directly from LangChain docs)
class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: list[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

# Here we use a global variable to store the chat message history.
# This will make it easier to inspect it to see the underlying results.
store = {}

def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]

# Wrap the chain to support message history (**should update this to v0.3)
input_validation_chain_with_history = RunnableWithMessageHistory(
    input_validation_chain,
    get_session_history=get_by_session_id,
    input_messages_key="input",
    history_messages_key="conversation"
)

def validate_user_input(user_input: str, review_flag: bool = False) -> dict:
    """Run Chain 2: component compatibility check + memory."""
    try:
        result = input_validation_chain_with_history.invoke(
            {"input": user_input, "manual_review_flag": review_flag},
            config={"configurable": {"session_id": "foo"}}
        )
        print(result)
    except (OutputParserException, ValueError) as e:
        print(e)

print("--------"*10)

# Example test run for Chain 2
user_input = {          # feel free to modify this (try including lm393 - a microphone)
  "component_list": [
    "bme280",
    "lcd1602"
  ],
  "protocol": "i2c"
}
validate_user_input(user_input)

print("--------"*10)
print(store)

# note: chain 2 would probably have to go back to chain 1 if component or protocol is modified