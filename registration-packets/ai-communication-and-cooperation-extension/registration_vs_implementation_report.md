# Registration vs. Implementation: Change Report

**Registration**: [w5zv9](https://osf.io/w5zv9) — *Communication and Cooperation with Human and Artificial Agents*
**Registered**: 2023-08-21
**Schema**: OSF Preregistration v3

**Implementation**: oTree experiment (`otree-aicoop-4.0-free_msg-v2026_03`)
**Generated**: 2026-03-16

---

## Major Changes

### 1. One game becomes two

- **Registration**: A single one-shot Prisoner's Dilemma.
- **Implementation**: Two sequential games — a **Prisoner's Dilemma** (Game 1) followed by a **Stag Hunt** (Game 2). One game is randomly selected to determine the bonus. This is a significant design expansion not mentioned in the preregistration.

### 2. Pre-defined messages become free-text

- **Registration**: Communication conditions used "seven possible pre-defined messages."
- **Implementation**: Participants (or AI) type **free-text messages up to 50 words**. This is a fundamentally different communication manipulation — open-ended language vs. constrained choice from a menu.

### 3. Six conditions collapse to four

- **Registration**: 6 conditions — a 2x2 for active human players + 2 additional "passive" conditions where the algorithm played on behalf of a human who only guessed outcomes.
- **Implementation**: 4 conditions (c1–c4). The passive participants are still present in AI conditions (c3, c4) but are built into the same condition as a paired "bot player" rather than separate conditions. The passive players now see the AI's actual choices in real time and answer survey items rather than being in standalone guessing conditions.

| Condition | Short label | Opponent type | Communication |
|-----------|-------------|---------------|---------------|
| condition_1 | c1 | Human | No |
| condition_2 | c2 | Human | Yes |
| condition_3 | c3 | AI bot | No |
| condition_4 | c4 | AI bot | Yes |

### 4. Platform switch: Qualtrics to oTree

- **Registration**: "Simple randomization through the Qualtrics functionality."
- **Implementation**: oTree-based experiment with real-time participant matching, wait rooms, and live AI API calls. This enables the synchronous two-player interaction that Qualtrics could not support.

### 5. Recruitment: MTurk to in-lab

- **Registration**: Amazon Mechanical Turk, US residents, English-speaking, 18+.
- **Implementation**: In-lab at Stony Brook University — participants enter a Lab PC Number, are told to "remain seated," and lab administrators handle payment. No mention of MTurk.

### 6. Payment scale increased substantially

- **Registration**: $1 participation + $0.25–$1 bonus.
- **Implementation**: $7 participation + up to $5 bonus (payoffs per game cell range from $1.00 to $5.00). This is a ~7x increase in base pay and ~5x in max bonus.

### 7. AI agent: pre-programmed to live ChatGPT

- **Registration**: "We prompted the Chat-GPT algorithm to play a prisoner's dilemma" — implied a static prompt / pre-recorded behavior.
- **Implementation**: Explicitly described as a "live instance of ChatGPT" connected in real time to OpenAI's GPT server. It reads game instructions, sees exchanged messages, and reasons through choices live during the session. Participants see a "The AI is making its decision..." wait screen.

### 8. Payoff structure changed

- **Registration**: Payoffs described as "$0.25 to $1" bonus; specific cell values not detailed.
- **Implementation**:

**Prisoner's Dilemma (Game 1)**

|  |  | Other player |  |
|--|--|--|--|
|  |  | Choice A | Choice B |
| You | Choice A | $2.50, $2.50 | $5.00, $1.00 |
|  | Choice B | $1.00, $5.00 | $3.50, $3.50 |

**Stag Hunt (Game 2)**

|  |  | Other player |  |
|--|--|--|--|
|  |  | Choice A | Choice B |
| You | Choice A | $2.50, $2.50 | $3.50, $1.00 |
|  | Choice B | $1.00, $3.50 | $5.00, $5.00 |

---

## Moderate Changes

### 9. Comprehension check expanded

- **Registration**: "One comprehension question" used as a covariate.
- **Implementation**: A comprehension question per game (Game 1 and Game 2), each with a randomly selected choice-pair and radio-select answers corresponding to the payoff matrix. Still appears to be used as a covariate rather than exclusion criterion.

### 10. Survey battery expanded

- **Registration**: Measured variables described vaguely — "Other outcomes are measured by survey items. See the attached documents."
- **Implementation**: Six survey pages covering:
  - AI attitudes and experience with LLMs
  - Demographics
  - Political views (party ID, ideology)
  - Post-game items: trust in opponent/bot, perceived honesty, selfishness, sincerity, whether opponent was unbiased, whether it had "a mind of its own," perceived intentions
  - Beliefs about opponent's choice of B in each game

### 11. AI regulation hypothesis — unclear operationalization

- **Registration** hypothesis 4: "Support for AI regulation will be higher in human-ai conditions than human-human conditions."
- **Implementation**: The current survey pages do not show an explicit AI regulation item in the rendered report. The Survey2/3 pages render dynamic `[field.label]` content not fully visible in the static document, so the item may still be present but is not confirmed.

---

## What Remained Consistent

- Core 2x2 factorial logic (opponent type x communication) is preserved
- Between-subjects design
- Single-blind (participants do not know their treatment condition)
- The no-deception commitment is maintained — condition-specific debriefings emphasize "everything we told you is 100% accurate and true"
- Choices are still A vs. B (defect vs. cooperate framing)
- The overarching research question — how AI-mediated interaction affects cooperation — is the same

---

## Assessment

The current experiment is best described as a substantially redesigned extension of the registered study, not a direct execution of it. The addition of the Stag Hunt, the switch to free-text communication, the move to lab-based real-time interaction with a live ChatGPT agent, and the revised payoff/payment structure collectively represent a materially different protocol from what was preregistered. Any confirmatory claims would need a new registration to cover these changes.
