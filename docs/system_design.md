# System Design: ESP32 Application Idea Generator

## 1. Purpose

We're currently using **LangChain v0.3 and LangGraph** to implement this. LangChain provides a powerful framework for structuring prompt workflows and memory in LLM applications.

Each subtask is implemented as a **graph node** in LangGraph. Nodes are connected in a memory-aware graph that maintains the conversation state across turns. As the user and LLM alternate control, persistant state is needed to carry session context during conditional branching.

## 2. Why ESP32?

ESP32 is a micro-controller board family that is low-cost, energy-efficient (deep sleep mode) with both Wi-Fi (can connect to or create its own network) and Bluetooth capabilities.

It was selected due to its wide protocol support (I2C, SPI, UART), processing power, wireless capability (already integrated, no loss of pins), and multi-threading support.

## 3. Why LangChain?

The decision to use LangChain (vs. Vanilla Python via API calls or other libraries) was driven by the need for a standard interface to interact with different LLMs or tools.

As AI is rapidly growing, with it came a number of various libraries and tools with their own use cases. To provide the developer with an easier experience, Langchain provides a full framework that is coupled with observability, orchestration, and standardized interface for different LLM providers.

### TO-DO:

- [ ] `with_structured_outputs` coupled with the use of `Pydantic` library on the state can help mimic the flow of Pydantic AI.

---

> **NOTE**: I'm considering alternatives like [Pydantic-AI](https://ai.pydantic.dev/), which emphasizes strict schemas and minimal overhead. Based on first impressions, Pydantic-AI seems to be less bloated in features which can better fit simpler user scenarios.

## 4. Why LangGraph?

The decision to use LangGraph (vs. LCEL or LangChain v0.2) is the driven by the need for:

- Conditional control flow between nodes (e.g., user can choose to revise input or move forward)
- A unified state defined from the very start, forcing you to outline how exactly you want your data to look like.
- Persistent memory via the `MemorySaver` + `Checkpointer` which can allow you resume interrupted flows at any point.

### TODO:

- [ ] Reactive event flow via `Command` + `goto` + `update` tools supported by [LangGraph](https://langchain-ai.github.io/langgraph/how-tos/graph-api/).

---

> **NOTE**: This is a small workflow (~5 steps), but LangGraph is being used as per LangChain documentation recommendations. Must see whether its use case is appropriate here.

## 5. Stack Summary

| Layer        | Tool                  | Notes                                                                                      |
| ------------ | --------------------- | ------------------------------------------------------------------------------------------ |
| LLM Provider | Groq                  | Provides several models + API is free and # of requests is sufficient for current use case |
| Framework    | LangChain + LangGraph | LangGraph manages orchestration and memory                                                 |
| Schema       | `TypedDict` for now   | Will consider migrating to `Pydantic` for input/output validation                          |
| Memory       | `MemorySaver`         | Via `checkpointer` on LangGraph                                                            |

## 6. Workflow Nodes (Current Implementation)

### Entry Point: `collect_input_components_protocol`

- **Goal**: Collect initial hardware component list and communication protocol from the user.
- **Prompts used**: `system_prompt`, `first_task_prompt`
- **Output**: Appends the model's evaluation to `state["messages"]`

---

### Node: `manual_review_decision`

- **Goal**: Ask the user whether they wish to manually review validation results.
- **Prompt used**: `manual_review_followup_prompt`
- **Output**: Updates `manual_review_flag: bool`

---

### Node: `validate_input`

- **Goal**: Validate hardware components against selected protocol.
- **Prompt used**: `second_task_prompt`
- **Logic**: May return user suggestions like `modify` or `different protocol`.

---

### Conditional Router: `route_after_validation`

- **Goal**: Decide whether to re-loop or proceed.
- **Rule**: If last message content is `"modify"` or `"different protocol"`, re-loop to `collect_input_components_protocol`.

---

### Node: `collect_input_board_industry`

- **Goal**: Ask for dev board and target industry.
- **Prompt used**: `third_task_prompt`
- **Final Step** (currently): Terminates here

### TODO:

- [ ] Add input/output types or example state snapshots for each node

---

## 7. State Design

```python
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    manual_review_flag: bool
```

### TODO:

- [ ] Migrate to Pydantic models with validation? Currently no input/output contract enforced

## 8. Prompt Strategy

All nodes share a common system_prompt, and receive additional system task-specific prompts:

- first_task_prompt
- manual_review_followup_prompt
- second_task_prompt
- third_task_prompt

### TODO:

- [ ] Evaluate the need for per-node system_prompt injections. If behavior diverges from one node to the other, consider using small variations.

---

## 9. Architectural Alternatives

| Option         | Notes                                                                                          |
| -------------- | ---------------------------------------------------------------------------------------------- |
| LangChain LCEL | good for linear deterministic flows                                                            |
| Vanilla Python | no abstractions --> gives full control, but poor reusability                                   |
| Pydantic-AI    | alternative agentic framework --> has input/output validation, less features but more readable |

### TODO:

- [ ] Create comparison table of LangChain vs. Pydantic-AI vs. LCEL vs. Raw API. Criteria may include: memory control, modularity, schema validation

---

## 10. Workflow Diagram

To be created in docs/workflow.md:

### TODO:

- [x] Show node flow
- [x] Include expected input/output state at each level (think FSM)

---
