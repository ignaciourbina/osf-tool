# Registration Memo

**Project:** Misperceptions of Immigrants on the Workforce: Unpacking Labor Market Concerns
**OSF Registration ID:** [nkbxf](https://osf.io/nkbxf)
**Registration Type:** OSF Preregistration
**Status:** Accepted (Public)
**Date Registered:** July 1, 2025
**Last Modified:** July 30, 2025
**Subject Area:** Social and Behavioral Sciences > Political Science > American Politics

## Contributors

| Name              | Role  | Permission |
|-------------------|-------|------------|
| Vitoria Sgorlon   | PI    | Admin      |
| Ignacio Urbina    | Co-PI | Write      |

---

## Study Overview

This study investigates how correcting misperceptions about immigrants in the labor force affects attitudes toward immigration. The core question: *does providing people with factual data about the number of immigrants in the workforce reduce perceived economic threat and increase support for pro-immigration policies?*

The design distinguishes between **egotropic** (personal/occupation-level) and **sociotropic** (national/state-level) information corrections, testing which level of factual information is more effective at shifting beliefs.

## Design

- **Type:** Between-subjects survey experiment (4 conditions)
- **Platform:** Qualtrics, recruited via Connect
- **Sample:** N = 1,950 U.S. adults aged 18-65, currently in the workforce
- **Compensation:** $1.60 (~12 min survey)
- **Blinding:** Participants do not know their treatment assignment
- **Data status:** Registration prior to creation of data

### Experimental Conditions

1. **Control** -- No factual correction; participants answer belief and outcome measures only
2. **Egotropic** -- Factual numbers of immigrants in the participant's occupation and job family
3. **Sociotropic** -- Factual numbers of immigrants at the national and state levels
4. **Socio-egotropic** -- All four levels of information combined (occupation, job family, national, state)

## Hypotheses

| # | Hypothesis | Direction |
|---|-----------|-----------|
| H1 | Treatment conditions reduce perceived economic threat vs. control | - threat |
| H2 | Treatment conditions increase pro-immigration policy support and positive attitudes vs. control | + support |
| H3 | Socio-egotropic condition shows the strongest effects (most information) | Socio-ego > others |
| H4 | Egotropic > Sociotropic for reducing economic threat (personal relevance) | Ego > Socio on threat |
| H5 | Sociotropic > Egotropic for policy support (national-level policies) | Socio > Ego on policy |
| H6 | Effects stronger for high numeracy, trait anxiety, trust, and economic anxiety | Positive moderation |
| H7 | Effects weaker for high status threat, cultural threat, and crime threat | Negative moderation |
| H8 | Effects weaker for Democrats (ceiling effect due to prior pro-immigration attitudes) | Ceiling |
| H9 | Effects stronger for individuals with greater initial misperceptions | Positive moderation |

## Outcome Variables

**Economic Threat** (pre- and post-treatment, 5-point scale):
- Sociotropic: "...makes it harder for people in the U.S. to find or keep a job"
- Egotropic: "...makes it harder for you personally to find or keep a job"

**Pro-Immigration Policy Support** (post-treatment, 7-point Likert, 5 items):
- Guest worker program support
- Path to legal status for unauthorized immigrants
- Path to citizenship for unauthorized immigrants
- Equal rights to social benefits (reverse-coded)
- Increased federal spending on immigrant financial assistance (reverse-coded)

**Attitudes Toward Immigrants** (post-treatment, 3 items):
- Economic contribution (5-point)
- Comfort with immigrant work colleague (5-point)
- Feeling thermometer (0-100)

## Moderators and Indices

- **Trait Anxiety Index** -- 4-item average (7-point scale)
- **Economic Anxiety Index** -- 3-item standardized average (5-point scales)
- **Numeracy Index** -- 3-item correct/incorrect sum
- **Trust in Information Source** -- single item (5-point)
- **Status Threat** -- single item (7-point)
- **Cultural Threat** -- single item (5-point)
- **Crime Threat** -- single item (5-point)
- **Party Identification** -- 7-point scale (Democrat vs. non-Democrat for H8)

Indices will be validated with confirmatory factor analysis.

## Analysis Plan

| Analysis | Method | Purpose |
|----------|--------|---------|
| Manipulation check | Paired t-tests (pre vs. post belief) within each group | Confirm treatment altered beliefs |
| H1, H2 (main effects) | OLS regression per outcome | Treatment vs. control coefficients |
| H3, H4, H5 (comparisons) | Post-estimation pairwise contrasts | Compare treatment condition coefficients |
| H6, H7, H8 (moderation) | OLS with interaction terms per moderator | Conditional effects + marginal effects at levels |
| H9 (overestimation) | OLS with Prior Overestimation Score x Treatment interaction | Stronger effects for larger misperceptions |
| Model assumption test | OLS on control group only | Economic threat predicts lower policy support |

All tests at p < 0.05. Non-preregistered analyses reported as exploratory.

---

*Memo generated on 2026-03-20 from OSF registration nkbxf.*
