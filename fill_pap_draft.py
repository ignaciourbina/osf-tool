#!/usr/bin/env python3
"""Fill in the OSF Pre-Analysis Plan for the
Trait Aggression & Far-Right Voting project.

Scope: BR 2023 and US 2024 original datasets only.
Status: Data collected, not yet analyzed.

Usage:
    python fill_pap_draft.py [--output OUTPUT.docx]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from osf_workflow import parse_osf_form, write_osf_form_to_docx, VersionManager

OSF_TEMPLATE = Path(__file__).resolve().parent.parent / "OSF Preregistration.docx"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "PAP_Trait_Aggression_DRAFT.docx"
VERSIONS_DIR = Path(__file__).resolve().parent / "versions"

# ── Field content ───────────────────────────────────────────────────────

TITLE = (
    "Trait Aggression Predicts Vote Choice for Far-Right Candidates: "
    "Evidence from the United States and Brazil"
)

DESCRIPTION = (
    "This study tests whether trait aggression — a stable personality disposition "
    "toward hostile cognition, affect, and behavior — predicts vote choice for "
    "populist far-right candidates. We leverage two independent survey samples "
    "spanning two countries: the United States (N = 933, 2024 presidential election) "
    "and Brazil (N = 1,004, 2022 presidential election). The outcome is binary vote "
    "choice for the far-right candidate (Donald Trump in the US; Jair Bolsonaro in "
    "Brazil). Both datasets include the identical 12-item Buss-Perry Aggression "
    "Questionnaire (short form). We first validate the trait aggression measurement "
    "model via confirmatory factor analysis, then estimate a series of logistic "
    "regression models testing whether trait aggression predicts far-right vote "
    "choice controlling for demographics, political attitudes, and competing "
    "predispositions. We further test (a) whether specific aggression subdimensions "
    "drive the effect and (b) whether trait aggression operates through partisan "
    "sorting or has a direct effect on vote choice via structural mediation. Each "
    "sample is analyzed independently; substantive conclusions are compared "
    "qualitatively across countries."
)

CONTRIBUTORS = (
    "[Author names redacted for blinded preregistration]"
)

HYPOTHESES = (
    "H1 (Global effect): Individuals higher in trait aggression are more likely "
    "to vote for far-right candidates (Trump in the US, Bolsonaro in Brazil), "
    "controlling for demographics, political interest, institutional trust, and "
    "(in the US) social dominance orientation, need for chaos, and ideology.\n\n"
    "H2 (Direct effect above partisanship): The effect of trait aggression on "
    "far-right vote choice persists after controlling for partisan affect "
    "(leader feeling thermometer differences in Brazil; expressive partisanship "
    "in the US), indicating a direct candidate-appeal pathway beyond partisan "
    "sorting.\n\n"
    "H3 (Subdimension specificity): Among the four Buss-Perry aggression "
    "dimensions (physical aggression, verbal aggression, hostility, anger), "
    "hostility and anger are the primary drivers of far-right vote choice, "
    "consistent with the hostility-anger-action mechanism.\n\n"
    "H4 (Partisan mediation): Trait aggression partially operates through "
    "partisan sorting — higher trait aggression predicts stronger affective "
    "alignment with the far-right side, which in turn predicts vote choice. "
    "The proportion mediated is expected to be larger in the US (where party ID "
    "is a stronger identity) than in Brazil (where partisan attachment is more "
    "personalist).\n\n"
    "All hypotheses are directional: higher trait aggression → higher probability "
    "of far-right vote choice. Each hypothesis is tested independently in each "
    "sample."
)

STUDY_TYPE = (
    "Observational Study - Data is collected from study subjects that are not "
    'randomly assigned to a treatment. This includes surveys, "natural '
    'experiments," and regression discontinuity designs.'
)

BLINDING = {
    "No blinding is involved in this study.": True,
    "For studies that involve human subjects, they will not know the treatment group to which they have been assigned.": False,
    'Personnel who interact directly with the study subjects (either human or non-human subjects) will not be aware of the assigned treatments. (Commonly known as "double blind")': False,
    "Personnel who analyze the data collected from the study are not aware of the treatment applied to any given group.": False,
}

ADDITIONAL_BLINDING = (
    "This is a purely observational study using cross-sectional survey data. "
    "No experimental manipulation or blinding is involved in the analyses "
    "covered by this pre-analysis plan. (The US 2024 survey includes an "
    "embedded experiment administered after the main survey battery; those "
    "experimental analyses are not part of this registration.)"
)

STUDY_DESIGN = (
    "Cross-sectional observational design. Two independent survey samples each "
    "measure trait aggression and vote choice for far-right candidates. Each "
    "sample is analyzed independently; cross-country consistency of substantive "
    "conclusions is assessed qualitatively.\n\n"
    "- Brazil 2023 (N = 1,004): Retrospective self-reported vote for Bolsonaro "
    "in the 2022 second-round presidential election. Collected October 2023 via "
    "Opinion Box (online panel), approximately one year after the election.\n\n"
    "- US 2024 (N = 933): Prospective vote intention for the 2024 presidential "
    "election. Collected October 2024 via Connect (cloud research platform), "
    "weeks before the November 2024 election.\n\n"
    "Each country uses the best available controls given its questionnaire. We "
    "do not force variable harmonization across countries — instead, we estimate "
    "the strongest possible model for each and compare the direction, significance, "
    "and magnitude of trait aggression effects."
)

RANDOMIZATION = (
    "Not applicable. This is a purely observational study with no experimental "
    "manipulation or random assignment."
)

EXISTING_DATA = (
    "Registration prior to analysis of the data: As of the date of submission, "
    "the data exist and you have accessed it, though no analysis has been "
    "conducted related to the research plan (including calculation of summary "
    "statistics). A common situation for this scenario when a large dataset "
    "exists that is used for many different studies over time, or when a data "
    "set is randomly split into a sample for exploratory analyses, and the "
    "other section of data is reserved for later confirmatory data analysis."
)

EXPLANATION_EXISTING_DATA = (
    "Both datasets have been collected and cleaned, but no hypothesis-testing "
    "analyses have been performed. Specifically:\n\n"
    "- Brazil 2023: Collected October 2023 via Opinion Box. Data cleaned and "
    "codebook prepared. No regressions, correlations, or descriptive analyses "
    "of aggression-vote relationships have been run.\n\n"
    "- US 2024: Collected October 2024 via Connect. Data cleaned, variables "
    "reverse-coded, and codebook prepared. No analysis conducted.\n\n"
    "Data cleaning operations performed to date: variable renaming, reverse-coding "
    "of Likert items for trait aggression, construction of binary vote-choice "
    "indicators, and demographic variable recoding. These operations are "
    "documented in codebooks and replication scripts but involve no examination "
    "of bivariate or multivariate relationships between aggression and vote choice."
)

DATA_COLLECTION_PROCEDURES = (
    "Brazil 2023: 1,004 Brazilian adults recruited via Opinion Box, an online "
    "survey panel. Inclusion criteria: age >= 18, Brazilian resident. The survey "
    "was fielded in Portuguese in October 2023, approximately one year after "
    "the 2022 presidential election second round. The vote-choice question asks "
    "respondents to recall their actual vote.\n\n"
    "US 2024: 933 US adults recruited via Connect (cloud research platform). "
    "Inclusion criteria: age >= 18, US resident. Fielded in October 2024, weeks "
    "before the November 2024 presidential election. The vote-choice question "
    "asks about intended vote. The survey includes an attention check (slider "
    "task requiring response between 70-80).\n\n"
    "Both surveys include the identical 12-item Buss-Perry Aggression "
    "Questionnaire (short form) with 6-point Likert response scales."
)

SAMPLE_SIZE = (
    "- Brazil 2023: N = 1,004\n"
    "- US 2024: N = 933\n\n"
    "Each sample is analyzed independently. No pooled analysis is planned."
)

SAMPLE_SIZE_RATIONALE = (
    "Sample sizes were determined by the original data collection budgets and "
    "platform constraints, not by a priori power analysis for this specific "
    "project. However, post-hoc sensitivity analysis will be reported. With "
    "N = 933 (smallest sample, US 2024) and a base rate of far-right vote "
    "choice of approximately 45%, logistic regression can detect odds ratios "
    "of 1.3 or larger for a standardized continuous predictor at alpha = .05, "
    "power = .80."
)

STOPPING_RULE = (
    "Data collection is complete. No sequential testing or adaptive stopping "
    "was employed. Both datasets were collected in full before any analysis "
    "was planned for this project."
)

MANIPULATED_VARIABLES = (
    "Not applicable. The analyses covered by this pre-analysis plan are "
    "purely observational. (The US 2024 survey includes an embedded "
    "experiment with 3 between-subjects conditions administered after the "
    "main survey battery; those experimental analyses are not part of this "
    "registration.)"
)

MEASURED_VARIABLES = (
    "PRIMARY OUTCOME VARIABLE:\n"
    "Vote choice for far-right candidate (binary: 1 = Trump/Bolsonaro, "
    "0 = other). Measured as retrospective vote (Brazil 2023) or prospective "
    "intention (US 2024).\n\n"
    "PRIMARY PREDICTOR:\n"
    "Trait aggression. Measured with the 12-item short form of the Buss-Perry "
    "Aggression Questionnaire (BAQ; Buss & Perry 1992) in both datasets. "
    "Response scale: 1 = Completely true for me ... 6 = Completely false for me. "
    "All 12 items are worded in the aggressive direction and are reverse-coded "
    "before analysis (score_rc = 7 - raw), so higher = more aggressive. "
    "Four subscales of 3 items each:\n"
    "- Physical Aggression (PA): items 1-3 "
    "(BR: PERGUNTA 8a_1-8a_3; US: aggr_1_1-aggr_1_3)\n"
    "- Verbal Aggression (VA): items 4-6 "
    "(BR: PERGUNTA 8a_4-8a_6; US: aggr_1_4-aggr_1_6)\n"
    "- Anger (A): items 7-9 "
    "(BR: PERGUNTA 8b_1-8b_3; US: aggr_2_1-aggr_2_3)\n"
    "- Hostility (H): items 10-12 "
    "(BR: PERGUNTA 8b_4-8b_6; US: aggr_2_4-aggr_2_6)\n\n"
    "MEDIATOR:\n"
    "Partisan affect, operationalized differently per country:\n"
    "- Brazil: Relative leader affect = Feeling(Bolsonaro) - Feeling(Lula), "
    "each on a 5-point scale (1 = hate, 5 = strong positive identification). "
    "No reverse coding — both items already coded in positive direction. "
    "Range: -4 to +4.\n"
    "- US: Expressive Partisanship = (PID7pt - 4) * feeling_4p, where PID7pt "
    "is the 7-point party identification scale (1 = Strong Democrat to "
    "7 = Strong Republican; centered: -3 to +3) and feeling_4p is the Q11 "
    "partisan importance slider (0-100) discretized into 4 levels "
    "(0-25 = 1, 26-50 = 2, 51-75 = 3, 76-100 = 4; inspired by "
    "Huddy et al. 2015). Range: -12 to +12. Pure independents = 0.\n\n"
    "CONTROL VARIABLES (BR 2023):\n"
    "- Age (continuous)\n"
    "- Gender (binary: male = 1, other = 0)\n"
    "- Education (ordinal)\n"
    "- Race (binary: white = 1, non-white = 0)\n"
    "- Political interest (BR: PERGUNTA 10; 4-point: 1 = Very interested, "
    "4 = Not at all interested; reverse-coded: score_rc = 5 - raw)\n"
    "- Institutional trust (mean of trust in National Congress + Judiciary; "
    "BR: PERGUNTA 15 items 3-4; 4-point: 1 = Very trustworthy, "
    "4 = Not at all trustworthy; reverse-coded: score_rc = 5 - raw)\n\n"
    "CONTROL VARIABLES (US 2024):\n"
    "- Age (continuous)\n"
    "- Gender (binary: male = 1, other = 0)\n"
    "- Education (ordinal)\n"
    "- Race (binary: white = 1, non-white = 0)\n"
    "- Political interest (US: Q15; 4-point: 1 = Very interested, "
    "4 = Not at all interested; reverse-coded: score_rc = 5 - raw)\n"
    "- Institutional trust (mean of trust in Congress + Courts; 5-point: "
    "1 = Not at all, 5 = A great deal; no reverse coding needed)\n"
    "- Social Dominance Orientation (SDO7, 8 items, 7-point; Ho et al. 2015; "
    "items 3, 4, 7, 8 reverse-coded: score_rc = 8 - raw)\n"
    "- Need for Chaos (7 items, 6-point; Petersen et al. 2023; "
    "all items reverse-coded: score_rc = 7 - raw)\n"
    "- Ideology (Q8; 7-point: 1 = Extremely Liberal to 7 = Extremely Conservative; "
    "no reverse coding)"
)

INDICES = (
    "Trait aggression global index: Mean of all 12 BAQ items after "
    "reverse-coding (score_rc = 7 - raw). Range: 1-6; higher = more aggressive. "
    "Both datasets.\n\n"
    "Trait aggression subscales: Mean of 3 reverse-coded items each for "
    "Physical Aggression (PA), Verbal Aggression (VA), Anger (A), and "
    "Hostility (H). Each subscale range: 1-6.\n\n"
    "SDO index: Mean of 8 SDO7 items after reverse-coding counter-dominance "
    "items 3, 4, 7, 8 (score_rc = 8 - raw). Range: 1-7; higher = more "
    "social dominance orientation. US 2024 only.\n\n"
    "Need for Chaos index: Mean of 7 reverse-coded items (score_rc = 7 - raw). "
    "Range: 1-6; higher = more need for chaos. US 2024 only.\n\n"
    "Political interest: Single reverse-coded item (score_rc = 5 - raw). "
    "Range: 1-4; higher = more interested. Both datasets.\n\n"
    "Institutional trust index: Mean of 2 items — trust in Congress/Legislature "
    "and Courts/Judiciary. BR: reverse-coded (score_rc = 5 - raw), range 1-4. "
    "US: no recoding, range 1-5. Higher = more trust in both datasets.\n\n"
    "Partisan affect (BR): Feeling(Bolsonaro) - Feeling(Lula). "
    "Range: -4 to +4; positive = pro-Bolsonaro.\n\n"
    "Expressive Partisanship (US): PID_centered * feeling_4p, where "
    "PID_centered = PID7pt - 4 (range: -3 to +3) and feeling_4p is the Q11 "
    "importance slider binned into 4 levels (0-25 = 1, 26-50 = 2, 51-75 = 3, "
    "76-100 = 4). Range: -12 to +12; positive = Republican-leaning. "
    "Follows the logic of Huddy et al. (2015) but uses a single-item proxy "
    "for partisan identity importance rather than their full 4-item scale.\n\n"
    "All non-binary variables are z-standardized (M = 0, SD = 1) within each "
    "sample before entry into regression models."
)

STATISTICAL_MODELS = (
    "STAGE 0 — MEASUREMENT VALIDATION:\n\n"
    "0A. Confirmatory Factor Analysis (CFA): 4-factor model for the 12-item "
    "Buss-Perry scale (PA, VA, H, A, 3 items each). Estimator: WLSMV (ordinal "
    "items). Fit indices: CFI, TLI, RMSEA, SRMR. Decision thresholds: "
    "acceptable fit = CFI/TLI >= .90 and RMSEA/SRMR <= .08; good fit = "
    "CFI/TLI >= .95 and RMSEA/SRMR <= .06 (Hu & Bentler 1999; Yu 2002). "
    "Compared against 1-factor and 2-factor alternatives via chi-square "
    "difference tests (lavTestLRT). If any latent factor pair correlates "
    "> .85, collapsing is considered.\n\n"
    "0B. Scale Reliability: Cronbach's alpha and McDonald's omega (hierarchical "
    "and total) for each subscale and the global 12-item scale.\n\n"
    "STAGE 1 — MAIN EFFECTS MODELS (logistic regression, binary vote DV):\n\n"
    "Model 1a (Global TA, no partisan controls):\n"
    "BR: logit(Vote_Bolsonaro) = TA_global + Demographics + Political_Interest "
    "+ Trust_Index\n"
    "US: logit(Vote_Trump) = TA_global + Demographics + Political_Interest "
    "+ Trust_Index + SDO + NfC + Ideology\n"
    "Key test: b_TA > 0. Report OR, 95% CI, McFadden pseudo-R2, AIC/BIC.\n\n"
    "Model 1b (Global TA, with partisan controls):\n"
    "BR: Model 1a + Partisan_Affect_BR (Feeling_Bolsonaro - Feeling_Lula)\n"
    "US: Model 1a + Expressive_PID\n"
    "Key comparison: Attenuation of TA coefficient from M1a to M1b. Report "
    "both raw logit coefficients and average marginal effects (AMEs) to address "
    "the logit rescaling problem.\n\n"
    "Model 2 (Subdimension model):\n"
    "Replace TA_global with four subscale means (PA, VA, H, A). Full controls "
    "as in M1b. Report VIFs for all focal predictors; if any VIF > 5, "
    "supplementary dominance analysis (Budescu 2003) is conducted and reported.\n\n"
    "STAGE 2 — STRUCTURAL MEDIATION (Model 3):\n\n"
    "SEM: TA_global --(a)--> Partisanship --(b)--> Vote_FarRight, with direct "
    "path c'. Partisanship = Partisan_Affect_BR (Brazil) or Expressive_PID (US). "
    "All Stage 1 controls enter as predictors of both mediator and outcome.\n"
    "Estimator: WLSMV. Bootstrap 95% CIs for indirect effect (bias-corrected, "
    "5,000 resamples). Report a-path, b-path, c'-path, indirect effect, "
    "proportion mediated, model fit (CFI, TLI, RMSEA, SRMR), and structural "
    "R2 adjusted for each equation.\n\n"
    "ROBUSTNESS CHECKS:\n"
    "1. Alternative DV: Restrict to major-candidate voters (Bolsonaro vs. Lula; "
    "Trump vs. Harris).\n"
    "2. Nonlinearity: Include TA^2 in Model 1a.\n"
    "3. Alternative partisan affect (BR only): Party feelings (PL - PT) instead "
    "of leader feelings.\n"
    "4. Measurement invariance: Configural, metric, and scalar invariance tests "
    "for the CFA across BR and US samples.\n"
    "5. Alternative partisan controls (US only): Re-estimate M1b-M3 with "
    "(a) standard 7-point Party ID alone and (b) PID7pt + Expressive_PID "
    "simultaneously, to test sensitivity to partisan operationalization."
)

TRANSFORMATIONS = (
    "1. Trait aggression items (BAQ, both surveys): All 12 items reverse-coded "
    "so higher values indicate greater aggression. Original scale: "
    "1 = Completely true for me, 6 = Completely false for me. "
    "Formula: score_rc = 7 - raw. After recoding: 1 = least aggressive, "
    "6 = most aggressive.\n\n"
    "2. SDO7 items 3, 4, 7, 8 (US 2024 only): Counter-dominance items "
    "reverse-coded so higher = more dominance-oriented. "
    "Formula: score_rc = 8 - raw. Items 1, 2, 5, 6 unchanged.\n\n"
    "3. Need for Chaos items (US 2024 only): All 7 items reverse-coded so "
    "higher values indicate greater need for chaos. Original scale: "
    "1 = Completely true for me, 6 = Completely false for me. "
    "Formula: score_rc = 7 - raw.\n\n"
    "4. Political interest (both surveys; BR: PERGUNTA 10, US: Q15): "
    "Reverse-coded so higher = more interested. Original scale: "
    "1 = Very interested, 4 = Not at all interested. "
    "Formula: score_rc = 5 - raw.\n\n"
    "5. Institutional trust (Brazil only; PERGUNTA 15 items 3-4): "
    "Reverse-coded so higher = more trust. Original scale: "
    "1 = Very trustworthy, 4 = Not at all trustworthy. "
    "Formula: score_rc = 5 - raw. US trust items already coded in positive "
    "direction (1 = Not at all, 5 = A great deal); no recoding applied.\n\n"
    "6. Expressive Partisanship construction (US 2024):\n"
    "   a. Discretize Q11 (0-100 partisan importance slider) into 4 levels: "
    "0-25 = 1, 26-50 = 2, 51-75 = 3, 76-100 = 4.\n"
    "   b. Center 7-point Party ID: PID_centered = PID7pt - 4 (range: -3 to +3).\n"
    "   c. Expressive_PID = PID_centered * feeling_4p (range: -12 to +12).\n"
    "   Pure independents receive 0 by construction.\n\n"
    "7. Partisan affect (BR 2023): Feeling_Bolsonaro - Feeling_Lula "
    "(range: -4 to +4). No recoding — both items coded in positive direction.\n\n"
    "8. All non-binary variables z-standardized (M = 0, SD = 1) within each "
    "sample before model estimation. Binary variables (gender, race, DV) left "
    "in original 0/1 coding.\n\n"
    "9. Binary vote choice: 1 = far-right candidate (Trump/Bolsonaro), "
    "0 = all other responses (including null/blank/other)."
)

INFERENCE_CRITERIA = (
    "Primary inference: Two-tailed tests at alpha = .05 for all confirmatory "
    "hypotheses. Effect sizes reported as odds ratios with 95% confidence "
    "intervals (logistic regression) and standardized coefficients (SEM).\n\n"
    "Average marginal effects (AMEs) reported alongside logit coefficients "
    "for all focal parameters to enable valid cross-model comparison (addressing "
    "the logit rescaling problem when comparing coefficients across nested "
    "models).\n\n"
    "Mediation inference: Bootstrap 95% confidence intervals (5,000 resamples, "
    "bias-corrected) for indirect effects. If the CI excludes zero, mediation "
    "is considered statistically supported.\n\n"
    "CFA model comparison: Chi-square difference tests (lavTestLRT with WLSMV "
    "estimator) comparing 1-factor, 2-factor, and 4-factor models.\n\n"
    "We will report exact p-values, confidence intervals, and effect sizes for "
    "all focal parameters regardless of statistical significance."
)

DATA_EXCLUSION = (
    "1. Respondents who did not complete the full 12-item trait aggression "
    "battery are excluded from all analyses.\n\n"
    "2. US 2024: Respondents who failed the attention check (slider response "
    "outside the 70-80 range on the dining-out frequency question) are "
    "excluded.\n\n"
    "3. Brazil 2023: Respondents who answered 'Don't remember' to the vote "
    "question are excluded from vote-choice models (retained in measurement "
    "validation analyses).\n\n"
    "4. No exclusion based on outlier values on continuous variables. "
    "Sensitivity analyses winsorizing at the 1st/99th percentiles will be "
    "reported."
)

MISSING_DATA = (
    "Item-level missingness on multi-item scales: If a respondent answered at "
    "least 75% of items in a scale (e.g., >= 9 of 12 aggression items), the "
    "index is computed as the mean of available items. Otherwise, the "
    "respondent is excluded from that analysis.\n\n"
    "Model-level missingness: Listwise deletion is used for regression models. "
    "As a sensitivity check, we will re-estimate Model 1a using multiple "
    "imputation (5 datasets, predictive mean matching) for any variable with "
    "> 5% missingness and report whether conclusions change."
)

EXPLORATORY_ANALYSIS = (
    "1. Heterogeneity by demographics: Estimate Model 1a separately by gender "
    "and by education terciles to examine whether the aggression-vote "
    "relationship varies across demographic subgroups.\n\n"
    "2. Interaction with SDO (US only): TA * SDO interaction to test whether "
    "trait aggression is more predictive at high vs. low social dominance "
    "orientation.\n\n"
    "3. Dose-response in partisan identity (US only): Examine whether the "
    "TA effect varies across levels of partisan identity strength (Q11) by "
    "estimating TA * feeling_4p interaction.\n\n"
    "These analyses are explicitly labeled as exploratory and will not be "
    "subject to multiple-comparison correction."
)

OTHER = (
    "Software: All analyses will be conducted in R with packages: lavaan "
    "(CFA, SEM), semTools (reliability, measurement invariance), psych (omega, "
    "descriptives), marginaleffects (AMEs), performance (VIF, model "
    "diagnostics). Bootstrap confidence intervals via lavaan's built-in "
    "bootstrapping.\n\n"
    "Replication code and data will be deposited on OSF upon publication.\n\n"
    "Ethics: The Brazil 2023 survey was approved by [IRB name redacted]. "
    "The US 2024 survey was approved by [IRB name redacted].\n\n"
    "Limitations noted in advance:\n"
    "- RWA (right-wing authoritarianism) is not available in either dataset. "
    "We cannot partial out authoritarianism as a competing predisposition.\n"
    "- SDO, Need for Chaos, and Ideology are available only in US 2024. "
    "The US models therefore provide a stronger test of TA's incremental "
    "validity over competing predispositions.\n"
    "- Brazil's vote-choice measure is retrospective (1 year post-election), "
    "introducing potential recall bias. This is a limitation that cannot be "
    "tested with the available data.\n\n"
    "Deviations from this plan will be transparently reported in the final "
    "manuscript with justification."
)


# ── Build and write ────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fill OSF PAP draft")
    parser.add_argument(
        "--output", "-o",
        default=str(DEFAULT_OUTPUT),
        help="Output .docx path",
    )
    parser.add_argument(
        "--template",
        default=str(OSF_TEMPLATE),
        help="Path to blank OSF Preregistration .docx template",
    )
    args = parser.parse_args()

    print(f"Parsing template: {args.template}")
    form = parse_osf_form(args.template)
    print(f"  -> {form.summary()}")

    # ── Fill fields ─────────────────────────────────────────────────

    form.edit_field("title", TITLE)
    form.edit_field("description", DESCRIPTION)
    form.edit_field("contributors", CONTRIBUTORS)
    form.edit_field("study_type", STUDY_TYPE)
    form.edit_field("blinding", BLINDING)
    form.edit_field("additional_blinding", ADDITIONAL_BLINDING)
    form.edit_field("study_design", STUDY_DESIGN)
    form.edit_field("randomization", RANDOMIZATION)
    form.edit_field("existing_data", EXISTING_DATA)
    form.edit_field("explanation_existing_data", EXPLANATION_EXISTING_DATA)
    form.edit_field("hypotheses", HYPOTHESES)
    form.edit_field("data_collection_procedures", DATA_COLLECTION_PROCEDURES)
    form.edit_field("sample_size", SAMPLE_SIZE)
    form.edit_field("sample_size_rationale", SAMPLE_SIZE_RATIONALE)
    form.edit_field("stopping_rule", STOPPING_RULE)
    form.edit_field("manipulated_variables", MANIPULATED_VARIABLES)
    form.edit_field("measured_variables", MEASURED_VARIABLES)
    form.edit_field("indices", INDICES)
    form.edit_field("statistical_models", STATISTICAL_MODELS)
    form.edit_field("transformations", TRANSFORMATIONS)
    form.edit_field("inference_criteria", INFERENCE_CRITERIA)
    form.edit_field("data_exclusion", DATA_EXCLUSION)
    form.edit_field("missing_data", MISSING_DATA)
    form.edit_field("exploratory_analysis", EXPLORATORY_ANALYSIS)
    form.edit_field("other", OTHER)

    dirty = [f for f in form.all_fields() if f.dirty]
    print(f"\n  Filled {len(dirty)} of {len(form.all_fields())} fields")

    # ── Write DOCX ──────────────────────────────────────────────────

    out_path = write_osf_form_to_docx(form, args.template, args.output)
    print(f"  Written to: {out_path}")

    # ── Save version snapshot ───────────────────────────────────────

    vm = VersionManager(VERSIONS_DIR)
    record = vm.save(form, "pap-draft-v3", "Enriched PAP: RC formulas for NfC/PolitInt/BRTrust, BAQ item-variable map, CFA fit thresholds, VIF>5 trigger")
    print(f"  Version saved: {record.label} -> {record.filepath}")

    # ── Print markdown preview ──────────────────────────────────────

    print("\n" + "=" * 72)
    print("MARKDOWN PREVIEW (first 3000 chars)")
    print("=" * 72)
    print(form.to_markdown()[:3000])
    print("...")


if __name__ == "__main__":
    main()
