"""
Update draft registration 69bce30f78362cbc4abff59c with revised fields.

Changes:
1. 344-40 (Design): Add signal game as separate protocol, disclose bot-seat design
2. 344-44 (Randomization): Permuted-block randomization, not simple random
3. 344-47 (Procedures): Update session duration, add orphan path disclosure
4. 344-62 (Outcomes): Fix variable names (trust_ai_bot), add belief measures as confirmatory DV
5. 344-71 (Analysis plan): Drop Bayesian model, replace with mixed-effects LPM matching Study 2; add belief ANOVA
6. 344-75 (Transformations): Fix trust variable name mapping
7. 344-77 (Inference): Remove Bayesian inference criteria
8. 344-79 (Exclusions): Drop comprehension-as-covariate, add bot-seat exclusion, operationalize dropout
9. 344-83 (Exploratory): Move belief measures out (now confirmatory), keep comprehension as exploratory moderator
10. 344-86 (Other): Remove PyStan from software list, add communication flow details
11. description: Remove Bayesian mention
12. tags: Fix "Stag Hung" typo
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from osf_api_cli.client import OSFClient

DRAFT_ID = "69bce30f78362cbc4abff59c"

# ── Updated field values ──────────────────────────────────────────────

UPDATES = {}

# 344-40: Design — add signal game disclosure + bot-seat disclosure
UPDATES["344-40"] = (
    "This is a 2×2 between-subjects factorial design crossing two factors: "
    "Opponent Type (Human vs. AI) and Communication (None vs. Free-text). "
    "The four conditions are:\n\n"
    "- Condition 1 (c1): Human opponent, No communication\n"
    "- Condition 2 (c2): Human opponent, Free-text communication\n"
    "- Condition 3 (c3): AI bot opponent, No communication\n"
    "- Condition 4 (c4): AI bot opponent, Free-text communication\n\n"
    "All participants play two sequential games with the same partner: "
    "Game 1 is a Prisoner's Dilemma, and Game 2 is a Stag Hunt. "
    "In communication conditions (c2, c4), participants exchange free-text messages "
    "(up to 50 words each) simultaneously before making their decision in each game. "
    "Both players compose their messages independently; once both have submitted, "
    "both messages are displayed on a shared screen before the decision page. "
    "Messages are non-binding cheap talk and do not directly affect payoffs.\n\n"
    "This experiment is the second in a lab session sequence. The first task is a completely "
    "independent study conducted by a separate research team; its outcome is withheld until the "
    "end of the session and has no bearing on the cooperation games.\n\n"
    "The experiment is conducted in the Behavioral Political Economy Lab at Stony Brook University "
    "using the oTree platform. Sessions are allocated in a 1/6, 1/6, 2/6, 2/6 ratio across "
    "c1, c2, c3, and c4 respectively. Because human-opponent sessions (c1, c2) pair two humans "
    "— each contributing a data point — while AI-opponent sessions (c3, c4) pair one active human "
    "with a bot, running twice as many AI-condition sessions yields approximately equal numbers of "
    "human observations (~100) in every condition.\n\n"
    "Bot-seat design: In AI-opponent conditions (c3, c4), both seats in each pair are filled by "
    "real human participants arriving to the lab. One participant is randomly designated as the "
    "active player; the other is designated as the passive (bot-seat) participant on whose behalf "
    "a live ChatGPT instance makes cooperation-game decisions. The bot-seat participant completes "
    "the consent and survey, but does not make their own PD/SH choices. "
    "Bot-seat participants are excluded from all confirmatory analyses (see Exclusion Criteria). "
    "ChatGPT receives the same game instructions shown to participants and makes choices in real time. "
    "One of the two games is randomly selected at the end to determine each participant's bonus payment."
)

# 344-44: Randomization — permuted-block
UPDATES["344-44"] = (
    "Randomization is handled by the oTree platform using permuted-block randomization. "
    "Before any participants arrive, a sequence of permuted blocks is pre-generated, where each block "
    "contains six treatment slots [c1, c2, c3, c3, c4, c4] in shuffled order. As participant pairs "
    "form on a first-in-first-out (FIFO) basis, each pair draws its treatment assignment sequentially "
    "from this pre-generated queue. This ensures near-perfect balance across conditions within every "
    "six consecutive pairs, preventing the finite-sample imbalance that pure random assignment would allow. "
    "Conditions 1 and 2 (human-opponent) each receive 1/6 of participant pairs, while conditions 3 and 4 "
    "(AI-opponent) each receive 2/6 of participant pairs. The condition assignment persists for the "
    "entire session — the same pair plays both the Prisoner's Dilemma and the Stag Hunt under the "
    "same treatment."
)

# 344-47: Procedures — fix duration, add orphan path
UPDATES["344-47"] = (
    "Participants are recruited in the Behavioral Political Economy Lab at Stony Brook University. "
    "Sessions last approximately 25–35 minutes. Participants receive $7.00 for completing the study "
    "plus a performance-based bonus of up to $5.00. The bonus is determined by game outcomes: "
    "participants play two games (Prisoner's Dilemma and Stag Hunt), and one game is randomly selected "
    "at the end to determine the bonus payment. The study is approved by the Stony Brook University "
    "Institutional Review Board. No deception is used: participants in AI conditions are explicitly "
    "informed that a live ChatGPT agent is playing on behalf of the other participant.\n\n"
    "Session flow: After consenting, all participants enter a synchronized start gate (a 2-digit code "
    "announced by the experimenter). Participants first complete an independent task run by a separate "
    "research team, then enter a partner-matching waiting room (timeout: 3 minutes). Matched pairs "
    "proceed to the Prisoner's Dilemma and Stag Hunt in sequence, followed by a post-game survey, "
    "results, and debriefing. Participants who are not matched with a partner within the waiting-room "
    "timeout complete a hypothetical strategy-method version of the cooperation games (no real payoffs) "
    "as a filler task before proceeding to the survey; these participants are excluded from "
    "confirmatory analyses.\n\n"
    "Eligibility criteria: English-speaking adults aged 18 or older."
)

# 344-62: Outcomes — fix trust variable name, add belief measures as confirmatory
UPDATES["344-62"] = (
    "Primary outcome measures:\n"
    "- cooperate (app_prisoner): Binary (True/False) choice in Game 1 (Prisoner's Dilemma), "
    "where True = cooperate (Choice B) and False = defect (Choice A). "
    "Referred to as prisoner_decision (coded 1/0) in the analysis dataset.\n"
    "- cooperate (app_stag): Binary (True/False) choice in Game 2 (Stag Hunt), "
    "where True = cooperate (Choice B) and False = defect (Choice A). "
    "Referred to as stag_decision (coded 1/0) in the analysis dataset.\n\n"
    "Trust measure:\n"
    "- trust_ai_bot: 5-point scale (\"Very Trustworthy\", \"Somewhat Trustworthy\", "
    "\"Neither Trustworthy nor Untrustworthy\", \"Somewhat Untrustworthy\", \"Very Untrustworthy\"). "
    "Mapped to numeric values: Very Untrustworthy = 1, Somewhat Untrustworthy = 2, "
    "Neither = 3, Somewhat Trustworthy = 4, Very Trustworthy = 5. "
    "Referred to as trust_num in the analysis dataset.\n\n"
    "Perception Likert items (5-point scale: Strongly Agree to Strongly Disagree, coded 5 to 1):\n"
    "- intentions: The opponent had good/clear intentions.\n"
    "- mind_of_its_own: The opponent has a mind of its own.\n"
    "- honest: The opponent is honest.\n"
    "- selfish: The opponent is selfish.\n"
    "- sincere: The opponent is sincere.\n"
    "- unbiased: The opponent is unbiased.\n\n"
    "Belief measures (confirmatory):\n"
    "- chose_B_game1: Belief about whether the opponent chose B in Game 1 (Prisoner's Dilemma).\n"
    "- chose_B_game2: Belief about whether the opponent chose B in Game 2 (Stag Hunt).\n"
    "These are analyzed as separate DVs with their own ANOVA (see Analysis Plan).\n\n"
    "Additional measures collected but not part of confirmatory analyses: "
    "demographic information, political views, AI attitudes, and comprehension check accuracy."
)

# 344-71: Analysis plan — drop Bayesian, add LPM, add belief ANOVA
UPDATES["344-71"] = (
    "The following statistical models will be used, corresponding to each confirmatory hypothesis. "
    "Because treatment is randomized at the pair level and both members of a human-opponent pair "
    "contribute data, observations are nested within pairs. Regression models account for this "
    "non-independence using multilevel (mixed-effects) models with a random intercept for pair. "
    "We report both separate models (one per game) and pooled models (combining PD and SH observations). "
    "This approach mirrors the analysis strategy used in Study 2 (registered as zux2b on OSF).\n\n"

    "1. Prisoner's Dilemma cooperation — separate model (H1, H2, H3):\n"
    "   - One-way ANOVA: prisoner_decision ~ treatment (4 levels: conditions 1–4)\n"
    "   - Tukey HSD post-hoc pairwise comparisons across all treatment pairs\n"
    "   - Two-way factorial ANOVA: prisoner_decision ~ opponent_type * communication, "
    "to formally test the interaction (H3)\n"
    "   - Mixed-effects linear probability model (LPM): "
    "prisoner_decision ~ opponent_type + communication + opponent_type:communication + (1 | pair)\n"
    "   - Report: F statistic, degrees of freedom, p-value, and eta-squared for ANOVAs; "
    "coefficients, z-statistics, p-values, and 95% CIs for regression; Hedges' g for pairwise comparisons\n\n"

    "2. Stag Hunt cooperation — separate model (H1, H2, H3):\n"
    "   - One-way ANOVA: stag_decision ~ treatment (4 levels: conditions 1–4)\n"
    "   - Tukey HSD post-hoc pairwise comparisons across all treatment pairs\n"
    "   - Two-way factorial ANOVA: stag_decision ~ opponent_type * communication, "
    "to formally test the interaction (H3)\n"
    "   - Mixed-effects linear probability model (LPM): "
    "stag_decision ~ opponent_type + communication + opponent_type:communication + (1 | pair)\n"
    "   - Report: as above\n\n"

    "3. Cooperation — pooled model (H1, H2, H3):\n"
    "   - Pool PD and SH observations (two observations per participant, one per game). "
    "Mixed-effects linear probability model: "
    "cooperation ~ opponent_type + communication + opponent_type:communication + game_type + "
    "(1 + game_type | pair), with a random intercept for pair and random slope for game type\n"
    "   - This pooled specification increases power and tests whether effects are consistent "
    "across game types. It yields N = 800 observations (400 human participants × 2 games each), "
    "nested within approximately 300 pairs.\n"
    "   - If the random-slope model fails to converge, the fallback is a random-intercept-only model: "
    "cooperation ~ opponent_type + communication + opponent_type:communication + game_type + (1 | pair)\n"
    "   - Report: coefficients with 95% CIs, z-statistics, p-values\n\n"

    "4. Trust (H4):\n"
    "   - Welch's t-test comparing trust_num between the HH group (conditions 1 and 2) "
    "and the AIH group (conditions 3 and 4)\n"
    "   - One-way ANOVA: trust_num ~ treatment (4 levels) with Tukey HSD post-hoc comparisons\n"
    "   - Linear mixed model: trust_num ~ opponent_type + communication + "
    "opponent_type:communication + (1 | pair)\n"
    "   - Report: t statistic, degrees of freedom, p-value, and Cohen's d for the t-test; "
    "F, df, p, and eta-squared for the ANOVA; regression coefficients with 95% CIs\n\n"

    "5. Agentic perception scale (H5):\n"
    "   - Welch's t-test comparing ai_agentic_scale between the HH group and the AIH group\n"
    "   - Linear mixed model: ai_agentic_scale ~ opponent_type + communication + "
    "opponent_type:communication + (1 | pair)\n"
    "   - Report: t statistic, degrees of freedom, p-value, and Cohen's d; "
    "regression coefficients with 95% CIs\n\n"

    "6. Honest/Fair perception scale (H5):\n"
    "   - Welch's t-test comparing ai_honest_fair_scale between the HH group and the AIH group\n"
    "   - Linear mixed model: ai_honest_fair_scale ~ opponent_type + communication + "
    "opponent_type:communication + (1 | pair)\n"
    "   - Report: t statistic, degrees of freedom, p-value, and Cohen's d; "
    "regression coefficients with 95% CIs\n\n"

    "7. Conditional cooperation beliefs (confirmatory DV):\n"
    "   - One-way ANOVA: chose_B_game1 ~ treatment (4 levels) with Tukey HSD post-hoc comparisons\n"
    "   - One-way ANOVA: chose_B_game2 ~ treatment (4 levels) with Tukey HSD post-hoc comparisons\n"
    "   - Report: F, df, p, eta-squared; pairwise Hedges' g with 95% CIs\n\n"

    "All analyses use Python (pingouin for ANOVAs and t-tests, statsmodels for mixed-effects models). "
    "HH group = conditions 1 and 2; AIH group = conditions 3 and 4. "
    "Analyses are conducted on active human players only (bot-seat participants excluded)."
)

# 344-77: Inference — remove Bayesian sentence
UPDATES["344-77"] = (
    "All hypotheses are directional and tested one-tailed with a significance threshold of alpha = 0.05. "
    "For ANOVAs (which are inherently omnibus/non-directional), we use the standard two-tailed F-test "
    "at alpha = 0.05, with directional predictions evaluated through the planned post-hoc comparisons "
    "and regression coefficients. For t-tests and regression coefficients, one-tailed p-values are used "
    "in the predicted direction. Effect sizes are reported as eta-squared for ANOVAs, Cohen's d for "
    "t-tests, and Hedges' g for pairwise comparisons. 95% confidence intervals are reported for all "
    "group means and effect size estimates."
)

# 344-79: Exclusions — drop comprehension covariate, add bot-seat, operationalize dropout
UPDATES["344-79"] = (
    "The following participants are excluded from all confirmatory analyses:\n\n"
    "1. Timeout exclusions: Participants who are not matched with a partner within the 3-minute "
    "waiting-room timeout (identified by the timed_out_from_coord_games flag in the dataset). "
    "These participants complete a hypothetical strategy-method filler task instead of the live games.\n\n"
    "2. Mid-game dropout: Participants who are matched but fail to complete both games "
    "(identified by a missing cooperate value on either app_prisoner or app_stag). "
    "If a participant completes Game 1 but drops out before Game 2, both of their observations "
    "are excluded. The matched partner's data is retained if their own responses are complete.\n\n"
    "3. Bot-seat participants: In AI-opponent conditions (c3, c4), the passive participant on whose "
    "behalf ChatGPT plays is excluded. These are identified by the player_bot flag in the dataset.\n\n"
    "No outlier exclusion criteria are applied. Comprehension check accuracy is reported descriptively "
    "(pass rates by condition) but is not used as a covariate or exclusion criterion. "
    "Data on the ChatGPT agent's choices and messages is collected but is secondary to the analysis "
    "of human behavior."
)

# 344-75: Transformations — fix trust variable name
UPDATES["344-75"] = (
    "The following transformations are applied to prepare the raw data for analysis. "
    "The analysis dataset contains only active human players (bot-seat participants and "
    "AI bot records are excluded).\n\n"
    "1. Variable renaming: The oTree database fields are mapped to analysis variable names:\n"
    "   - app_prisoner.player.cooperate → prisoner_decision (1 = True/cooperate, 0 = False/defect)\n"
    "   - app_stag.player.cooperate → stag_decision (1 = True/cooperate, 0 = False/defect)\n"
    "   - app_survey.player.trust_ai_bot → trust_num (see recoding below)\n\n"
    "2. Treatment coding: Treatment condition labels (\"condition_1\" through \"condition_4\") "
    "are mapped to numeric codes 1–4.\n\n"
    "3. Factor coding: Two binary indicators are derived from the treatment variable:\n"
    "   - opponent_type: 0 = Human (conditions 1, 2), 1 = AI (conditions 3, 4)\n"
    "   - communication: 0 = None (conditions 1, 3), 1 = Free-text (conditions 2, 4)\n\n"
    "4. Group assignment: Participants are assigned to one of two groups for aggregate comparisons:\n"
    "   - HH group: conditions 1 and 2 (human opponent)\n"
    "   - AIH group: conditions 3 and 4 (AI opponent)\n\n"
    "5. Trust recoding: The trust_ai_bot field stores string labels. These are mapped to a numeric scale:\n"
    "   Very Untrustworthy = 1, Somewhat Untrustworthy = 2, Neither Trustworthy nor Untrustworthy = 3, "
    "Somewhat Trustworthy = 4, Very Trustworthy = 5\n\n"
    "6. Reverse coding: The selfish perception item is reverse-coded as selfish_rev = 6 - selfish, "
    "so that higher values indicate less selfish (i.e., more fair) perceptions, consistent with "
    "the direction of the other honest/fair scale items.\n\n"
    "7. Scale construction: Two composite indices are computed from perception items as specified "
    "in the Indices section (q16):\n"
    "   - ai_agentic_scale = (intentions + mind_of_its_own) / 2\n"
    "   - ai_honest_fair_scale = (selfish_rev + honest + unbiased + sincere) / 4\n\n"
    "No other variable transformations, standardizations, or normalizations are applied."
)

# 344-83: Exploratory — remove belief measures (now confirmatory), keep comprehension as moderator
UPDATES["344-83"] = (
    "Exploratory analyses may include:\n\n"
    "(1) AI attitudes and their correlates with cooperation by condition.\n\n"
    "(2) Demographic and political correlates of cooperation.\n\n"
    "(3) Comprehension check accuracy as a moderator of treatment effects.\n\n"
    "(4) Exploratory text analysis of free-text messages in communication conditions (c2 and c4). "
    "This analysis is designed to complement the confirmatory hypotheses by examining whether "
    "message content explains, mediates, or qualifies the main treatment effects. Both human-authored "
    "and ChatGPT-generated messages are analyzed symmetrically using two approaches: "
    "dictionary-based classification and sentence embeddings.\n\n"
    "  (a) Robustness of treatment effects controlling for message content (H1, H2, H3): "
    "Extract message-level features — cooperative intent (dictionary-coded), sentiment, and semantic "
    "representations (sentence embeddings from a pretrained model) — and include them as covariates "
    "in the main LPM models for prisoner_decision and stag_decision. If treatment effects on cooperation "
    "persist after controlling for message content, the results are robust to communication differences. "
    "If treatment effects are attenuated, message content is a candidate mechanism.\n\n"
    "  (b) Are AI and human messages substantively different? (H2, H3): Compare messages sent in c2 "
    "(human-human) versus c4 (human-AI) on cooperative intent (dictionary classification), semantic "
    "content (cosine distances between human and ChatGPT message embedding distributions), and surface "
    "features (length, sentiment). If messages are substantively similar across conditions, any cooperation "
    "difference between c2 and c4 cannot be attributed to what was communicated — it reflects who "
    "communicated it.\n\n"
    "  (c) Intent-behavior consistency by opponent type (H2 mechanism): Code messages for revealed "
    "cooperative intent (e.g., explicit statements of intent to cooperate, appeals to mutual benefit). "
    "Compute the rate at which stated cooperative intent is followed by actual cooperation (choosing B), "
    "separately for c2 and c4. Compare intent-behavior consistency rates across conditions.\n\n"
    "  (d) Cross-game conditioning: Game 1 messages predicting Game 2 behavior: Messages exchanged before "
    "the Prisoner's Dilemma (Game 1) reveal cooperative intent prior to the Stag Hunt (Game 2). Test "
    "whether PD-round message content (intent classification, embeddings) predicts SH cooperation, "
    "controlling for the PD outcome.\n\n"
    "  Methods: (i) Dictionary-based classification: code messages for cooperative intent (cooperative, "
    "competitive, neutral), promise/commitment language, and strategic vs. prosocial framing using "
    "predefined keyword lists and rules. (ii) Sentence embeddings: encode messages using a pretrained "
    "language model to capture semantic content; use embedding representations for cosine similarity "
    "comparisons across conditions, clustering, and as covariates in regression models. Both methods "
    "are applied to human and ChatGPT messages identically.\n\n"
    "(5) Analysis of ChatGPT agent behavior: descriptive analysis of the bot's choices and message "
    "content across conditions, treated as secondary to the human behavioral data."
)

# 344-86: Other — add communication flow detail, remove PyStan
UPDATES["344-86"] = (
    "AI Agent Details: In conditions 3 and 4, a live instance of ChatGPT acts as the opponent on "
    "behalf of the bot-seat participant. ChatGPT is not pre-programmed with fixed responses; it receives "
    "the same game instructions, payoff information, and context (including any exchanged messages in "
    "communication conditions) as the human participant, and it reasons through the situation and submits "
    "a choice in real time during the experiment.\n\n"
    "Communication Flow: In communication conditions (c2, c4), participants first see a preamble page "
    "explaining the communication round. Each player then independently composes a free-text message "
    "(up to 50 words, validated server-side). In condition 4, the ChatGPT agent's message is generated "
    "via a live API call. After both messages are submitted, a synchronization wait page ensures "
    "simultaneity, and both messages are displayed together on a shared screen before the decision page. "
    "This process repeats for each game (PD and SH).\n\n"
    "No Deception: Participants in AI conditions are explicitly informed — via a dedicated information "
    "page shown before the game instructions — that a live ChatGPT agent is making decisions on behalf "
    "of the other participant. Participants in human conditions interact with a real human partner.\n\n"
    "Payoff Matrices:\n"
    "Prisoner's Dilemma (Game 1):\n"
    "- Both choose A: $2.50 each\n"
    "- Both choose B: $3.50 each\n"
    "- You choose A, Other chooses B: You get $5.00, Other gets $1.00\n"
    "- You choose B, Other chooses A: You get $1.00, Other gets $5.00\n\n"
    "Stag Hunt (Game 2):\n"
    "- Both choose A: $2.50 each\n"
    "- Both choose B: $5.00 each\n"
    "- You choose A, Other chooses B: You get $3.50, Other gets $1.00\n"
    "- You choose B, Other chooses A: You get $1.00, Other gets $3.50\n\n"
    "One game is randomly selected at the end to determine the bonus payment.\n\n"
    "Software: The experiment is implemented using oTree (open-source platform for behavioral research). "
    "Statistical analyses are conducted in Python using pingouin and statsmodels."
)

# description: remove Bayesian mention
UPDATES["description"] = (
    "This preregistration describes a lab-based experiment to be conducted at the Behavioral Political "
    "Economy Lab at Stony Brook University. The study investigates how opponent type (human vs. live "
    "ChatGPT agent) and pre-decision free-text communication affect cooperation in two sequential "
    "economic games: a Prisoner's Dilemma and a Stag Hunt. Using a 2×2 between-subjects design with "
    "approximately 400 human participants, the experiment tests directional hypotheses about the effects "
    "of AI opponents and communication on cooperative behavior, trust, and perceptions of the opponent. "
    "The analysis plan includes frequentist ANOVAs with Tukey HSD post-hoc tests and multilevel "
    "mixed-effects linear probability models accounting for pair-level clustering. "
    "Exploratory analyses include text analysis of free-text messages using dictionary-based "
    "classification and sentence embeddings. This study is a follow-up to Study 2 (OSF registration "
    "zux2b), transitioning from online (MTurk) recruitment with structured message menus to in-person "
    "lab sessions with free-form text communication and a live ChatGPT opponent."
)

# tags: fix "Stag Hung" typo
UPDATES["tags"] = [
    "AI Agents",
    "AI Attitudes",
    "Communication",
    "Economic Experiments",
    "Prisoners' Dilemma",
    "Social Dilemmas",
    "Stag Hunt",
]


def main():
    client = OSFClient()

    # Separate registration_responses fields from top-level attributes
    reg_response_keys = {k for k in UPDATES if k.startswith("344-")}
    top_level_keys = set(UPDATES) - reg_response_keys

    # Update registration_responses via registration_metadata
    if reg_response_keys:
        registration_responses = {k: UPDATES[k] for k in sorted(reg_response_keys)}
        print(f"Updating {len(registration_responses)} registration response fields...")
        result = client.update_draft_registration(
            DRAFT_ID,
            registration_responses=registration_responses,
        )
        print(f"  ✓ registration_responses updated (datetime_updated: {result['attributes']['datetime_updated']})")

    # Update top-level attributes (description, tags)
    if top_level_keys:
        top_attrs = {k: UPDATES[k] for k in sorted(top_level_keys)}
        print(f"Updating top-level attributes: {list(top_attrs.keys())}...")
        result = client.update_draft_registration(DRAFT_ID, **top_attrs)
        print(f"  ✓ top-level attributes updated (datetime_updated: {result['attributes']['datetime_updated']})")

    print("\nDone. Fetching updated draft to verify...")

    # Re-fetch and verify
    updated = client.get_draft_registration(DRAFT_ID)
    attrs = updated["attributes"]
    responses = attrs.get("registration_responses", {})

    print(f"\nVerification:")
    print(f"  Title: {attrs['title']}")
    print(f"  Tags: {attrs.get('tags', [])}")
    print(f"  Updated: {attrs['datetime_updated']}")

    errors = []
    for key in sorted(reg_response_keys):
        remote_val = responses.get(key, "")
        expected = UPDATES[key]
        if remote_val == expected:
            print(f"  ✓ {key} matches")
        else:
            # Check first 80 chars for quick diagnostics
            print(f"  ✗ {key} MISMATCH")
            print(f"    Expected starts: {expected[:80]}...")
            print(f"    Got starts:      {str(remote_val)[:80]}...")
            errors.append(key)

    if attrs.get("description", "") == UPDATES.get("description", ""):
        print(f"  ✓ description matches")
    else:
        print(f"  ✗ description MISMATCH")
        errors.append("description")

    if attrs.get("tags", []) == UPDATES.get("tags", []):
        print(f"  ✓ tags matches")
    else:
        print(f"  ✗ tags MISMATCH")
        errors.append("tags")

    if errors:
        print(f"\n⚠ {len(errors)} field(s) did not match after update: {errors}")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(UPDATES)} fields verified successfully.")


if __name__ == "__main__":
    main()
