# LLM Prompt & Tool Documentation for Academic Reproducibility

## Purpose

This document provides a complete, verbatim record of every prompt, tool schema, and API configuration used by the LLM bot player in the experiment. It is intended for inclusion in a paper's methods section or supplementary materials, enabling exact replication of the AI agent's behavior.

## Source Files

| File | Role |
|------|------|
| `_shared/llm_backend.py` | All prompt strings, tool schemas, API configuration, retry logic, parsing, tracing |
| `_shared/utils.py` | `PARAMS_PAYOFFS` dictionary (payoff amounts per game) |
| `_shared/llm_job_pool.py` | Thread pool architecture for async API calls |
| `docs/v5-llm-PD-withComm.py` | Historical v5 implementation for evolution comparison |

## Table of Contents

- [Section 1: Experimental Design Context](#section-1-experimental-design-context)
- [Section 2: System Prompt (Developer Message)](#section-2-system-prompt-developer-message)
- [Section 3: Game Description Prompt](#section-3-game-description-prompt)
- [Section 4: Communication Preamble](#section-4-communication-preamble)
- [Section 5: User Prompts (3 Variants)](#section-5-user-prompts-3-variants)
- [Section 6: Tool Definitions (JSON Schemas)](#section-6-tool-definitions-json-schemas)
- [Section 7: API Configuration Parameters](#section-7-api-configuration-parameters)
- [Section 8: Prompt Assembly Flow by Condition](#section-8-prompt-assembly-flow-by-condition)
- [Section 9: Response Parsing and Validation](#section-9-response-parsing-and-validation)
- [Section 10: Retry Logic and Error Handling](#section-10-retry-logic-and-error-handling)
- [Section 11: Tracing and Logging](#section-11-tracing-and-logging)
- [Section 12: Thread Pool and Async Execution](#section-12-thread-pool-and-async-execution)
- [Section 13: Evolution from v5 to Current Implementation](#section-13-evolution-from-v5-to-current-implementation)
- [Section 14: Reproducibility Checklist](#section-14-reproducibility-checklist)

---

## Section 1: Experimental Design Context

### Treatment Conditions

| Code | Label | Pair Type | Communication | LLM Involved |
|------|-------|-----------|---------------|---------------|
| `condition_1` (C1) | H-H no comm | Human vs Human | No | No |
| `condition_2` (C2) | H-H comm | Human vs Human | Yes | No |
| `condition_3` (C3) | H-AI no comm | Human vs AI | No | **Yes** |
| `condition_4` (C4) | H-AI comm | Human vs AI | Yes | **Yes** |

The LLM acts as a bot player in conditions C3 and C4 only. In C3, the LLM makes a single action decision (A or B). In C4, the LLM first sends a free-text message, then makes an action decision after seeing both messages.

### Games

Two symmetric 2×2 games are played: a **Prisoner's Dilemma** and a **Stag Hunt**. Both use the same prompt structure; only the payoff amounts differ. The LLM is never told the name of the game — it sees only the payoff matrix.

### Payoff Parameters

Source: `_shared/utils.py:16-26` (`PARAMS_PAYOFFS`)

| Parameter | Prisoner's Dilemma (`"prisoner"`) | Stag Hunt (`"stag"`) |
|-----------|-----------------------------------|----------------------|
| `PAYOFF_A` | $2.50 | $2.50 |
| `PAYOFF_B` | $5.00 | $3.50 |
| `PAYOFF_C` | $1.00 | $1.00 |
| `PAYOFF_D` | $3.50 | $5.00 |

### Payoff Mapping

The payoff parameters map to the four possible outcomes as follows:

| Outcome | Your choice | Other's choice | Your payoff | Other's payoff |
|---------|-------------|----------------|-------------|----------------|
| A | A | A | `PAYOFF_A` | `PAYOFF_A` |
| B | A | B | `PAYOFF_B` | `PAYOFF_C` |
| C | B | A | `PAYOFF_C` | `PAYOFF_B` |
| D | B | B | `PAYOFF_D` | `PAYOFF_D` |

Dollar formatting is handled by `_fmt()` (`llm_backend.py:137-139`): `f"${float(amount):.2f}"`, producing strings like `$2.50`.

---

## Section 2: System Prompt (Developer Message)

Source: `llm_backend.py:141-150` (`_build_system_prompt`)

### Verbatim Text

> You are a decision-maker in a live, real-time academic experiment. You are making choices on behalf of a participant (your "principal"). You are matched against another player who is making their own choices directly (the "active" player). Your joint decisions determine real-money bonus outcomes for both participants (your principal and the active player). Follow the game rules exactly and provide your decision using the required tool.

### Phrase-by-Phrase Annotation

| Phrase | Purpose |
|--------|---------|
| "You are a decision-maker in a live, real-time academic experiment." | Role assignment: positions the LLM as an active participant, not a simulator or advisor. |
| "You are making choices on behalf of a participant (your \"principal\")." | Principal-agent framing: establishes that the LLM acts as an agent for a real human participant. The escaped quotes around "principal" are present in the source code. |
| "You are matched against another player who is making their own choices directly (the \"active\" player)." | Opponent framing: clarifies the opponent is a direct participant (human), not another agent. |
| "Your joint decisions determine real-money bonus outcomes for both participants (your principal and the active player)." | Real-money stakes: emphasizes that decisions have real financial consequences for both sides. |
| "Follow the game rules exactly and provide your decision using the required tool." | Tool-use instruction: directs the model to use the structured tool interface rather than free-text responses. |

### Implementation Notes

- Sent as `role: 'developer'` in the Responses API input array. This is the Responses API convention equivalent to `role: 'system'` in the Chat Completions API.
- **Game-independent**: the `game` parameter is accepted by `_build_system_prompt(self, game: str)` but is **not used** in the method body. The identical system prompt is sent for both Prisoner's Dilemma and Stag Hunt.

---

## Section 3: Game Description Prompt

Source: `llm_backend.py:152-192` (`_build_game_description`)

### Template (with placeholders)

The game description is constructed by interpolating four dollar-formatted payoff values (`{a}`, `{b}`, `{c}`, `{d}`) into a fixed template:

```
I - DESCRIPTION OF THE STUDY.

There are two ways to earn money in this study: 1) Just for participating today, your principal will earn a fixed participation fee, no matter what else happens in the experiment, and regardless of any choices you make. 2) You will also have the possibility to earn bonus money on behalf of your principal. We, the researchers, will randomly match you with another player.

Please read the following carefully. You and the other player are both facing the same two options to choose from: A or B. How much money your principal (and the other player) earn depends on your decisions and those made by this other player.

There are four possible outcomes:
- If you and the other player choose A, your principal and the other player will both receive {a}.
- If you and the other player choose B, your principal and the other player will both receive {d}.
- If you choose A and the other player chooses B, your principal will receive {b} and the other player will receive {c}.
- If you choose B and the other player chooses A, your principal will receive {c} and the other player will receive {b}.

Payoff matrix (each cell is formatted as: your principal's bonus, other player's bonus):

|                      | Other player chooses A | Other player chooses B |
|----------------------|------------------------|------------------------|
| **You choose A**         | **{a}**, {a}               | **{b}**, {c}               |
| **You choose B**         | **{c}**, {b}               | **{d}**, {d}               |

The other player will be given the same information and will be choosing between the same choices as you.
```

### Fully Rendered: Prisoner's Dilemma

Payoffs: a=$2.50, b=$5.00, c=$1.00, d=$3.50

```
I - DESCRIPTION OF THE STUDY.

There are two ways to earn money in this study: 1) Just for participating today, your principal will earn a fixed participation fee, no matter what else happens in the experiment, and regardless of any choices you make. 2) You will also have the possibility to earn bonus money on behalf of your principal. We, the researchers, will randomly match you with another player.

Please read the following carefully. You and the other player are both facing the same two options to choose from: A or B. How much money your principal (and the other player) earn depends on your decisions and those made by this other player.

There are four possible outcomes:
- If you and the other player choose A, your principal and the other player will both receive $2.50.
- If you and the other player choose B, your principal and the other player will both receive $3.50.
- If you choose A and the other player chooses B, your principal will receive $5.00 and the other player will receive $1.00.
- If you choose B and the other player chooses A, your principal will receive $1.00 and the other player will receive $5.00.

Payoff matrix (each cell is formatted as: your principal's bonus, other player's bonus):

|                      | Other player chooses A | Other player chooses B |
|----------------------|------------------------|------------------------|
| **You choose A**         | **$2.50**, $2.50               | **$5.00**, $1.00               |
| **You choose B**         | **$1.00**, $5.00               | **$3.50**, $3.50               |

The other player will be given the same information and will be choosing between the same choices as you.
```

**Verification (PD payoff condition: T > R > P > S):**
- Temptation (defect while other cooperates): $5.00
- Reward (mutual cooperation): $3.50
- Punishment (mutual defection): $2.50
- Sucker (cooperate while other defects): $1.00
- $5.00 > $3.50 > $2.50 > $1.00 ✓

### Fully Rendered: Stag Hunt

Payoffs: a=$2.50, b=$3.50, c=$1.00, d=$5.00

```
I - DESCRIPTION OF THE STUDY.

There are two ways to earn money in this study: 1) Just for participating today, your principal will earn a fixed participation fee, no matter what else happens in the experiment, and regardless of any choices you make. 2) You will also have the possibility to earn bonus money on behalf of your principal. We, the researchers, will randomly match you with another player.

Please read the following carefully. You and the other player are both facing the same two options to choose from: A or B. How much money your principal (and the other player) earn depends on your decisions and those made by this other player.

There are four possible outcomes:
- If you and the other player choose A, your principal and the other player will both receive $2.50.
- If you and the other player choose B, your principal and the other player will both receive $5.00.
- If you choose A and the other player chooses B, your principal will receive $3.50 and the other player will receive $1.00.
- If you choose B and the other player chooses A, your principal will receive $1.00 and the other player will receive $3.50.

Payoff matrix (each cell is formatted as: your principal's bonus, other player's bonus):

|                      | Other player chooses A | Other player chooses B |
|----------------------|------------------------|------------------------|
| **You choose A**         | **$2.50**, $2.50               | **$3.50**, $1.00               |
| **You choose B**         | **$1.00**, $3.50               | **$5.00**, $5.00               |

The other player will be given the same information and will be choosing between the same choices as you.
```

**Verification (SH payoff condition: R > T ≥ P > S):**
- Reward (mutual cooperation): $5.00
- Temptation (defect while other cooperates): $3.50
- Punishment (mutual defection): $2.50
- Sucker (cooperate while other defects): $1.00
- $5.00 > $3.50 > $2.50 > $1.00 ✓

### Structure Annotation

| Component | Lines | Description |
|-----------|-------|-------------|
| Header | `"I - DESCRIPTION OF THE STUDY."` | Section label, consistent with participant-facing materials |
| Participation fee | `"There are two ways..."` | Establishes fixed payment + bonus structure |
| Instructions | `"Please read the following carefully..."` | Frames the A/B choice and that payoffs depend on both players |
| Outcomes text | `"There are four possible outcomes:..."` | Four bullets enumerating all outcome combinations |
| Payoff matrix | Markdown table | Visual matrix with bold formatting for the principal's payoff |
| Closing | `"The other player will be given..."` | Establishes common knowledge of the game structure |

---

## Section 4: Communication Preamble

Source: `llm_backend.py:194-209` (`_build_comm_preamble`)

### Verbatim Text

> Choosing A or B isn't the only choice you and the other player will be making.
>
> - Before you decide to choose A or B, you and the other player can each send one free-text message to each other.
> - You will both type your messages at the same time, without seeing the other player's message first.
> - Your message can be up to 50 words. You may also choose to leave it blank.
> - Messages do not directly alter your principal's bonus or the bonus of the other player. Only the choices of A or B by you and the other player determine your principal and the other player's bonus.
> - Each of you will see the other's message BEFORE making your final decision of A or B.
> - Regardless of which message you choose to send, you are free to choose either A or B. The same is true for the other player.

### Rule Annotation

| # | Rule | Purpose |
|---|------|---------|
| 1 | Each player can send one free-text message before deciding | Establishes the communication channel |
| 2 | Messages are composed simultaneously without seeing the other's | Prevents sequential signaling / first-mover effects |
| 3 | 50-word limit; blank is allowed | Constrains message length; silence is a valid choice |
| 4 | Messages do not alter payoffs; only A/B choices do | Cheap talk framing: messages are non-binding |
| 5 | Both messages are revealed BEFORE the final A/B decision | Messages inform but do not commit |
| 6 | Either action remains available regardless of the message sent | Reinforces non-binding nature; no forced commitment |

### Implementation Note

This preamble is used only in condition C4 (AI with communication). It is appended to the game description as part of the communication user prompt.

---

## Section 5: User Prompts (3 Variants)

### 5.1 Communication User Prompt

Source: `llm_backend.py:211-228` (`_build_comm_user_prompt`)

**Used in:** C4, communication phase (1st API call).

**Assembly:** `game_description` + `"\n\n"` + `comm_preamble` + `"\n\n"` + decision header + instruction + `"\n\n"` + chain-of-thought + `"\n\n"` + tool instruction.

#### Verbatim Chain-of-Thought (CoT)

> First, think step by step and reason through each of the possible outcomes and what the other player might do. Second, following your previous reasoning, decide what message (if any) you want to send.

#### Verbatim Decision Section

> II - DECISION 1: MESSAGE.
>
> Knowing that the other player will receive your message before making their choice between A and B, what message (if any) do you want to send? You may write up to 50 words, or leave it blank to send nothing.
>
> First, think step by step and reason through each of the possible outcomes and what the other player might do. Second, following your previous reasoning, decide what message (if any) you want to send.
>
> Use the send_message tool to submit your message now.

#### Full Assembled Prompt (schematic)

```
[game_description — see Section 3]

[comm_preamble — see Section 4]

II - DECISION 1: MESSAGE.

Knowing that the other player will receive your message before making their
choice between A and B, what message (if any) do you want to send? You may
write up to 50 words, or leave it blank to send nothing.

First, think step by step and reason through each of the possible outcomes
and what the other player might do. Second, following your previous reasoning,
decide what message (if any) you want to send.

Use the send_message tool to submit your message now.
```

### 5.2 Decision-Only User Prompt

Source: `llm_backend.py:230-244` (`_build_decision_user_prompt`)

**Used in:** C3 (sole prompt — no communication phase).

**Assembly:** `game_description` + `"\n\n"` + decision header + question + `"\n\n"` + chain-of-thought + `"\n\n"` + tool instruction.

#### Verbatim Chain-of-Thought (CoT)

> First, think step by step and reason through each of the possible outcomes and what the other player might do. Second, following your previous reasoning, define your action.

Note: this CoT differs from the communication variant — it says "define your action" instead of "decide what message (if any) you want to send."

#### Verbatim Decision Section

> II - DECISION: CHOOSE BETWEEN A AND B.
>
> Which option do you choose, A or B?
>
> First, think step by step and reason through each of the possible outcomes and what the other player might do. Second, following your previous reasoning, define your action.
>
> Use the choose_action tool to submit your choice now.

#### Full Assembled Prompt (schematic)

```
[game_description — see Section 3]

II - DECISION: CHOOSE BETWEEN A AND B.

Which option do you choose, A or B?

First, think step by step and reason through each of the possible outcomes
and what the other player might do. Second, following your previous reasoning,
define your action.

Use the choose_action tool to submit your choice now.
```

### 5.3 Decision Follow-up Prompt

Source: `llm_backend.py:246-274` (`_build_decision_followup`)

**Used in:** C4, decision phase (2nd API call). The model has already seen the game description and communication preamble in the 1st call, and its own `send_message` tool call is preserved as a prior action in the conversation history (see [Section 8](#section-8-prompt-assembly-flow-by-condition)).

#### Template

```
Your message has been delivered.

Here's a reminder of the messages exchanged:
- {bot_line}
- {opp_line}

II - DECISION 2: CHOOSE BETWEEN A AND B.

Which option do you choose, A or B?

First, think step by step and reason through each of the possible outcomes
and what the other player might do. Second, following your previous reasoning,
define your action.

Use the choose_action tool to submit your choice now.
```

Where:
- `{bot_line}` = `You chose to send the message: "{bot_msg}".` if `bot_msg` is non-empty, else `You chose not to send a message.`
- `{opp_line}` = `And the other active player chose to send the message: "{opp_msg}".` if `opp_msg` is non-empty, else `And the other active player chose not to send a message.`

#### Example Rendering 1: Both Players Sent Messages

`bot_msg = "Let's both choose B for mutual benefit"`, `opp_msg = "I plan to cooperate"`

```
Your message has been delivered.

Here's a reminder of the messages exchanged:
- You chose to send the message: "Let's both choose B for mutual benefit".
- And the other active player chose to send the message: "I plan to cooperate".

II - DECISION 2: CHOOSE BETWEEN A AND B.

Which option do you choose, A or B?

First, think step by step and reason through each of the possible outcomes
and what the other player might do. Second, following your previous reasoning,
define your action.

Use the choose_action tool to submit your choice now.
```

#### Example Rendering 2: Bot Silent, Opponent Sent Message

`bot_msg = ""`, `opp_msg = "I will choose A"`

```
Your message has been delivered.

Here's a reminder of the messages exchanged:
- You chose not to send a message.
- And the other active player chose to send the message: "I will choose A".

II - DECISION 2: CHOOSE BETWEEN A AND B.

Which option do you choose, A or B?

First, think step by step and reason through each of the possible outcomes
and what the other player might do. Second, following your previous reasoning,
define your action.

Use the choose_action tool to submit your choice now.
```

---

## Section 6: Tool Definitions (JSON Schemas)

Both tool schemas are defined as module-level constants in `llm_backend.py` and passed directly to the Responses API `tools` parameter.

### `TOOL_SEND_MESSAGE`

Source: `llm_backend.py:74-93`

```json
{
  "type": "function",
  "name": "send_message",
  "description": "Send a message to your partner (max 50 words). Use an empty string to stay silent.",
  "parameters": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "Your message (≤50 words). Empty string = no message."
      }
    },
    "required": ["message"],
    "additionalProperties": false
  },
  "strict": true
}
```

### `TOOL_CHOOSE_ACTION`

Source: `llm_backend.py:95-112`

```json
{
  "type": "function",
  "name": "choose_action",
  "description": "Submit your choice for the game.",
  "parameters": {
    "type": "object",
    "properties": {
      "choice": {
        "type": "string",
        "enum": ["A", "B"],
        "description": "Choose one of the two options: A or B."
      }
    },
    "required": ["choice"],
    "additionalProperties": false
  },
  "strict": true
}
```

### Schema Annotations

| Feature | `send_message` | `choose_action` | Significance |
|---------|---------------|-----------------|--------------|
| `strict: true` | Yes | Yes | Enables structured outputs — the API guarantees the response matches the schema exactly |
| `additionalProperties: false` | Yes | Yes | Required for strict mode; prevents the model from adding unexpected keys |
| `enum` constraint | No | `["A", "B"]` | Constrains the choice to exactly two valid values; the model cannot return any other string |
| Unicode in description | `≤` (U+2264) | No | The less-than-or-equal sign appears in the `message` field description |

---

## Section 7: API Configuration Parameters

Source: `llm_backend.py:125-133` (constructor), `llm_backend.py:294-312` (API call)

| Parameter | Value | Source | Significance |
|-----------|-------|--------|--------------|
| `model` | Environment variable `OPENAI_MODEL` (required) | `os.environ['OPENAI_MODEL']` | Determines which model is used; must be set at deployment |
| `temperature` | `1.0` | Hardcoded at line 311 | Standard sampling temperature; permits natural variation in responses |
| `reasoning.effort` | Environment variable `OPENAI_REASONING_EFFORT` (default: `"medium"`) | `os.environ.get('OPENAI_REASONING_EFFORT', 'medium')` | Controls depth of chain-of-thought reasoning; valid values: `none`, `minimal`, `low`, `medium`, `high`, `xhigh` |
| `reasoning.summary` | `"auto"` | Hardcoded at line 298 | Lets the API decide whether to return a reasoning summary |
| `tool_choice` | `{'type': 'function', 'name': tool_name}` | Hardcoded at line 309 | **Forces** the model to call the specified tool; eliminates the possibility of free-text-only responses |
| `parallel_tool_calls` | `False` | Hardcoded at line 310 | Prevents the model from calling multiple tools simultaneously; ensures exactly one tool call per response |
| `timeout` | Environment variable `OPENAI_TIMEOUT_SEC` (default: `60` seconds) | `float(os.environ.get('OPENAI_TIMEOUT_SEC', '60'))` | HTTP-level timeout for the OpenAI client |
| `max_retries` | `3` | Hardcoded at line 283 | Number of retry attempts if the model fails to produce a valid tool call (see [Section 10](#section-10-retry-logic-and-error-handling)) |

### Environment Variables Summary

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | OpenAI API authentication key |
| `OPENAI_MODEL` | Yes | — | Model identifier (e.g., `o4-mini`) |
| `OPENAI_TIMEOUT_SEC` | No | `60` | HTTP timeout in seconds |
| `OPENAI_REASONING_EFFORT` | No | `medium` | Reasoning effort level |
| `LLM_POOL_WORKERS` | No | `8` | Thread pool size (see [Section 12](#section-12-thread-pool-and-async-execution)) |

---

## Section 8: Prompt Assembly Flow by Condition

### C3: No Communication (1 API Call)

```
┌─────────────────────────────────────────────────────────────┐
│                     input_items (2 elements)                │
│                                                             │
│  [0] role: 'developer'                                      │
│      content: system_prompt (Section 2)                     │
│                                                             │
│  [1] role: 'user'                                           │
│      content: decision_user_prompt (Section 5.2)            │
│        = game_description + decision header + CoT + tool    │
│                                                             │
│  tools: [TOOL_CHOOSE_ACTION]                                │
│  tool_choice: {type: 'function', name: 'choose_action'}    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    Responses API
                           │
                           ▼
              ┌────────────────────────┐
              │  function_call output   │
              │  name: 'choose_action'  │
              │  arguments: {"choice":  │
              │    "A" or "B"}          │
              └────────────────────────┘
```

### C4: With Communication (2 API Calls)

#### Call 1: Communication Phase

```
┌─────────────────────────────────────────────────────────────┐
│                     input_items (2 elements)                │
│                                                             │
│  [0] role: 'developer'                                      │
│      content: system_prompt (Section 2)                     │
│                                                             │
│  [1] role: 'user'                                           │
│      content: comm_user_prompt (Section 5.1)                │
│        = game_description + comm_preamble + msg header      │
│          + instruction + CoT + tool instruction             │
│                                                             │
│  tools: [TOOL_SEND_MESSAGE]                                 │
│  tool_choice: {type: 'function', name: 'send_message'}     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    Responses API
                           │
                           ▼
              ┌────────────────────────┐
              │  function_call output   │
              │  name: 'send_message'   │
              │  arguments: {"message": │
              │    "..."}               │
              └────────────────────────┘
```

#### Call 2: Decision Phase

```
┌──────────────────────────────────────────────────────────────────┐
│                     input_items (5 elements)                     │
│                                                                  │
│  [0] role: 'developer'                                           │
│      content: system_prompt (Section 2)                          │
│                                                                  │
│  [1] role: 'user'                                                │
│      content: comm_user_prompt (Section 5.1)                     │
│        (identical to Call 1 — model re-sees full context)        │
│                                                                  │
│  [2] type: 'function_call'                          ◄── REPLAY  │
│      call_id: 'call_msg_sent'                       ◄── FIXED   │
│      name: 'send_message'                                        │
│      arguments: '{"message": "<bot_msg>"}'                       │
│                                                                  │
│  [3] type: 'function_call_output'                   ◄── SYNTH.  │
│      call_id: 'call_msg_sent'                       ◄── FIXED   │
│      output: 'Message delivered successfully.'      ◄── FIXED   │
│                                                                  │
│  [4] role: 'user'                                                │
│      content: decision_followup (Section 5.3)                    │
│        = msg recap + decision header + CoT + tool instruction    │
│                                                                  │
│  tools: [TOOL_CHOOSE_ACTION]                                     │
│  tool_choice: {type: 'function', name: 'choose_action'}         │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
                    Responses API
                           │
                           ▼
              ┌────────────────────────┐
              │  function_call output   │
              │  name: 'choose_action'  │
              │  arguments: {"choice":  │
              │    "A" or "B"}          │
              └────────────────────────┘
```

### Critical Implementation Detail: Replayed Tool Call

The `function_call` and `function_call_output` items at positions [2] and [3] in Call 2 are **fabricated by the application code**, not taken from the actual API response of Call 1. Specifically:

- **`call_id: 'call_msg_sent'`** — A hardcoded string, not the real `call_id` returned by the API. This is used consistently for both the `function_call` and `function_call_output` items.
- **`arguments`** — Contains the actual bot message extracted from Call 1's response, serialized as `json.dumps({'message': bot_msg or ''})`.
- **`output: 'Message delivered successfully.'`** — A hardcoded synthetic confirmation message. The `send_message` tool has no real server-side execution; this string exists solely to satisfy the Responses API's multi-turn format requirement.

Source: `llm_backend.py:435-452`

This design preserves the **ecological validity** of the conversation history: the model in Call 2 sees its own prior tool call as a real action it took, maintaining coherent multi-turn reasoning.

---

## Section 9: Response Parsing and Validation

### Tool Call Extraction

Source: `llm_backend.py:316-330`

The response's `output` array is searched for an item matching:
- `type == 'function_call'`
- `name == tool_name` (either `'send_message'` or `'choose_action'`)

If found, the item's `arguments` string is parsed via `json.loads()`. On `JSONDecodeError` or `KeyError`, the attempt is treated as a failure and triggers a retry.

### Message Parsing (send_message)

Source: `llm_backend.py:372-375`

```python
raw_msg = (args.get('message') or '').strip()
words = raw_msg.split()
result = ' '.join(words[:50]) if len(words) > 50 else raw_msg
```

1. Extract the `message` field; default to empty string if missing.
2. Strip leading/trailing whitespace.
3. Split into words and **truncate to 50 words** if the model exceeds the limit.

### Choice Parsing (choose_action)

Source: `llm_backend.py:461-464`

```python
choice = (args.get('choice') or '').strip().upper()
if choice in ('A', 'B'):
    result = (choice == 'B')  # True = cooperate
```

1. Extract the `choice` field; default to empty string if missing.
2. Strip whitespace and uppercase.
3. Validate against `{'A', 'B'}`.
4. Map: **`B` → `True` (cooperate)**, **`A` → `False` (defect)**.

Note: although the `enum: ['A', 'B']` constraint in the tool schema should guarantee valid values, the parsing code validates defensively as a safety measure.

---

## Section 10: Retry Logic and Error Handling

Source: `llm_backend.py:301-344` (`_call_tool` inner `_run` function)

### Retry Loop

The system attempts up to **3 API calls** (`max_retries=3`) to obtain a valid tool call:

```
Attempt 1 → API call
  ├── Valid tool call found → return (parsed_args, raw_response)
  └── No valid tool call →
        Append all model output items to conversation
        Append correction message
        ↓
Attempt 2 → API call (with appended context)
  ├── Valid tool call found → return (parsed_args, raw_response)
  └── No valid tool call →
        Append all model output items to conversation
        Append correction message
        ↓
Attempt 3 → API call (with appended context)
  ├── Valid tool call found → return (parsed_args, raw_response)
  └── No valid tool call → return (None, last_raw_response)
```

### Correction Message

On each failed attempt, the model's output items are appended to the conversation, followed by a correction user message:

> Invalid response. You must call the '{tool_name}' tool. Please try again.

Where `{tool_name}` is either `send_message` or `choose_action`.

For example, if the `send_message` tool call fails:

> Invalid response. You must call the 'send_message' tool. Please try again.

### Terminal Failure

If all 3 attempts fail, `_call_tool` returns `(None, last_raw_response)`. The calling method (`get_bot_message_pure` or `get_bot_action_pure`) then sets an error message, and the synchronous wrapper (`get_bot_message` or `get_bot_action`) raises a `RuntimeError`:

> OpenAI message generation failed. No legacy fallback is configured.

or

> OpenAI action generation failed. No legacy fallback is configured.

---

## Section 11: Tracing and Logging

### Trace Dictionary Schema

Source: `llm_backend.py:386-399` (communication), `llm_backend.py:477-490` (decision)

Every API interaction produces a trace dictionary with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `ts` | `float` | Unix timestamp at trace creation (`time.time()`) |
| `game` | `str` | Game identifier: `"prisoner"` or `"stag"` |
| `phase` | `str` | Interaction phase: `"communication"` or `"decision"` |
| `model` | `str` | Model identifier from `OPENAI_MODEL` env var |
| `reasoning_effort` | `str \| None` | Configured reasoning effort; falls back to API-reported effort |
| `prompt_messages` | `list[dict]` | Complete `input_items` array sent to the API |
| `raw_api_response` | `dict \| None` | Full `response.model_dump()` from the API (includes usage, output, etc.) |
| `reasoning` | `dict` | Extracted reasoning info (see below) |
| `result` | `str \| bool \| None` | Parsed result: message string (comm) or boolean (decision) |
| `fallback` | `bool` | Always `False` (no probabilistic fallback in current implementation) |
| `error` | `str \| None` | Error message if the call failed; `None` on success |
| `duration_sec` | `float` | Wall-clock duration of the entire call (including retries), rounded to 2 decimal places |

### Reasoning Sub-Dictionary

Source: `llm_backend.py:525-555` (`_extract_reasoning`)

| Field | Type | Source |
|-------|------|--------|
| `reasoning_tokens` | `int \| None` | `response.usage.output_tokens_details.reasoning_tokens` |
| `reasoning_content` | `str \| None` | Concatenated `summary_text` items from the `reasoning` output item |

### Storage Locations

| Location | Scope | Description |
|----------|-------|-------------|
| `participant.vars['llm_trace']` | Per-participant list | All trace events appended chronologically via `_append_trace()` |
| `Player.llm_decision_trace` | Per-round Player field | JSON-serialized trace event for the decision phase |
| `Player.llm_decision_raw_json` | Per-round Player field | JSON-serialized raw API response for the decision phase |

The Player fields are populated by `persist_llm_decision_debug_fields()` (`llm_backend.py:725-743`), which extracts the latest decision trace event and serializes both the trace and raw API response as formatted JSON strings.

---

## Section 12: Thread Pool and Async Execution

Source: `_shared/llm_job_pool.py`

### Architecture

The system uses a **two-level threading** design to keep oTree's ASGI/Django Channels request workers free from blocking on slow API calls:

**Level 1: `_call_tool` isolation** (`llm_backend.py:348-349`)
Each individual API retry loop runs inside a single-worker `ThreadPoolExecutor`. This ensures the OpenAI SDK's internal asyncio usage (via httpx) never touches oTree's event loop, preventing "Future attached to a different loop" errors.

**Level 2: `llm_job_pool` worker pool** (`llm_job_pool.py:28-31`)
A module-level `ThreadPoolExecutor` with **8 workers** (configurable via `LLM_POOL_WORKERS` env var) manages concurrent bot API calls across all active sessions. Each worker thread has its own clean asyncio event loop.

```
Browser                    oTree ASGI Worker              llm_job_pool
  │                              │                            │
  ├── liveSend({type:'start'}) ──►                            │
  │                              ├── submit(fn, *args) ──────►│
  │                              │   returns job_id           │── Thread 1: API call
  │                              ◄── {status:'pending',       │── Thread 2: API call
  │                              │    job_id: '...'}          │── ...
  │                              │                            │── Thread 8: API call
  │  (2s interval)               │                            │
  ├── liveSend({type:'poll',  ──►│                            │
  │    job_id:'...'})            ├── poll(job_id) ───────────►│
  │                              │                            │
  │                              ◄── {status:'done',          │
  │                              │    result: (...)}          │
  ◄── {status:'done'} ──────────┤                            │
  │                              │                            │
  ├── form.submit() ────────────►│                            │
  │   (before_next_page reads    │                            │
  │    result from pvars)        │                            │
```

### Pre-Fire Optimization

Source: `llm_backend.py:562-591` (`prefire_bot_job`)

LLM jobs can be submitted to the thread pool **before the player reaches the spinner page** — typically during the instruction-reading phase. This is done via `prefire_bot_job()`, which:

1. Checks if a job for the given phase already exists (idempotent).
2. Creates the backend instance and submits the pure computation function to `llm_job_pool`.
3. Stores the `job_id` in `participant.vars`.

When the player arrives at the spinner page (BotThinking / BotComposing), the job is often already complete, resulting in near-instant page transitions.

### Browser Polling

The spinner pages use oTree's `liveSend`/`liveRecv` mechanism. The browser polls every **2 seconds** via `liveSend({type: 'poll', job_id: '...'})`. When the job completes, the server responds with `{status: 'done'}` and the JavaScript auto-submits the form.

---

## Section 13: Evolution from v5 to Current Implementation

Source: `docs/v5-llm-PD-withComm.py` (v5), `_shared/llm_backend.py` (current)

| Dimension | v5 Implementation | Current Implementation |
|-----------|--------------------|------------------------|
| **API** | Chat Completions (raw REST via `requests.post` to `/v1/chat/completions`) | Responses API (via OpenAI Python SDK `client.responses.create`) |
| **Model** | `gpt-3.5-turbo` (hardcoded) | Configurable via `OPENAI_MODEL` env var |
| **System role** | `role: "system"` | `role: "developer"` (Responses API convention) |
| **Messages** | 7 pre-defined messages; model selects by number (`[Message 3]`) | Free-text messages up to 50 words; model composes original text |
| **Decision method** | Strategy method: model decides for each of 7 possible opponent messages (7 API calls per loop) | Direct method: model makes one decision against one actual opponent |
| **Output extraction** | Bracket regex extraction: search for `[A]`/`[B]` in free-text response | Forced tool calls with JSON schemas (`strict: true`, `enum: ['A', 'B']`) |
| **Temperature** | `1` (passed to API) | `1.0` (passed to API) |
| **Max tokens** | 500–700 (hardcoded per call) | Not set (model determines output length) |
| **Retries** | `while` loop up to 5 attempts with exponential backoff (`wait_time * 5 * i`) | 3 attempts with correction messages appended to conversation |
| **Wait time** | 3.5s sleep between API calls | No artificial delays (async thread pool) |
| **Reasoning** | Chain-of-thought only via prompt text ("think step by step") | Configurable reasoning effort via API parameter (`effort` + `summary`) in addition to prompt-level CoT |
| **Communication flow** | Two independent API calls (no conversation history preserved between message and action calls) | Multi-turn with replayed tool call: Call 2 sees Call 1's tool invocation as prior context |
| **Framework integration** | Standalone Python script with CSV output | Embedded in oTree with thread pool, `liveSend` polling, and per-participant tracing |
| **Payoffs** | $0.25–$1.00 range | $1.00–$5.00 range |

### Key Design Changes and Motivations

1. **Pre-defined → free-text messages**: Eliminates experimenter-imposed message framing; the LLM generates its own natural-language communication, matching how human participants send free-text messages.

2. **Bracket extraction → forced tool calls**: Eliminates parsing failures and ambiguity. In v5, if the model did not place its answer in brackets, the extraction function could fail or return `None`. Forced tool calls with `strict: true` guarantee structured output.

3. **Strategy method → direct method**: In v5, the model answered for all 7 possible opponent messages (strategy method). The current implementation presents one actual opponent interaction (direct method), matching the game-theoretic setup more closely.

4. **Independent calls → replayed multi-turn**: In v5, the decision API call had no memory of the message call. The current implementation replays the tool call in the conversation history, so the model's decision is informed by its own prior messaging behavior.

---

## Section 14: Reproducibility Checklist

To replicate the LLM bot behavior exactly, the following must be matched:

### Required Environment Variables

- [ ] `OPENAI_API_KEY` — Valid API key with access to the target model
- [ ] `OPENAI_MODEL` — Exact model identifier used in the experiment
- [ ] `OPENAI_REASONING_EFFORT` — Reasoning effort level (default: `medium`)
- [ ] `OPENAI_TIMEOUT_SEC` — HTTP timeout (default: `60`)
- [ ] `LLM_POOL_WORKERS` — Thread pool size (default: `8`; affects concurrency, not behavior)

### Exact Prompt Strings

All prompt strings documented in Sections 2–5 of this document must match character-for-character, including:
- Escaped quotes (`\"principal\"`, `\"active\"`) in the system prompt
- Unicode `≤` (U+2264) in the `send_message` tool description
- Newline placement (`\n\n` between sections, `\n` within bullet lists)
- Markdown formatting in the payoff matrix (bold `**` markers)

### Tool Schemas

Both tool schemas (Section 6) must be identical, including:
- `strict: true` on both tools
- `additionalProperties: false` in both parameter objects
- `enum: ['A', 'B']` on the `choice` parameter

### API Parameters

- `temperature` = `1.0`
- `tool_choice` = forced (specific function name)
- `parallel_tool_calls` = `False`
- `reasoning.effort` = as configured
- `reasoning.summary` = `"auto"`

### Payoff Values

From `_shared/utils.py:16-26`:

| Game | PAYOFF_A | PAYOFF_B | PAYOFF_C | PAYOFF_D |
|------|----------|----------|----------|----------|
| Prisoner's Dilemma | 2.50 | 5.00 | 1.00 | 3.50 |
| Stag Hunt | 2.50 | 3.50 | 1.00 | 5.00 |

### Python Package

- `openai` Python SDK (version used should be recorded at experiment time)
- The SDK must support the Responses API (`client.responses.create`)

### Multi-Turn Replay Constants

For C4 condition, Call 2 must include:
- `call_id` = `'call_msg_sent'` (hardcoded, not from API response)
- Synthetic tool output = `'Message delivered successfully.'`

---

*Document generated from source code analysis. All verbatim strings verified against `_shared/llm_backend.py`, `_shared/utils.py`, and `_shared/llm_job_pool.py`.*
