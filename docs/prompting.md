# Prompting

This document is a reference for understanding prompt engineering and best practices.

Prompting is our preferred method over fine-tuning due to:

- Lower resource cost
- Rapid iteration and flexibility
- Ease of debugging and adjustment mid-development

---

## 1. Prompting Foundations (via [Learn Prompting](#appendix))

### What is a Prompt?

A _prompt_ is the input or instruction given to an AI model to produce a response. _Prompting_ is the method of crafting that input to guide the model toward a useful output.

### What is AI?

_AI_ refers to the ability of machines or systems to perform tasks that normally require human intelligence like image recognition, translation, or speech understanding.

### How Does AI Work?

Most modern AI is based on **machine learning**:

- Exposes models to large datasets that are then analyzed by an algorithm
- Algorithm identifies patterns that are then learned and used to make predictions

**Deep learning** (a subset) uses multi-layer neural networks:

- Layers break data into abstract features
- Each layer refines the signal further, enabling complex behavior (transformation)

### How Does AI Learn?

1. **Data Collection**
   <br> Raw data is gathered
2. **Model Training**
   <br> Data is fed through an algorithm to learn patterns
3. **Evaluation/Tuning**
   <br> Performance is tested and adjusted
4. **Inference**
   <br> The trained model makes predictions on new inputs

### What is Generative AI?

_Generative AI_ creates new content (text, images, code) using what it learned from its training data. It’s based on deep learning and sequence prediction.

### Foundation of LLMs

- **Context Length**: Max number of tokens a model can handle at once. This directly affects memory limits and quality of multi-turn interactions.
- **Tokens**: Text is broken down into tokens (chunks of characters or words). These are the model’s base unit of reasoning.

> NOTE: [Context Rot](#appendix) warns that longer context windows may not always yield proportional improvements.
> See also [OpenAI's Hallucination issues](#appendix).

### LLMs vs Chatbots

- **LLMs** process one input at a time with no memory or context by default
- **Chatbots** use memory and tooling to simulate human-like conversation

### Prompt Priming (Context)

_Priming_ means structuring the first prompt to set tone, style, or constraints.

- Assign a role to the model (via system)
- Define format or expected behavior
- Useful for safety, tone, and structure (e.g., educational bots, moderation)

---

## 2. Why Prompt Engineering?

A well-structured prompt leads to more accurate and efficient outputs. Since LLMs are predictive systems, clarity and specificity in prompts are essential. Prompt engineering gives you:

- Greater control over output
- Reduced reliance on post-processing
- Stronger guarantees around format and structure
- Less risk of misinterpretation, especially with complex tasks

---

## 3. Prompt Design Principles (via [Anthropic](#appendix))

### Be Clear and Direct

Always tell the model:

- **What the task is**
- **Why it matters** (context, audience, workflow stage)
- **How you want it done** (format, tone, constraints)

**Recommended format:**

```txt
Your task is to {...}

Instructions:
1. ...
2. ...
3. ...

Here's the data:
{{ ... }}

Expected structure:
1. Field A: ...
2. Field B: ...
```

Avoid large paragraphs. Use bullet points or numbered lists as they are easier for LLMs to follow.

### Use Examples (One-Shot, Few-Shot)

Examples improve structure, reduce ambiguity, and help with formatting, especially for complex or structured outputs.

Why:

- Avoids misinterpretation
- Enforces consistency
- Reduces token usage due to fewer retries

How:

- Show 1–3 real examples
- Cover edge cases
- Wrap them in `<example>` tags for clarity and parsing:

```xml
<examples>
  <example>
    Input: ...
    Output: ...
  </example>
</examples>
```

### Let the LLM think (Chain-Of-Thought)

Best used for tasks a human would need to think through. This helps reduce errors, improves clarity, and can also assist with debugging.

How:

- Add `"think step-by-step"` or similar instructions
- Ask it to `"outline its thinking first"`, then provide the final answer (helps reduce latency and guide its steps)

> NOTE: During prompt refinement, this technique can help expose weak points in the model’s logic before optimizing for output quality. Be mindful of performance cost (latency and token usage).

### Use XML Tags / Delimiters

For separating sections of your prompt or structuring input/output.

Tags help:

- Structure your prompt parts clearly and cleanly
- Prevent prompt injection
- Improve parseability

```xml
<context>
  <doc>...</doc>
  <doc>...</doc>
</context>

<query>What does doc 2 imply about X?</query>
```

### Assign a Role (System Prompt)

Setting a role improves focus, tone, and behavior.

Why:

- Helps the LLM behave like a specialist (e.g., lawyer, engineer)
- Makes outputs more realistic and aligned with expectations

How:

- Use `system` message for setting identity and tone
- Use `user` messages for specific instructions or data

```txt
System: You are a robotics instructor helping beginners choose components.
User: List 3 component kits suitable for building an obstacle-avoiding robot.
```

### Prefill Output Format

Guide model behavior by pre-seeding partial output.

Example:

```txt
User: Give me the system status in JSON format.
Assistant: {
```

Placed as an `assistant` message to enforce JSON formatting from the start.

### Chain Complex Prompts (Prompt Chaining)

Break your process into smaller, focused steps. Each prompt handles one sub-task, reducing complexity and making LLM behavior more predictable.

Why:

- Better focus per task
- More granular control over responses
- Easier debugging

How:

- Design sequential steps with clear handoffs (use XML or JSON when needed)
- Each step’s output feeds into the next

Examples:

- Content: Research &rarr; Outline &rarr; Draft &rarr; Edit
- Data: Extract &rarr; Transform &rarr; Analyze &rarr; Visualize
- Decision: List &rarr; Analyze &rarr; Recommend
- Verification: Generate &rarr; Review &rarr; Refine

### Long Context Tips

For prompts with long documents or multi-section input:

- Place the long content first, above your instructions and examples.
- Structure inputs as `<doc>...</doc>` entries
- Ask the model to quote relevant sections before acting on long inputs

---

## 4. Prompt Design Principles (via [Google](#appendix))

---

## 5. Prompt Chaining

Our main architecture style. We break the user experience into modular subprompts. Each subtask is isolated, debuggable, and easier to evaluate.

Research: [Prompt Chaining Paper](https://arxiv.org/pdf/2406.00507)

## 6. Limitations of LLMs

1. **Hallucination**
   <br>LLMs may generate incorrect information that sounds confident. This is likely a side effect of prediction-based generation and context window limits.
2. **Outdated Knowledge**
   <br>LLMs can’t access recent data unless integrated with tools like retrieval APIs or live documentation.
3. **Weak Reasoning**
   <br>Even simple math or counting tasks (like “how many R’s in ‘strawberry’”) can fail due to token-based processing.
4. **Bias**
   <br>Models reflect the biases in their training data. Fair, representative datasets and additional safety layers are required.
5. **Jailbreakable**
   <br>LLMs can be manipulated into producing harmful or unintended content. Prompt engineering must account for attack vectors and edge cases.

---

## 7. Appendix

- [Anthropic Prompt Engineering](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Gemeni Prompting Guide 101](https://services.google.com/fh/files/misc/gemini-for-google-workspace-prompting-guide-101.pdf)
- [Learn Prompting](https://learnprompting.org/docs/basics/introduction)
- [Context Rot Research](https://research.trychroma.com/context-rot)
- [OpenAI Reasoning Regression](https://techcrunch.com/2025/04/18/openais-new-reasoning-ai-models-hallucinate-more/)

## TODOs

- [ ] Add examples from own prompts
- [ ] Provide clearer examples on quoting in long context
- [ ] Add Google guide
