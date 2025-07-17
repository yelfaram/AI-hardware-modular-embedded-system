"""
AI Agent Workflow - ESP32 Application Idea Generator

This script implements the first two subtasks of a LangGraph-based agent workflow:
1. Input Collection
2. Input Validation (with memory for back-and-forth dialog)

Each subtask is modular and designed for independent testing. Prompts are kept separate from code for clarity. 
We're using LangChain's Runnable interface (v0.3) with LangGraph for persistent memory and state tracking.
"""

"""
TO DO:
"""
import os
from dotenv import load_dotenv

import json 

from langchain.chat_models import init_chat_model

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages

from typing import Sequence
from typing_extensions import Annotated, TypedDict
from pydantic import BaseModel, Field

from prompts import (
    system_prompt, 
    first_task_prompt, 
    manual_review_followup_prompt,
    second_task_prompt
)

# ------------------------------------------
# Environment Setup
# ------------------------------------------

# Load environment variables from .env file
load_dotenv()

# Set Groq API key
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# ------------------------------------------
# Configuration
# ------------------------------------------

# some supported Groq models
GROQ_MODELS  = {
    "fast": "llama3-8b-8192",
    "balanced": "deepseek-r1-distill-llama-70b",
    "powerful": "llama-3.3-70b-versatile"
}

# Choose the model to use
GROQ_MODEL   = GROQ_MODELS["powerful"]      

# Initialize Groq LLM
model = init_chat_model(GROQ_MODEL, model_provider="groq", temperature=0.3)

# ------------------------------------------
# State Definition
#   - track application parameters (a way to keep track of information)
#   - shared data structure (passed along edges between nodes)
#       - output of one node to the next can be taken as input
#
# Schema Definition
#   - structure of the state
#   - can be TypedDict or Pydantic
# ------------------------------------------
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages] # add_messages(format='langchain-openai')
    manual_review_flag: bool
    go_back_to_input_collection: bool

# ------------------------------------------
# Node 1: Input Collection
#   - Asks user for hardware components + protocol
# ------------------------------------------
def collect_input(state: State):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("system", first_task_prompt),
        MessagesPlaceholder(variable_name="messages")       # Injects conversation history
    ]).invoke(state)                                        # Need invoke(state) to return formatted messages

    response = model.invoke(prompt)

    # Append LLM response to conversation history
    return {**state, "messages": state["messages"] + [response]} 

# ------------------------------------------
# Node 2: Manual Review Decision
#   - Asks user if they want to review component validation
#   - Model should return JSON: { "manual_review_flag": true/false }
# ------------------------------------------
def manual_review_decision(state: State):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("system", manual_review_followup_prompt),
        MessagesPlaceholder(variable_name="messages")
    ]).invoke(state)

    response = model.invoke(prompt)
    content = response.content.strip()

    try:
        parsed = json.loads(content)
        manual_review = parsed.get("manual_review_flag", False)
    except json.JSONDecodeError:
        manual_review = False

    # Append LLM response and manual review flag
    return {**state, "messages": state["messages"] + [response], "manual_review_flag": manual_review}

# ------------------------------------------
# Node 3: Input Validation
#   - Checks component compatibility with protocol
#   - If any component fails, this node also prompts next user decision
# ------------------------------------------

def validate_input(state: State):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("system", second_task_prompt),
        MessagesPlaceholder(variable_name="messages")
    ]).invoke(state)

    response = model.invoke(prompt)

    # Append LLM response to conversation history
    return {**state, "messages": state["messages"] + [response]} 

# ------------------------------------------
# Router Function: Conditional Edge Logic
#   - Determines where to go after validation
#   - If user said "modify" or "different protocol", go back to collect_input
# ------------------------------------------

def route_after_validation(state: State):
    last_msg = state["messages"][-1].content.lower()
    return last_msg in ["modify", "different protocol"]

# ------------------------------------------
# Connect Graph Nodes
#
# Node Definition
#   - perform the actual work (execute logic; e.g. llm calls)
#
# Edge Definition
#   - define what happens next (flow of state)
# ------------------------------------------

# Define a new graph
workflow = StateGraph(state_schema=State)       

# add nodes to the graph
workflow.add_node("collect_input", collect_input)
workflow.add_node("manual_review_decision", manual_review_decision)
workflow.add_node("validate_input", validate_input)

# add edges to the graph
workflow.set_entry_point("collect_input")
workflow.add_edge("collect_input", "manual_review_decision")
workflow.add_edge("manual_review_decision", "validate_input")

# add conditional edge
workflow.add_conditional_edges("validate_input", route_after_validation, path_map={
    True: "collect_input",  # Re-loop to collect_input if user wants to modify/different protocol
    False: END              # Otherwise, finish workflow
})

# add remaining edges

# add memory and compile the graph
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# ------------------------------------------
# Example Run (Simulates Full Workflow)
# ------------------------------------------

config = {"configurable": {"thread_id": "abc123"}}

# Simulated user inputs:
# - 3 hardware components (1 incompatible)
# - says yes to manual review
# - says modify (should re-loop or ask user for guidance)
# input_messages = [
#     HumanMessage(content="#### bme280, mpu6050, lm393 #### #### i2c ####"),
#     HumanMessage(content="yes"),                                                
#     HumanMessage(content="modify")                                                    
# ]

# Simulated user inputs:
# - 3 hardware components (all compatible)
# - says no to manual review
# - leaves next prompt empty (workflow should END)
input_messages = [
    HumanMessage(content="#### bme280, mpu6050, lcd1602 #### #### i2c ####"),
    HumanMessage(content="no"),                               
    HumanMessage(content="")        
]

initial = {
    "messages": input_messages,
    "manual_review_flag": False,
    "go_back_to_input_collection": False
}

output = app.invoke(input=initial, config=config)

print("\n--- FINAL OUTPUT MESSAGES ---")
for msg in output["messages"]:
    print(f"{msg.type.upper()}: {msg.content}")