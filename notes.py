# -----------------------------
# v0.3 stuff
# -----------------------------
# model = init_chat_model(GROQ_MODEL, model_provider="groq", temperature=0.3) # <= new way of instantiating model ***

# TESTING FOR MEMORY
# print(llm.invoke([("user", "Hi! I'm Bob")]))
# print("--------"*10)
# print(llm.invoke([("user", "What's my name?")]))
# print("--------"*10)
# print(llm.invoke(
#     [
#         ("user", "Hi! I'm Bob"),
#         ("ai", "Hello Bob! How can I assist you today?"),
#         ("user", "What's my name?"),
#     ]
# ))
# print("--------"*10)
# print('\n')

# PERSISTANCE WITH LANGGRAPH
# workflow = StateGraph(state_schema=MessagesState)   # define a graph

# def call_model(state: MessagesState):               # Define the function that calls the model
#     response = model.invoke(state["messages"])
#     return {"messages": response}

# workflow.add_edge(START, "model")                   # Define the (single) node in the graph
# workflow.add_node("model", call_model)

# memory = MemorySaver()                              # Add memory (in-memory checkpointer)
# app = workflow.compile(checkpointer=memory)

# config = {"configurable": {"thread_id": "abc123"}}  # enables multiple conversation threads

# # EXAMPLE W/ PERSISTANCE
# input_messages = [("user", "Hi! I'm Bob.")]         
# output = app.invoke({"messages": input_messages}, config)
# print(output["messages"][-1])                       # output contains all messages in state

# input_messages = [("user", "What's my name?")]
# output = app.invoke({"messages": input_messages}, config)   # since we invoke to the same thread, conversation continues
# print(output["messages"][-1])
# print("--------"*10)
# print('\n')

# ------------------------------------------
# Chain 1: Input Collection
# ------------------------------------------
# input_collection_parser = JsonOutputParser(pydantic_object={
#     "type": "object",
#     "properties": {
#         "component_list": {
#             "type": "array",
#             "items": {"type": "string"}
#         },
#         "protocol": {"type": "string"}
#     }
# })

# input_collection_chain = (
#     input_collection_prompt 
#     | llm 
#     | input_collection_parser
# )

# def collect_user_input(user_input: str) -> dict:
#     """Run Chain 1: component collection from user."""
#     try:
#         result = input_collection_chain.invoke({"input": user_input})
#         print(json.dumps(result, indent=2))
#     except (OutputParserException, ValueError) as e:
#         print(e)

# # Example test run for Chain 1
# user_input = """#### bme280, mpu6050 i2c ####""" # feel free to modify this (can see differences when protocol missing or less than 2 components given)
# collect_user_input(user_input)

# ------------------------------------------
# Chain 2: Input Validation
# ------------------------------------------
# Checks if the components are compatible with the given protocol.
# Adds memory support to handle user corrections or manual review.

# input_validation_prompt = ChatPromptTemplate.from_messages([
#     ("system", system_prompt),
#     ("system", second_task_prompt),
#     ("placeholder", "{conversation}"),                          # memory placeholder
#     ("user", "{input}"),
#     ("user", "Manual review requested? {manual_review_flag}")
# ])

# input_validation_parser = JsonOutputParser(pydantic_object={
#     "type": "object",
#     "properties": {
#         "component_list": {
#             "type": "array",
#             "items": {"type": "string"}
#         },
#         "protocol": {"type": "string"},
#         "incompatible_components_detected": {"type": "bool"},
#         "csv_report": {"type": "string"}
#     },
#     "required": ["component_list", "protocol"]
# })

# input_validation_chain = (
#     input_validation_prompt
#     | llm 
#     | input_validation_parser
# )
# 
# --------------------------------
# Session-Aware Memory for Chain 2
# --------------------------------
# Simple in-memory message store to simulate session-based conversation state. (copied directly from LangChain docs)
# def validate_user_input(user_input: str, review_flag: bool = False) -> dict:
#     """Run Chain 2: component compatibility check + memory."""
#     try:
#         result = input_validation_chain_with_history.invoke(
#             {"input": user_input, "manual_review_flag": review_flag},
#             config={"configurable": {"session_id": "foo"}}
#         )
#         print(result)
#     except (OutputParserException, ValueError) as e:
#         print(e)

# print("--------"*10)

# # Example test run for Chain 2
# user_input = {          # feel free to modify this (try including lm393 - a microphone)
#   "component_list": [
#     "bme280",
#     "lcd1602"
#   ],
#   "protocol": "i2c"
# }
# validate_user_input(user_input)

# ------------------------------------------
# Example Run (OLD)
# ------------------------------------------

# config             = {"configurable": {"thread_id": "abc123"}}
# first_query        = "#### bme280, mpu6050, lcd1602 #### #### i2c ####"   # try lm393 (should say not compatible)
# manual_review_flag = True

# First input: component collection
# input_messages = [HumanMessage(first_query)]
# output = app.invoke(
#     {"messages": input_messages, "manual_review_flag": manual_review_flag},
#     config
# )
# print("OUTPUT: ", output["messages"][-2].content)
# print("\n")
# print("OUTPUT: ", output["messages"][-1].content)

#   - app needs to be invoked only once. since its a graph it will flow through all nodes dictate by the edges until it reaches end
#   - so no need to receive a second input telling to validate

# Second input: validation step
# input_messages = [HumanMessage(second_query)]
# output = app.invoke(
#     {"messages": input_messages, "manual_review_flag": manual_review_flag},
#     config
# )
# print(output["messages"][-1].content)