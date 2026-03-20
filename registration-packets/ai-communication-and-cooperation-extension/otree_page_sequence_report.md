Project root: /home/ignacio/Dropbox/RESEARCH/Research-Pipeline-MASTER/001_AI_Cooperation/IRB_Rev_v6/experiment-versions/lab_open-msg/otree-aicoop-4.0-free_msg-v2026_03

Generated at (UTC): 2026-03-16T22:01:54+00:00

# Target Session Config

\- Experiment_wRAND_Cond_1_OR_2_OR_3_OR_4

\- app_sequence: \['app_consent', 'app_waiting', 'app_prisoner', 'app_stag', 'app_survey', 'app_collect_results', 'app_debriefing'\]

# Condition-Specific Sequences

## condition_1

app_consent: Consent_v2 -\> WaitingWarning

app_waiting: WaitForPartner -\> TimeOutPage

app_prisoner: GPWait -\> FirstInfoPage -\> Instruction -\> BotThinking -\> WaitForBotDecision -\> Decision -\> ResultsWaitPage -\> NextGameWarning

app_stag: GPWait -\> Instruction -\> BotThinking -\> WaitForBotDecision -\> Decision -\> ResultsWaitPage -\> GamesEnd

app_survey: Survey1 -\> Survey2 -\> Survey3 -\> Survey4 -\> Survey5 -\> Survey6

app_collect_results: CollectResults

app_debriefing: Debrief_Parent -\> End

## condition_2

app_consent: Consent_v2 -\> WaitingWarning

app_waiting: WaitForPartner -\> TimeOutPage

app_prisoner: GPWait -\> FirstInfoPage -\> Instruction -\> Preamble_Comm -\> Communication -\> CommWaitPage -\> ShowMessages -\> BotThinking -\> WaitForBotDecision -\> Decision -\> ResultsWaitPage -\> NextGameWarning

app_stag: GPWait -\> Instruction -\> Preamble_Comm -\> Communication -\> CommWaitPage -\> ShowMessages -\> BotThinking -\> WaitForBotDecision -\> Decision -\> ResultsWaitPage -\> GamesEnd

app_survey: Survey1 -\> Survey2 -\> Survey3 -\> Survey4 -\> Survey5 -\> Survey6

app_collect_results: CollectResults

app_debriefing: Debrief_Parent -\> End

## condition_3

app_consent: Consent_v2 -\> WaitingWarning

app_waiting: WaitForPartner -\> TimeOutPage

app_prisoner: GPWait -\> FirstInfoPage -\> Info_GPT -\> Instruction -\> BotThinking -\> WaitForBotDecision -\> Decision -\> ResultsWaitPage -\> NextGameWarning

app_stag: GPWait -\> Instruction -\> BotThinking -\> WaitForBotDecision -\> Decision -\> ResultsWaitPage -\> GamesEnd

app_survey: Survey1 -\> Survey2 -\> Survey3 -\> Survey4 -\> Survey5 -\> Survey6

app_collect_results: CollectResults

app_debriefing: Debrief_Parent -\> End

## condition_4

app_consent: Consent_v2 -\> WaitingWarning

app_waiting: WaitForPartner -\> TimeOutPage

app_prisoner: GPWait -\> FirstInfoPage -\> Info_GPT -\> Instruction -\> Preamble_Comm -\> Communication -\> BotComposing -\> CommWaitPage -\> ShowMessages -\> BotThinking -\> WaitForBotDecision -\> Decision -\> ResultsWaitPage -\> NextGameWarning

app_stag: GPWait -\> Instruction -\> Preamble_Comm -\> Communication -\> BotComposing -\> CommWaitPage -\> ShowMessages -\> BotThinking -\> WaitForBotDecision -\> Decision -\> ResultsWaitPage -\> GamesEnd

app_survey: Survey1 -\> Survey2 -\> Survey3 -\> Survey4 -\> Survey5 -\> Survey6

app_collect_results: CollectResults

app_debriefing: Debrief_Parent -\> End

# Per-App Page Gate Matrix

## app_consent

| Page           | is_displayed | Notes | condition_1 | condition_2 | condition_3 | condition_4 |
|----------------|--------------|-------|-------------|-------------|-------------|-------------|
| Consent_v2     | (none)       |       | Y           | Y           | Y           | Y           |
| WaitingWarning | (none)       |       | Y           | Y           | Y           | Y           |

## app_waiting

| Page           | is_displayed         | Notes                                                          | condition_1 | condition_2 | condition_3 | condition_4 |
|----------------|----------------------|----------------------------------------------------------------|-------------|-------------|-------------|-------------|
| WaitForPartner | not player.timed_out | Condition-agnostic runtime predicate (not treatment-specific). | Y           | Y           | Y           | Y           |
| TimeOutPage    | player.timed_out     | Condition-agnostic runtime predicate (not treatment-specific). | Y           | Y           | Y           | Y           |

## app_prisoner

| Page                  | is_displayed                                                                      | Notes                                                                                           | condition_1 | condition_2 | condition_3 | condition_4 |
|-----------------------|-----------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|-------------|-------------|-------------|-------------|
| GPWait                | (none)                                                                            |                                                                                                 | Y           | Y           | Y           | Y           |
| FirstInfoPage         | (none)                                                                            |                                                                                                 | Y           | Y           | Y           | Y           |
| DebuggingTemplatePage | C.SHOW_DEBUG_SCREEN                                                               |                                                                                                 | N           | N           | N           | N           |
| Info_GPT              | in_treatment(self, {TREATMENT_C3}) or in_treatment(self, {TREATMENT_C4})          |                                                                                                 | N           | N           | Y           | Y           |
| Instruction           | (none)                                                                            |                                                                                                 | Y           | Y           | Y           | Y           |
| Preamble_Comm         | in_treatment(self, {TREATMENT_C2}) or in_treatment(self, {TREATMENT_C4})          |                                                                                                 | N           | Y           | N           | Y           |
| Communication         | in_treatment(self, {TREATMENT_C2}) or in_treatment(self, {TREATMENT_C4})          |                                                                                                 | N           | Y           | N           | Y           |
| BotComposing          | player.is_bot and player.treatment_cond == TREATMENT_C4                           | Contains both treatment and non-treatment predicates; condition gating is projected statically. | N           | N           | N           | Y           |
| CommWaitPage          | in_treatment(player, {TREATMENT_C2, TREATMENT_C4}) and player.group.arrivals \< 2 | Contains both treatment and non-treatment predicates; condition gating is projected statically. | N           | Y           | N           | Y           |
| ShowMessages          | in_treatment(self, {TREATMENT_C2}) or in_treatment(self, {TREATMENT_C4})          |                                                                                                 | N           | Y           | N           | Y           |
| BotThinking           | player.is_bot                                                                     | Condition-agnostic runtime predicate (not treatment-specific).                                  | Y           | Y           | Y           | Y           |
| WaitForBotDecision    | player.treatment_cond in \[TREATMENT_C3, TREATMENT_C4\] and arrivals_3 \< 2       | Condition-agnostic runtime predicate (not treatment-specific).                                  | Y           | Y           | Y           | Y           |
| Decision              | (none)                                                                            |                                                                                                 | Y           | Y           | Y           | Y           |
| ResultsWaitPage       | player.group.arrivals_2 \< 2                                                      | Condition-agnostic runtime predicate (not treatment-specific).                                  | Y           | Y           | Y           | Y           |
| NextGameWarning       | (none)                                                                            |                                                                                                 | Y           | Y           | Y           | Y           |

## app_stag

| Page                  | is_displayed                                                                      | Notes                                                                                           | condition_1 | condition_2 | condition_3 | condition_4 |
|-----------------------|-----------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|-------------|-------------|-------------|-------------|
| GPWait                | (none)                                                                            |                                                                                                 | Y           | Y           | Y           | Y           |
| DebuggingTemplatePage | C.SHOW_DEBUG_SCREEN                                                               |                                                                                                 | N           | N           | N           | N           |
| Instruction           | (none)                                                                            |                                                                                                 | Y           | Y           | Y           | Y           |
| Preamble_Comm         | in_treatment(self, {TREATMENT_C2}) or in_treatment(self, {TREATMENT_C4})          |                                                                                                 | N           | Y           | N           | Y           |
| Communication         | in_treatment(self, {TREATMENT_C2}) or in_treatment(self, {TREATMENT_C4})          |                                                                                                 | N           | Y           | N           | Y           |
| BotComposing          | player.is_bot and player.treatment_cond == TREATMENT_C4                           | Contains both treatment and non-treatment predicates; condition gating is projected statically. | N           | N           | N           | Y           |
| CommWaitPage          | in_treatment(player, {TREATMENT_C2, TREATMENT_C4}) and player.group.arrivals \< 2 | Contains both treatment and non-treatment predicates; condition gating is projected statically. | N           | Y           | N           | Y           |
| ShowMessages          | in_treatment(self, {TREATMENT_C2}) or in_treatment(self, {TREATMENT_C4})          |                                                                                                 | N           | Y           | N           | Y           |
| BotThinking           | player.is_bot                                                                     | Condition-agnostic runtime predicate (not treatment-specific).                                  | Y           | Y           | Y           | Y           |
| WaitForBotDecision    | player.treatment_cond in \[TREATMENT_C3, TREATMENT_C4\] and arrivals_3 \< 2       | Condition-agnostic runtime predicate (not treatment-specific).                                  | Y           | Y           | Y           | Y           |
| Decision              | (none)                                                                            |                                                                                                 | Y           | Y           | Y           | Y           |
| ResultsWaitPage       | player.group.arrivals_2 \< 2                                                      | Condition-agnostic runtime predicate (not treatment-specific).                                  | Y           | Y           | Y           | Y           |
| GamesEnd              | (none)                                                                            |                                                                                                 | Y           | Y           | Y           | Y           |

## app_survey

| Page    | is_displayed                                        | Notes                                                          | condition_1 | condition_2 | condition_3 | condition_4 |
|---------|-----------------------------------------------------|----------------------------------------------------------------|-------------|-------------|-------------|-------------|
| Survey1 | (none)                                              |                                                                | Y           | Y           | Y           | Y           |
| Survey2 | (none)                                              |                                                                | Y           | Y           | Y           | Y           |
| Survey3 | (none)                                              |                                                                | Y           | Y           | Y           | Y           |
| Survey4 | (none)                                              |                                                                | Y           | Y           | Y           | Y           |
| Survey5 | (none)                                              |                                                                | Y           | Y           | Y           | Y           |
| Survey6 | not player.participant.vars.get('timed_out', False) | Condition-agnostic runtime predicate (not treatment-specific). | Y           | Y           | Y           | Y           |

## app_collect_results

| Page           | is_displayed                                        | Notes                                                          | condition_1 | condition_2 | condition_3 | condition_4 |
|----------------|-----------------------------------------------------|----------------------------------------------------------------|-------------|-------------|-------------|-------------|
| CollectResults | not player.participant.vars.get('timed_out', False) | Condition-agnostic runtime predicate (not treatment-specific). | Y           | Y           | Y           | Y           |

## app_debriefing

| Page           | is_displayed | Notes | condition_1 | condition_2 | condition_3 | condition_4 |
|----------------|--------------|-------|-------------|-------------|-------------|-------------|
| Debrief_Parent | (none)       |       | Y           | Y           | Y           | Y           |
| End            | (none)       |       | Y           | Y           | Y           | Y           |
