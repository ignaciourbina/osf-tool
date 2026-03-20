**Participant-Facing Page Content**

**Session config:** *Experiment_wRAND_Cond_1_OR_2_OR_3_OR_4*

*Generated: 2026-03-16*

**NOTE TO IRB REVIEWER — NOT DISPLAYED TO PARTICIPANTS**

# How to Read This Document

This document presents the participant-facing content for all pages in the experiment. Because the experiment uses a between-subjects 2×2 design, many pages are rendered differently depending on which treatment condition a participant is assigned to. The sections below explain the condition taxonomy and the annotation conventions used throughout this document.

## Experiment Structure

The experiment is built on oTree, an open-source web-based platform for conducting behavioral research. In oTree, an “app” is a self-contained module that handles one logical section of the study (e.g., the consent form, a game, or a survey). Each app is made up of one or more “pages” — individual screens that participants see in their web browser, implemented as HTML files. A page may display instructions, present a decision task, collect responses via form fields, or show feedback. oTree controls the order in which pages and apps are shown; participants cannot skip ahead or go back.

The experiment is structured as a sequential pipeline of apps. Participants move through every app in the order listed below; no app is skipped. Each app is presented as a separate section in this document, with each of its pages reproduced in full.

| **App**                 | **Role**                             | **Description**                                                                                                                                                                                                                  |
|-------------------------|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **app_consent**         | Consent form.                        | Presents the IRB-approved informed consent. Participants must click 'I agree to participate' to proceed; declining ends the session immediately.                                                                                 |
| **app_waiting**         | Participant matching / waiting room. | Holds participants in a waiting room while the platform matches them into pairs. Once a partner is found the treatment condition (c1–c4) is assigned. A timeout page is shown if no partner arrives within the allotted window.  |
| **app_prisoner**        | Game 1 — Prisoner's Dilemma.         | Participants are shown the payoff matrix and instructions for the Prisoner's Dilemma. In communication conditions (c2, c4) a message-exchange round precedes the choice screen. Payoffs: A=\$1.25, B=\$2.50, C=\$0.50, D=\$1.75. |
| **app_stag**            | Game 2 — Stag Hunt.                  | Structurally identical to app_prisoner but with the Stag Hunt payoff matrix. Payoffs: A=\$1.25, B=\$1.75, C=\$0.50, D=\$2.50.                                                                                                    |
| **app_survey**          | Post-game survey.                    | Collects demographic information and attitudinal measures (e.g. trust, risk preferences) from the human participant.                                                                                                             |
| **app_collect_results** | Results collection.                  | Aggregates each participant's game payoffs and generates a unique completion code used for in-lab completion verification and payment reconciliation.                                                                            |
| **app_debriefing**      | Debriefing and end of study.         | Reveals the study's purpose, explains how the bonus was calculated, and thanks the participant. The page shown depends on the assigned condition.                                                                                |

## Treatment Conditions

Participants are randomly assigned to one of four conditions that cross two factors: (1) whether the opponent is a human or an AI bot, and (2) whether a pre-decision communication round is included.

| **Condition**   | **Short label** | **Opponent type** | **Communication** |
|-----------------|-----------------|-------------------|-------------------|
| **condition_1** | c1              | Human             | No                |
| **condition_2** | c2              | Human             | Yes               |
| **condition_3** | c3              | AI bot            | No                |
| **condition_4** | c4              | AI bot            | Yes               |

## Key Template Variables

The experiment templates use Django-style {{ variable }} placeholders to personalise page text per condition. The most important variables are:

| **Variable**                     | **Value / description**                                                                                                         |
|----------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| **player_subject**               | Always "you" — refers to the human participant.                                                                                 |
| **opponent_subject**             | "player" (c1, c2) \| "player's AI bot" (c3, c4)                                                                                 |
| **ai_conditions**                | False (c1, c2) \| True (c3, c4) — whether the opponent is an AI bot.                                                            |
| **comm_conditions**              | False (c1, c3) \| True (c2, c4) — whether a communication round is shown.                                                       |
| **player_is_bot**                | False for the human participant; True for the AI bot player in c3/c4 pairs.                                                     |
| **formatted_payoff_a/b/c/d**     | Monetary payoffs formatted as currency strings (e.g. \$1.25). Values differ between the Prisoner's Dilemma and Stag Hunt games. |
| **comprehension_question_label** | Dynamically generated comprehension check question. The choice pair (\[Choice A/B\]) is randomly selected for each session.     |

## Annotation Conventions

| **Annotation**                               | **Meaning**                                                                                                                                                                                                           |
|----------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **\[variable_name\]**                        | A template variable placeholder whose value is condition-dependent. Resolved values are listed in the “Template variables” glossary above each page’s content box.                                                    |
| **{ val₁ \[IF c=c1\] \| val₂ \[IF c=c2\] }** | An inline condition-dependent value rendered in blue bold text. The braces { … } delimit the full span; each variant is the value shown to participants in the stated condition(s). Variants are separated by ‘ \| ’. |
| **\[IF condition = cN, cM\]**                | Small annotation appearing inside { } spans to identify which experimental condition(s) yield the immediately preceding value. Condition codes: c1 = Human/No-comm, c2 = Human/Comm, c3 = AI/No-comm, c4 = AI/Comm.   |
| **▸ Template variables:**                    | A compact glossary table shown above each page’s bordered content box. Lists every {{ variable }} used on that page and the value(s) it takes, grouped by condition where values differ.                              |
| **Shown in / Hidden in:**                    | Indicates which conditions include or skip a given page (controlled by is_displayed() in the app code).                                                                                                               |
| **\[IF: cond\] … \[END IF\]**                | Marks a conditional block in the HTML template. Content is only rendered for participants in the specified condition.                                                                                                 |
| **\[Button: label\]**                        | Represents a submit/action button visible at the bottom of the page.                                                                                                                                                  |
| **\[Form fields\]**                          | Placeholder for oTree-rendered form fields (e.g. multiple-choice, text input) whose exact appearance is determined at runtime.                                                                                        |
| **\[↳ filename.html\]**                      | Indicates content included from a shared template fragment.                                                                                                                                                           |

# App: app_consent

## Consent_v2

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Consent"</strong></p>
<p>────────────────────────────────────────────────</p>
<p><img src="media/image1.jpg" style="width:4.5in;height:0.85663in" /></p>
<p><em>Stony Brook Logo</em></p>
<p><strong>Project Title:</strong> Communication and Cooperation in Groups</p>
<p><strong>Principal Investigator:</strong> Dr. Reuben Kline</p>
<p><strong>Department:</strong> Department of Political Science</p>
<p><strong>KEY INFORMATION:</strong></p>
<ol type="1">
<li><p>The information in this form is being used to seek your consent for a research study. Being in the study is voluntary; it is up to you.</p></li>
<li><p>This research is being done to find out how people cooperate and communicate in small groups. Participation will last approximately 15 minutes. Study procedures for this research are:</p></li>
</ol>
<ul>
<li><p>Complete an experimental survey about a game in which you and another participant’s choices combine to give you additional bonus money.</p></li>
</ul>
<ol start="3" type="1">
<li><p>There are no foreseeable risks or discomforts associated with your participation in this study.</p></li>
</ol>
<ul>
<li><p>Please see the <strong>RISKS AND DISCOMFORTS</strong> section for a complete list of expected side effects</p></li>
</ul>
<ol start="4" type="1">
<li><p>There are no foreseeable benefits expected as a result of you being in this study.</p></li>
<li><p>Your alternative to not being in this study is to simply not participate.</p></li>
</ol>
<p><strong>You are being asked to be a volunteer in a research study.</strong></p>
<p><strong>PURPOSE</strong></p>
<p><strong>The purpose of this study is:</strong></p>
<ul>
<li><p>This study is for English-speaking adults who are at least 18 years old.</p></li>
<li><p>The purpose of this study is to understand how people communicate and interact in small groups.</p></li>
<li><p>Approximately 400 participants will be recruited for this research.</p></li>
</ul>
<p><strong>PROCEDURES</strong></p>
<p><strong>If you decide to be in this study, your part will involve:</strong></p>
<ul>
<li><p>This study will take approximately 15 minutes.</p></li>
<li><p>You will answer these questions using a computer.</p></li>
<li><p>You will be randomly assigned into an experimental treatment.</p></li>
<li><p>You will then play a game with real money at stake.</p></li>
<li><p>You will complete a demographic questionnaire.</p></li>
<li><p>You will be debriefed and given more information about the study and how your bonus earnings will be calculated.</p></li>
</ul>
<p><strong>RISKS / DISCOMFORTS</strong></p>
<p><strong>The following risks/discomforts may occur as a result of you being in this study:</strong></p>
<ul>
<li><p>There are no foreseeable risks or discomforts associated with your participation in this study.</p></li>
</ul>
<p><strong>BENEFITS</strong></p>
<ul>
<li><p>There is no direct benefit expected as a result of you being in this study.</p></li>
</ul>
<p><strong>PAYMENT TO YOU</strong></p>
<ul>
<li><p>Subjects will receive $7.00 for participating in this study. This is yours simply for completing the study and does not in any way depend on what happens during the study.</p></li>
<li><p>Throughout the course of the game, subjects have the potential to earn additional bonus money, between $1 and $5. This money will be added to the money you are already receiving simply for participating.</p></li>
<li><p>In the rare case that another participant is not available within 10 minutes of you beginning the study, you will automatically be paid the $7.00 participation fee and dismissed.</p></li>
</ul>
<p><strong>CONFIDENTIALITY</strong></p>
<p>We will take steps to help make sure that all the information we get about you is kept confidential. We do collect your Lab PC Number for payment processing. However, we cannot use this number to learn anything about you that you did not tell us in the questionnaire. In accordance with research rules and regulations, we as the researchers cannot request any information that could be used to identify you. All the study data that we get from you will be kept locked up. If any papers and talks are given about this research, your Lab PC Number will not be used. Your name will not be collected and will therefore not be connected to any answers you provide as part of the study.</p>
<p>We want to make sure that this study is being done correctly and that your rights and welfare are being protected. For this reason, we will share the data we get from you in this study with the study team, Stony Brook University's Institutional Review Board, applicable Institutional officials, and certain federal offices, including the Office for Human Research Protections (OHRP), and, where applicable, the Food and Drug Administration (FDA). However, if you tell us you are going to hurt yourself, hurt someone else, or if we believe the safety of a child is at risk, we will have to report this.</p>
<p>In a lawsuit, a judge can make us give him the information we collected about you.</p>
<p>If you are a U.S. Citizen or Resident Alien and you are paid $600 or more a year as a research subject, your social security number will be reported to those in charge of taxes (IRS) by the Research Foundation and you may have to pay taxes on this money.</p>
<p>If you are a Nonresident Alien, all payments made to you <em>must</em> be done through the Research Foundation and are subject to a 30% tax withholding. All withholdings and payments will be reported to those in charge of taxes (IRS) by the Research Foundation.</p>
<p><strong>COSTS TO YOU</strong></p>
<ul>
<li><p>There are no foreseeable costs to you associated with your participation in this study.</p></li>
</ul>
<p><strong>ALTERNATIVES</strong></p>
<ul>
<li><p>Your alternative to being in this study is to simply not participate.</p></li>
</ul>
<p><strong>IN CASE OF INJURY</strong></p>
<p>If you are injured as a result of being in this study, please contact Dr. Reuben Kline at reuben.kline@stonybrook.edu. The services of Stony Brook University Hospital will be open to you in case of such injury. However, you and/or your insurance company will be responsible for payment of any resulting treatment and/or hospital stay.</p>
<p><strong>YOUR RIGHTS AS A RESEARCH SUBJECT</strong></p>
<ul>
<li><p>Your participation in this study is voluntary. You do not have to be in this study if you don't want to be.</p></li>
<li><p>You have the right to change your mind and leave the study at any time without giving any reason, and without penalty.</p></li>
<li><p>Any new information that may make you change your mind about being in this study will be given to you.</p></li>
<li><p>You do not lose any of your legal rights by signing this consent form.</p></li>
</ul>
<p><strong>QUESTIONS ABOUT THE STUDY OR YOUR RIGHTS AS A RESEARCH SUBJECT</strong></p>
<ul>
<li><p>If you have any questions, concerns, or complaints about the study, you may contact Dr. Reuben Kline at reuben.kline@stonybrook.edu</p></li>
<li><p>If you have any questions about your rights as a research subject or if you would like to obtain information or offer input, you may contact the Stony Brook University Research Subject Advocate, Ms. Lu-Ann Kozlowski, BSN, RN, (631) 632-9036, OR by e-mail, lu-ann.kozlowski@stonybrook.edu</p></li>
<li><p>Visit Stony Brook University’s Community Outreach page, https://www.stonybrook.edu/commcms/research-community-outreach/index.php for more information about participating in research, frequently asked questions, and an opportunity to provide feedback, comments, or ask questions related to your experience as a research subject.</p></li>
</ul>
<p><em>If you click below, it means that you have read (or have had read to you) the information given in this consent form, and you would like to be a volunteer in this study.</em></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: I agree to participate in this study.]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## WaitingWarning

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><h4 id="welcome-to-the-experiment">Welcome to the Experiment!</h4>
<p>Thank you for joining our study. In the next step, you will be matched with another participant to complete the experiment.</p>
<p>On the next page, <em>you may enter a waiting room</em>. If so, you may need to wait a few seconds while we match you with another participant.</p>
<p>Once you are ready, click the button below to proceed.</p>
<p><strong>[Button: Proceed to be matched]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# App: app_waiting

## WaitForPartner

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>Waiting Room</p>
<p><em>[body_text]</em></p>
<p>Thank you for your patience. Please wait while we match you with another participant.</p>
<p><img src="media/image2.gif" style="width:4.5in;height:3.375in" /></p>
<p><em>Waiting Image</em></p>
<p>An aerial view of Stony Brook University's West Campus</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## TimeOutPage

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Continue"</strong></p>
<p>Please continue to the next page.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# App: app_prisoner

## GPWait

**Shown in:** condition_1, condition_2, condition_3, condition_4

*\[Default oTree WaitPage — no custom template; content below is the standard oTree waiting screen\]*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Please wait"</strong></p>
<p>Please wait for the other participants.</p>
<p><em>[A loading spinner is displayed automatically by the platform until all participants in the group have arrived at this point.]</em></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## FirstInfoPage

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><em><strong>[↳ common_info_page.html]</strong></em></p>
<p><strong>You Have Been Matched! You are now matched with another participant.</strong></p>
<p>────────────────────────────────────────────────</p>
<h4 id="important-information">Important Information</h4>
<p>Thanks for agreeing to participate in our study! There are two ways to earn money in this study:</p>
<ol start="6" type="1">
<li><p>Just for participating today you will earn $7.00. You will earn this money no matter what else happens in the experiment and regardless of any choices you make.</p></li>
<li><p>By participating in this study, you will also have the possibility to earn bonus money, up to an additional $2.50. We have randomly matched you with another participant. How much money you (and the other participant) earn depends on your decisions and those made by this other participant.</p></li>
</ol>
<p>Here's how your <strong>bonus payment</strong> will be determined:</p>
<ul>
<li><p>You will play two games in sequence, which are similar but not identical. In both games, you will be paired with the same participant.</p></li>
<li><p>Only one of the two games' results will be randomly selected for determining your bonus payment, and you will be paid based on that game's outcome.</p></li>
</ul>
<p>Please read the information on the following page carefully. It will explain the rules of <strong>Game 1</strong>, which will influence how you can earn additional <strong>bonus money</strong> in this study.</p>
<p>────────────────────────────────────────────────</p>
<p>To help us allocate bonus payments correctly, please enter your Lab PC Number before clicking Next Page.</p>
<p><strong>Please input your Lab PC Number ⓘ:</strong></p>
<p><em>[form.PC_id_manual_input]</em></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Info_GPT

**Shown in:** condition_3, condition_4 **\| Hidden in:** condition_1, condition_2

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Live ChatGPT Agent in This Study"</strong></p>
<p><em><strong>[↳ preamble_AI_conditions.html]</strong></em></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p>In this study, you are paired with another participant. <strong>For this part of the experiment, an AI will play on your behalf — you will not be asked to make any game decisions yourself.</strong> The AI acts as your stand-in: it reads the game instructions and makes every choice in your place.</p>
<p><strong>What this means for you:</strong> Your bonus payment will be determined by the AI's choices combined with the choices of the other participant. Even though you are not making the decisions, the outcomes — including your bonus — are real and will be paid to you at the end.</p>
<p><strong>[ELSE]</strong></p>
<p>In this study, you are paired with another participant. <strong>For this part of the experiment, an AI will play on that participant's behalf — they will not be making decisions directly themselves.</strong> The AI acts as their stand-in: it reads the same game instructions and makes every choice in their place.</p>
<p><strong>What this means for you:</strong> You will make your own decisions as normal. Your bonus payment will be determined by your choices combined with the AI's choices on behalf of the other participant. The other participant is real — they are also enrolled in this study — and their bonus will likewise depend on how the AI played for them.</p>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>How does the AI make decisions?</strong></p>
<p>The AI in this experiment is a <strong>live instance of ChatGPT</strong> — not a pre-programmed algorithm or a replay of recorded human behavior. Before each decision, ChatGPT is given <strong>exactly the same instructions that the active participant reads</strong>, and is asked to reason through the situation and make a choice, just as a human participant would.</p>
<p>Specifically, before each decision, ChatGPT receives:</p>
<ul>
<li><p>The same game rules and payoff structure shown to participants.</p></li>
<li><p>The current context of the round (including any messages exchanged, when applicable).</p></li>
<li><p>A request to choose between the available options.</p></li>
</ul>
<p>ChatGPT then reasons through the situation and submits a response, which is recorded as its move. <strong>This all happens live, in real time, during the experiment.</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Instruction

**Shown in:** condition_1, condition_2, condition_3, condition_4

**▸ Template variables:**

| **comprehension_question_label** | We want to make sure you understand the game. If you select \[Choice A/B\] and the other player selects \[Choice A/B\], what will your payoff be? (Note: choice pair is randomly selected each time) (c1, c2) \| We want to make sure you understand the game. If you select \[Choice A/B\] and the other player's AI bot selects \[Choice A/B\], what will your payoff be? (Note: choice pair is randomly selected each time) / We want to make sure you understand the game. If you selects \[Choice A/B\] and the other player's AI bot selects \[Choice A/B\], what will your payoff be? (Note: choice pair is randomly selected each time) (c3, c4) |
|----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **capitalized_player_subject**   | You                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **opponent_subject**             | player (c1, c2) \| player's AI bot (c3, c4)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **player_subject**               | you                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **formatted_payoff_a**           | \$2.50                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **formatted_payoff_d**           | \$3.50                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **formatted_payoff_b**           | \$5.00                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **formatted_payoff_c**           | \$1.00                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **ai_conditions**                | False (c1, c2) \| True (c3, c4)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **group_treatment**              | condition_1 (c1) \| condition_2 (c2) \| condition_3 (c3) \| condition_4 (c4)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **player_is_bot**                | False (c1, c2) \| False / True (c3, c4)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Instructions - Game 1"</strong></p>
<p><strong>[IF: ai_conditions]</strong></p>
<p><em><strong>[↳ instructions_pd_stag_ai.html]</strong></em></p>
<p><em>You and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> are both facing the same two options to choose from: <strong>A</strong> or <strong>B</strong></em>. How much you and the other player each earn depends on the combination of the choices made by you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong>.</p>
<p>There are four possible outcomes:</p>
<ul>
<li><p>If you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> choose A, you and the other player will both receive $2.50.</p></li>
<li><p>If you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> choose B, you and the other player will both receive $3.50.</p></li>
<li><p>If you choose A and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chooses B, you will receive $5.00 and the other player will receive $1.00.</p></li>
<li><p>If you choose B and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chooses A, you will receive $1.00 and the other player will receive $5.00.</p></li>
</ul>
<p>The bonus amounts for you and the other player can be summarized in the following table. <em>Within each of the four highlighted squares are the bonus amounts for each possible combination of choices</em>. Your bonus amount is <strong>listed first and in bold</strong>, and the other player's bonus amount is listed second. The other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> will be given the same information and will be choosing between the same choices as you.</p>
<p><em><strong>[↳ payoff_matrix_pd_stag_ai.html]</strong></em></p>
<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th></th>
<th></th>
<th>Other { player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</th>
<th></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td></td>
<td></td>
<td>Choice A</td>
<td>Choice B</td>
</tr>
<tr class="even">
<td>You</td>
<td>Choice A</td>
<td>$2.50, $2.50</td>
<td>$5.00, $1.00</td>
</tr>
<tr class="odd">
<td></td>
<td>Choice B</td>
<td>$1.00, $5.00</td>
<td>$3.50, $3.50</td>
</tr>
</tbody>
</table>
<p><strong>[ELSE]</strong></p>
<p><em><strong>[↳ instructions_pd_stag_humans.html]</strong></em></p>
<p><em>You and the other player are both facing the same two options to choose from: <strong>A</strong> or <strong>B</strong></em>. How much you and the other player each earn depends on the combination of the choices made by you and the other player.</p>
<p>There are four possible outcomes:</p>
<ul>
<li><p>If you both choose A, you and the other player will both receive $2.50.</p></li>
<li><p>If you both choose B, you and the other player will both receive $3.50.</p></li>
<li><p>If you choose A and the other player chooses B, you will receive $5.00 and they will receive $1.00.</p></li>
<li><p>If you choose B and the other player chooses A, you will receive $1.00 and they will receive $5.00.</p></li>
</ul>
<p>The bonus amounts for you and the other player can be summarized in the following table. <em>Within each of the four highlighted squares are the bonus amounts for each possible combination of your choice and the other player’s choice</em>. Your bonus amount is <strong>listed first and in bold</strong>, and the other player's bonus amount is listed second. The other player will be given the same information and will be choosing between the same choices as you.</p>
<p><em><strong>[↳ payoff_matrix_pd_stag_humans.html]</strong></em></p>
<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th></th>
<th></th>
<th>Other player</th>
<th></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td></td>
<td></td>
<td>Choice A</td>
<td>Choice B</td>
</tr>
<tr class="even">
<td>You</td>
<td>Choice A</td>
<td>$2.50, $2.50</td>
<td>$5.00, $1.00</td>
</tr>
<tr class="odd">
<td></td>
<td>Choice B</td>
<td>$1.00, $5.00</td>
<td>$3.50, $3.50</td>
</tr>
</tbody>
</table>
<p><strong>[END IF]</strong></p>
<p><strong>{ We want to make sure you understand the game. If you select [Choice A/B] and the other player selects [Choice A/B], what will your payoff be? (Note: choice pair is randomly selected each time) [IF condition = c1, c2] | We want to make sure you understand the game. If you select [Choice A/B] and the other player's AI bot selects [Choice A/B], what will your payoff be? (Note: choice pair is randomly selected each time) / We want to make sure you understand the game. If you selects [Choice A/B] and the other player's AI bot selects [Choice A/B], what will your payoff be? (Note: choice pair is randomly selected each time) [IF condition = c3, c4] }</strong></p>
<p><em>[Field: comprehension_answer — RadioSelect: A ($2.50) | B ($5.00) | C ($1.00) | D ($3.50)]</em></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Preamble_Comm

**Shown in:** condition_2, condition_4 **\| Hidden in:** condition_1, condition_3

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Message Exchange - Game 1"</strong></p>
<p><strong>[IF: condition_4_assigned]</strong></p>
<p><em><strong>[↳ preamble_communication_AI.html]</strong></em></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p>Choosing A or B isn't the only choice your AI bot will be making.</p>
<ul>
<li><p>Before your AI bot decides to choose A or B, the other player can type a free-text message to send to your AI bot.</p></li>
<li><p>Your AI bot will also compose and send a message to the other player at the same time, without seeing the other player's message first.</p></li>
<li><p>Messages can be up to <strong>50 words</strong>. Either party may also choose to send no message.</p></li>
<li><p>Messages do not affect your bonus. Only choices of A or B by your AI bot and the other player determine your bonus.</p></li>
<li><p>Each party will see the other's message before making the final choice of A or B.</p></li>
<li><p>Regardless of which message your AI bot chooses to send, the other player is free to choose either A or B. The same is true for your AI bot.</p></li>
</ul>
<p><strong>[ELSE]</strong></p>
<p>Choosing A or B isn't the only choice you will be making.</p>
<ul>
<li><p>Before you decide to choose A or B, you can type a free-text message to send to the other player's AI bot.</p></li>
<li><p>The other player's AI bot will also compose and send a message to you at the same time, without seeing your message first.</p></li>
<li><p>Your message can be up to <strong>50 words</strong>. You may also choose to leave it blank.</p></li>
<li><p>Messages do not affect your bonus. Only choices of A or B by you and the other player's AI bot determine your bonus.</p></li>
<li><p>You will see the AI bot's message before making your final choice of A or B.</p></li>
<li><p>Regardless of which message you choose to send, you are free to choose either A or B. The same is true for the other player's AI bot.</p></li>
</ul>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p><em><strong>[↳ preamble_communication.html]</strong></em></p>
<p>Choosing A or B isn’t the only choice you and the other player will be making.</p>
<ul>
<li><p>Before you decide to choose A or B, you and the other player can each send one free-text message to each other.</p></li>
<li><p>You will both type your messages at the same time, without seeing the other player's message first.</p></li>
<li><p>Your message can be up to <strong>50 words</strong>. You may also choose to leave it blank.</p></li>
<li><p>Messages do not affect your bonus or the bonus of the other player. Only choices of A or B by you and the other player determine your and the other player's bonus.</p></li>
<li><p>Each of you will see the other's message before making your final choice of A or B.</p></li>
<li><p>Regardless of which message you choose to send, you are free to choose either A or B. The same is true for the other player.</p></li>
</ul>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Communication

**Shown in:** condition_2, condition_4 **\| Hidden in:** condition_1, condition_3

**▸ Template variables:**

| **capitalized_player_subject** | You                                                                          |
|--------------------------------|------------------------------------------------------------------------------|
| **opponent_subject**           | player (c1, c2) \| player's AI bot (c3, c4)                                  |
| **player_subject**             | you                                                                          |
| **formatted_payoff_a**         | \$2.50                                                                       |
| **formatted_payoff_d**         | \$3.50                                                                       |
| **formatted_payoff_b**         | \$5.00                                                                       |
| **formatted_payoff_c**         | \$1.00                                                                       |
| **group_treatment**            | condition_1 (c1) \| condition_2 (c2) \| condition_3 (c3) \| condition_4 (c4) |
| **player_is_bot**              | False (c1, c2) \| False / True (c3, c4)                                      |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>▶ Game Rules Reference (click to expand)</p>
<p><strong>[IF: condition_4_assigned]</strong></p>
<p><em><strong>[↳ instructions_pd_stag_ai.html]</strong></em></p>
<p><em>You and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> are both facing the same two options to choose from: <strong>A</strong> or <strong>B</strong></em>. How much you and the other player each earn depends on the combination of the choices made by you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong>.</p>
<p>There are four possible outcomes:</p>
<ul>
<li><p>If you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> choose A, you and the other player will both receive $2.50.</p></li>
<li><p>If you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> choose B, you and the other player will both receive $3.50.</p></li>
<li><p>If you choose A and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chooses B, you will receive $5.00 and the other player will receive $1.00.</p></li>
<li><p>If you choose B and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chooses A, you will receive $1.00 and the other player will receive $5.00.</p></li>
</ul>
<p>The bonus amounts for you and the other player can be summarized in the following table. <em>Within each of the four highlighted squares are the bonus amounts for each possible combination of choices</em>. Your bonus amount is <strong>listed first and in bold</strong>, and the other player's bonus amount is listed second. The other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> will be given the same information and will be choosing between the same choices as you.</p>
<p><strong>[ELSE]</strong></p>
<p><em><strong>[↳ instructions_pd_stag_humans.html]</strong></em></p>
<p><em>You and the other player are both facing the same two options to choose from: <strong>A</strong> or <strong>B</strong></em>. How much you and the other player each earn depends on the combination of the choices made by you and the other player.</p>
<p>There are four possible outcomes:</p>
<ul>
<li><p>If you both choose A, you and the other player will both receive $2.50.</p></li>
<li><p>If you both choose B, you and the other player will both receive $3.50.</p></li>
<li><p>If you choose A and the other player chooses B, you will receive $5.00 and they will receive $1.00.</p></li>
<li><p>If you choose B and the other player chooses A, you will receive $1.00 and they will receive $5.00.</p></li>
</ul>
<p>The bonus amounts for you and the other player can be summarized in the following table. <em>Within each of the four highlighted squares are the bonus amounts for each possible combination of your choice and the other player’s choice</em>. Your bonus amount is <strong>listed first and in bold</strong>, and the other player's bonus amount is listed second. The other player will be given the same information and will be choosing between the same choices as you.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: condition_4_assigned]</strong></p>
<p><strong>[IF: opponent_is_bot]</strong></p>
<p><strong>Note:</strong> The AI bot is playing on behalf of your opponent.</p>
<p>Here you can type a message to send to the other participant's AI bot. The AI bot will also be given the chance to send a message to you.</p>
<p>Please <strong>type your message</strong> below (maximum 50 words; leave blank to send no message):</p>
<p><em>[Field: messages — LongStringField]</em></p>
<p>0 / 50 words</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p><strong>Note:</strong> An AI bot is making choices on your behalf.</p>
<p>The AI bot playing on your behalf will compose and send a message to the other participant. The other participant will also be given the chance to send a message back.</p>
<p>The AI bot will send a message on your behalf. You may proceed to the next page.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p>Here you can type a message to send to the other participant. They will also be given the chance to send a message to you.</p>
<p>Please <strong>type your message</strong> below (maximum 50 words; leave blank to send no message):</p>
<p><em>[Field: messages — LongStringField]</em></p>
<p>0 / 50 words</p>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## BotComposing

**Shown in:** condition_4 **\| Hidden in:** condition_1, condition_2, condition_3

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Please Wait"</strong></p>
<p>The AI is composing a message…</p>
<p>This may take a few seconds. Please do not close this page.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## CommWaitPage

**Shown in:** condition_2, condition_4 **\| Hidden in:** condition_1, condition_3

*\[Default oTree WaitPage — no custom template; content below is the standard oTree waiting screen\]*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Please wait"</strong></p>
<p>Please wait for the other participants.</p>
<p><em>[A loading spinner is displayed automatically by the platform until all participants in the group have arrived at this point.]</em></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## ShowMessages

**Shown in:** condition_2, condition_4 **\| Hidden in:** condition_1, condition_3

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Messages"</strong></p>
<p><strong>[IF: condition_4_assigned]</strong></p>
<p><strong>[IF: opponent_is_bot]</strong></p>
<p>Here are the messages you and the other player's AI bot sent to each other:</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p>Here are the messages your AI bot and the other player sent to each other:</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: opponent_is_bot]</strong></p>
<ul>
<li><p>You sent: <em>[player.messages or "(no message)"]</em></p></li>
<li><p>The other player's AI bot sent: <em>[opponent.messages or "(no message)"]</em></p></li>
</ul>
<p>Now you will choose between Choice A and Choice B.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: player_is_bot]</strong></p>
<ul>
<li><p>Your AI bot sent: <em>[player.messages or "(no message)"]</em></p></li>
<li><p>The other player sent: <em>[opponent.messages or "(no message)"]</em></p></li>
</ul>
<p>Now your bot will choose between Choice A and Choice B on your behalf.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p>Here are the messages you and the other player sent to each other:</p>
<ul>
<li><p>You sent: <em>[my_message or "(no message)"]</em></p></li>
<li><p>The other player sent: <em>[opponent_message or "(no message)"]</em></p></li>
</ul>
<p>Now you will choose between Choice A and Choice B.</p>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## BotThinking

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Please Wait"</strong></p>
<p>The AI is making its decision…</p>
<p>This may take a few seconds. Please do not close this page.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## WaitForBotDecision

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"wait_for_bot_decision"</strong></p>
<p>Please Wait The other participant’s AI is making its decision… Please wait a moment.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Decision

**Shown in:** condition_1, condition_2, condition_3, condition_4

**▸ Template variables:**

| **opponent_subject**           | player (c1, c2) \| player's AI bot (c3, c4)                                  |
|--------------------------------|------------------------------------------------------------------------------|
| **capitalized_player_subject** | You                                                                          |
| **player_subject**             | you                                                                          |
| **formatted_payoff_a**         | \$2.50                                                                       |
| **formatted_payoff_d**         | \$3.50                                                                       |
| **formatted_payoff_b**         | \$5.00                                                                       |
| **formatted_payoff_c**         | \$1.00                                                                       |
| **ai_conditions**              | False (c1, c2) \| True (c3, c4)                                              |
| **comm_conditions**            | False (c1, c3) \| True (c2, c4)                                              |
| **group_treatment**            | condition_1 (c1) \| condition_2 (c2) \| condition_3 (c3) \| condition_4 (c4) |
| **player_is_bot**              | False (c1, c2) \| False / True (c3, c4)                                      |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Decision - Game 1"</strong></p>
<p>Now you will have to make your decision. Below are the instructions from the previous page that you already read, for your reference.</p>
<p><strong>[IF: ai_conditions]</strong></p>
<p><em><strong>[↳ instructions_pd_stag_ai.html]</strong></em></p>
<p><em>You and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> are both facing the same two options to choose from: <strong>A</strong> or <strong>B</strong></em>. How much you and the other player each earn depends on the combination of the choices made by you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong>.</p>
<p>There are four possible outcomes:</p>
<ul>
<li><p>If you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> choose A, you and the other player will both receive $2.50.</p></li>
<li><p>If you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> choose B, you and the other player will both receive $3.50.</p></li>
<li><p>If you choose A and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chooses B, you will receive $5.00 and the other player will receive $1.00.</p></li>
<li><p>If you choose B and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chooses A, you will receive $1.00 and the other player will receive $5.00.</p></li>
</ul>
<p>The bonus amounts for you and the other player can be summarized in the following table. <em>Within each of the four highlighted squares are the bonus amounts for each possible combination of choices</em>. Your bonus amount is <strong>listed first and in bold</strong>, and the other player's bonus amount is listed second. The other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> will be given the same information and will be choosing between the same choices as you.</p>
<p><strong>[ELSE]</strong></p>
<p><em><strong>[↳ instructions_pd_stag_humans.html]</strong></em></p>
<p><em>You and the other player are both facing the same two options to choose from: <strong>A</strong> or <strong>B</strong></em>. How much you and the other player each earn depends on the combination of the choices made by you and the other player.</p>
<p>There are four possible outcomes:</p>
<ul>
<li><p>If you both choose A, you and the other player will both receive $2.50.</p></li>
<li><p>If you both choose B, you and the other player will both receive $3.50.</p></li>
<li><p>If you choose A and the other player chooses B, you will receive $5.00 and they will receive $1.00.</p></li>
<li><p>If you choose B and the other player chooses A, you will receive $1.00 and they will receive $5.00.</p></li>
</ul>
<p>The bonus amounts for you and the other player can be summarized in the following table. <em>Within each of the four highlighted squares are the bonus amounts for each possible combination of your choice and the other player’s choice</em>. Your bonus amount is <strong>listed first and in bold</strong>, and the other player's bonus amount is listed second. The other player will be given the same information and will be choosing between the same choices as you.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: comm_conditions]</strong></p>
<h5 id="messages-exchanged-reminder">Messages Exchanged Reminder</h5>
<p><strong>[IF: ai_conditions]</strong></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p><strong>Here's a reminder of the messages your AI bot and the other player sent:</strong></p>
<ul>
<li><p>Your AI bot chose to send the message "<em>[my_message]</em>",</p></li>
<li><p>And the other player chose to send the message "<em>[opponent_message]</em>".</p></li>
</ul>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: opponent_is_bot]</strong></p>
<p><strong>Here's a reminder of the messages you and the other player's AI bot sent:</strong></p>
<ul>
<li><p>You chose to send the message "<em>[my_message]</em>",</p></li>
<li><p>And the other player's AI bot chose to send the message "<em>[opponent_message]</em>".</p></li>
</ul>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p><strong>Here's a reminder of the messages you and the other player sent:</strong></p>
<ul>
<li><p>You chose to send the message "<em>[my_message]</em>",</p></li>
<li><p>And the other player chose to send the message "<em>[opponent_message]</em>".</p></li>
</ul>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p><strong>[END IF]</strong></p>
<h5 id="decision-1">Decision</h5>
<p><strong>[IF: ai_conditions]</strong></p>
<p><strong>[IF: opponent_is_bot]</strong></p>
<p><strong>Please select your choice:</strong></p>
<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th></th>
<th></th>
<th>The other { player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</th>
<th></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td></td>
<td></td>
<td>Choice A</td>
<td>Choice B</td>
</tr>
<tr class="even">
<td>You</td>
<td>I choose Choice A</td>
<td>$2.50, $2.50</td>
<td>$5.00, $1.00</td>
</tr>
<tr class="odd">
<td></td>
<td>I choose Choice B</td>
<td>$1.00, $5.00</td>
<td>$3.50, $3.50</td>
</tr>
</tbody>
</table>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p><strong>Your bot made the following decision:</strong></p>
<p><strong>[IF: bot_cooperate]</strong></p>
<ul>
<li><p>Choice B</p></li>
</ul>
<p><strong>[ELSE]</strong></p>
<ul>
<li><p>Choice A</p></li>
</ul>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p><strong>Please select your choice:</strong></p>
<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th></th>
<th></th>
<th>The other { player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</th>
<th></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td></td>
<td></td>
<td>Choice A</td>
<td>Choice B</td>
</tr>
<tr class="even">
<td>You</td>
<td>I choose Choice A</td>
<td>$2.50, $2.50</td>
<td>$5.00, $1.00</td>
</tr>
<tr class="odd">
<td></td>
<td>I choose Choice B</td>
<td>$1.00, $5.00</td>
<td>$3.50, $3.50</td>
</tr>
</tbody>
</table>
<p><strong>[END IF]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## ResultsWaitPage

**Shown in:** condition_1, condition_2, condition_3, condition_4

*\[Default oTree WaitPage — no custom template; content below is the standard oTree waiting screen\]*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Please wait"</strong></p>
<p>Please wait for the other participants.</p>
<p><em>[A loading spinner is displayed automatically by the platform until all participants in the group have arrived at this point.]</em></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## NextGameWarning

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><em><strong>[↳ next_game_warning.html]</strong></em></p>
<h4 id="instructions-for-the-second-game">Instructions for the Second Game</h4>
<p>Now you will be playing another game. It is similar, but not identical to, the first game you played. Please pay careful attention to the payment amounts for each choice.</p>
<p>The difference in this game is that the payments based on the combinations of choices have changed, but the overall structure of the game remains the same.</p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Start Second Game]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# App: app_stag

## GPWait

**Shown in:** condition_1, condition_2, condition_3, condition_4

*\[Default oTree WaitPage — no custom template; content below is the standard oTree waiting screen\]*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Please wait"</strong></p>
<p>Please wait for the other participants.</p>
<p><em>[A loading spinner is displayed automatically by the platform until all participants in the group have arrived at this point.]</em></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Instruction

**Shown in:** condition_1, condition_2, condition_3, condition_4

**▸ Template variables:**

| **comprehension_question_label** | We want to make sure you understand the game. If you select \[Choice A/B\] and the other player selects \[Choice A/B\], what will your payoff be? (Note: choice pair is randomly selected each time) (c1, c2) \| We want to make sure you understand the game. If you select \[Choice A/B\] and the other player's AI bot selects \[Choice A/B\], what will your payoff be? (Note: choice pair is randomly selected each time) / We want to make sure you understand the game. If you selects \[Choice A/B\] and the other player's AI bot selects \[Choice A/B\], what will your payoff be? (Note: choice pair is randomly selected each time) (c3, c4) |
|----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **capitalized_player_subject**   | You                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **opponent_subject**             | player (c1, c2) \| player's AI bot (c3, c4)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **player_subject**               | you                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **formatted_payoff_a**           | \$2.50                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **formatted_payoff_d**           | \$5.00                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **formatted_payoff_b**           | \$3.50                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **formatted_payoff_c**           | \$1.00                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **ai_conditions**                | False (c1, c2) \| True (c3, c4)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **group_treatment**              | condition_1 (c1) \| condition_2 (c2) \| condition_3 (c3) \| condition_4 (c4)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **player_is_bot**                | False (c1, c2) \| False / True (c3, c4)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Instructions - Game 2"</strong></p>
<p><strong>[IF: ai_conditions]</strong></p>
<p><em><strong>[↳ instructions_pd_stag_ai.html]</strong></em></p>
<p><em>You and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> are both facing the same two options to choose from: <strong>A</strong> or <strong>B</strong></em>. How much you and the other player each earn depends on the combination of the choices made by you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong>.</p>
<p>There are four possible outcomes:</p>
<ul>
<li><p>If you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> choose A, you and the other player will both receive $2.50.</p></li>
<li><p>If you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> choose B, you and the other player will both receive $5.00.</p></li>
<li><p>If you choose A and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chooses B, you will receive $3.50 and the other player will receive $1.00.</p></li>
<li><p>If you choose B and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chooses A, you will receive $1.00 and the other player will receive $3.50.</p></li>
</ul>
<p>The bonus amounts for you and the other player can be summarized in the following table. <em>Within each of the four highlighted squares are the bonus amounts for each possible combination of choices</em>. Your bonus amount is <strong>listed first and in bold</strong>, and the other player's bonus amount is listed second. The other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> will be given the same information and will be choosing between the same choices as you.</p>
<p><em><strong>[↳ payoff_matrix_pd_stag_ai.html]</strong></em></p>
<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th></th>
<th></th>
<th>Other { player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</th>
<th></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td></td>
<td></td>
<td>Choice A</td>
<td>Choice B</td>
</tr>
<tr class="even">
<td>You</td>
<td>Choice A</td>
<td>$2.50, $2.50</td>
<td>$3.50, $1.00</td>
</tr>
<tr class="odd">
<td></td>
<td>Choice B</td>
<td>$1.00, $3.50</td>
<td>$5.00, $5.00</td>
</tr>
</tbody>
</table>
<p><strong>[ELSE]</strong></p>
<p><em><strong>[↳ instructions_pd_stag_humans.html]</strong></em></p>
<p><em>You and the other player are both facing the same two options to choose from: <strong>A</strong> or <strong>B</strong></em>. How much you and the other player each earn depends on the combination of the choices made by you and the other player.</p>
<p>There are four possible outcomes:</p>
<ul>
<li><p>If you both choose A, you and the other player will both receive $2.50.</p></li>
<li><p>If you both choose B, you and the other player will both receive $5.00.</p></li>
<li><p>If you choose A and the other player chooses B, you will receive $3.50 and they will receive $1.00.</p></li>
<li><p>If you choose B and the other player chooses A, you will receive $1.00 and they will receive $3.50.</p></li>
</ul>
<p>The bonus amounts for you and the other player can be summarized in the following table. <em>Within each of the four highlighted squares are the bonus amounts for each possible combination of your choice and the other player’s choice</em>. Your bonus amount is <strong>listed first and in bold</strong>, and the other player's bonus amount is listed second. The other player will be given the same information and will be choosing between the same choices as you.</p>
<p><em><strong>[↳ payoff_matrix_pd_stag_humans.html]</strong></em></p>
<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th></th>
<th></th>
<th>Other player</th>
<th></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td></td>
<td></td>
<td>Choice A</td>
<td>Choice B</td>
</tr>
<tr class="even">
<td>You</td>
<td>Choice A</td>
<td>$2.50, $2.50</td>
<td>$3.50, $1.00</td>
</tr>
<tr class="odd">
<td></td>
<td>Choice B</td>
<td>$1.00, $3.50</td>
<td>$5.00, $5.00</td>
</tr>
</tbody>
</table>
<p><strong>[END IF]</strong></p>
<p><strong>{ We want to make sure you understand the game. If you select [Choice A/B] and the other player selects [Choice A/B], what will your payoff be? (Note: choice pair is randomly selected each time) [IF condition = c1, c2] | We want to make sure you understand the game. If you select [Choice A/B] and the other player's AI bot selects [Choice A/B], what will your payoff be? (Note: choice pair is randomly selected each time) / We want to make sure you understand the game. If you selects [Choice A/B] and the other player's AI bot selects [Choice A/B], what will your payoff be? (Note: choice pair is randomly selected each time) [IF condition = c3, c4] }</strong></p>
<p><em>[Field: comprehension_answer — RadioSelect: A ($2.50) | B ($3.50) | C ($1.00) | D ($5.00)]</em></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Preamble_Comm

**Shown in:** condition_2, condition_4 **\| Hidden in:** condition_1, condition_3

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Message Exchange – Game 2"</strong></p>
<p><strong>[IF: condition_4_assigned]</strong></p>
<p><em><strong>[↳ preamble_communication_AI.html]</strong></em></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p>Choosing A or B isn't the only choice your AI bot will be making.</p>
<ul>
<li><p>Before your AI bot decides to choose A or B, the other player can type a free-text message to send to your AI bot.</p></li>
<li><p>Your AI bot will also compose and send a message to the other player at the same time, without seeing the other player's message first.</p></li>
<li><p>Messages can be up to <strong>50 words</strong>. Either party may also choose to send no message.</p></li>
<li><p>Messages do not affect your bonus. Only choices of A or B by your AI bot and the other player determine your bonus.</p></li>
<li><p>Each party will see the other's message before making the final choice of A or B.</p></li>
<li><p>Regardless of which message your AI bot chooses to send, the other player is free to choose either A or B. The same is true for your AI bot.</p></li>
</ul>
<p><strong>[ELSE]</strong></p>
<p>Choosing A or B isn't the only choice you will be making.</p>
<ul>
<li><p>Before you decide to choose A or B, you can type a free-text message to send to the other player's AI bot.</p></li>
<li><p>The other player's AI bot will also compose and send a message to you at the same time, without seeing your message first.</p></li>
<li><p>Your message can be up to <strong>50 words</strong>. You may also choose to leave it blank.</p></li>
<li><p>Messages do not affect your bonus. Only choices of A or B by you and the other player's AI bot determine your bonus.</p></li>
<li><p>You will see the AI bot's message before making your final choice of A or B.</p></li>
<li><p>Regardless of which message you choose to send, you are free to choose either A or B. The same is true for the other player's AI bot.</p></li>
</ul>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p><em><strong>[↳ preamble_communication.html]</strong></em></p>
<p>Choosing A or B isn’t the only choice you and the other player will be making.</p>
<ul>
<li><p>Before you decide to choose A or B, you and the other player can each send one free-text message to each other.</p></li>
<li><p>You will both type your messages at the same time, without seeing the other player's message first.</p></li>
<li><p>Your message can be up to <strong>50 words</strong>. You may also choose to leave it blank.</p></li>
<li><p>Messages do not affect your bonus or the bonus of the other player. Only choices of A or B by you and the other player determine your and the other player's bonus.</p></li>
<li><p>Each of you will see the other's message before making your final choice of A or B.</p></li>
<li><p>Regardless of which message you choose to send, you are free to choose either A or B. The same is true for the other player.</p></li>
</ul>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Communication

**Shown in:** condition_2, condition_4 **\| Hidden in:** condition_1, condition_3

**▸ Template variables:**

| **capitalized_player_subject** | You                                                                          |
|--------------------------------|------------------------------------------------------------------------------|
| **opponent_subject**           | player (c1, c2) \| player's AI bot (c3, c4)                                  |
| **player_subject**             | you                                                                          |
| **formatted_payoff_a**         | \$2.50                                                                       |
| **formatted_payoff_d**         | \$5.00                                                                       |
| **formatted_payoff_b**         | \$3.50                                                                       |
| **formatted_payoff_c**         | \$1.00                                                                       |
| **group_treatment**            | condition_1 (c1) \| condition_2 (c2) \| condition_3 (c3) \| condition_4 (c4) |
| **player_is_bot**              | False (c1, c2) \| False / True (c3, c4)                                      |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Communication – Game 2"</strong></p>
<p>▶ Game Rules Reference (click to expand)</p>
<p><strong>[IF: condition_4_assigned]</strong></p>
<p><em><strong>[↳ instructions_pd_stag_ai.html]</strong></em></p>
<p><em>You and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> are both facing the same two options to choose from: <strong>A</strong> or <strong>B</strong></em>. How much you and the other player each earn depends on the combination of the choices made by you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong>.</p>
<p>There are four possible outcomes:</p>
<ul>
<li><p>If you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> choose A, you and the other player will both receive $2.50.</p></li>
<li><p>If you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> choose B, you and the other player will both receive $5.00.</p></li>
<li><p>If you choose A and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chooses B, you will receive $3.50 and the other player will receive $1.00.</p></li>
<li><p>If you choose B and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chooses A, you will receive $1.00 and the other player will receive $3.50.</p></li>
</ul>
<p>The bonus amounts for you and the other player can be summarized in the following table. <em>Within each of the four highlighted squares are the bonus amounts for each possible combination of choices</em>. Your bonus amount is <strong>listed first and in bold</strong>, and the other player's bonus amount is listed second. The other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> will be given the same information and will be choosing between the same choices as you.</p>
<p><strong>[ELSE]</strong></p>
<p><em><strong>[↳ instructions_pd_stag_humans.html]</strong></em></p>
<p><em>You and the other player are both facing the same two options to choose from: <strong>A</strong> or <strong>B</strong></em>. How much you and the other player each earn depends on the combination of the choices made by you and the other player.</p>
<p>There are four possible outcomes:</p>
<ul>
<li><p>If you both choose A, you and the other player will both receive $2.50.</p></li>
<li><p>If you both choose B, you and the other player will both receive $5.00.</p></li>
<li><p>If you choose A and the other player chooses B, you will receive $3.50 and they will receive $1.00.</p></li>
<li><p>If you choose B and the other player chooses A, you will receive $1.00 and they will receive $3.50.</p></li>
</ul>
<p>The bonus amounts for you and the other player can be summarized in the following table. <em>Within each of the four highlighted squares are the bonus amounts for each possible combination of your choice and the other player’s choice</em>. Your bonus amount is <strong>listed first and in bold</strong>, and the other player's bonus amount is listed second. The other player will be given the same information and will be choosing between the same choices as you.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: condition_4_assigned]</strong></p>
<p><strong>[IF: opponent_is_bot]</strong></p>
<p><strong>Note:</strong> The AI bot is playing on behalf of your opponent.</p>
<p>Here you can type a message to send to the other participant's AI bot. The AI bot will also be given the chance to send a message to you.</p>
<p>Please <strong>type your message</strong> below (maximum 50 words; leave blank to send no message):</p>
<p><em>[Field: messages — LongStringField]</em></p>
<p>0 / 50 words</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p><strong>Note:</strong> An AI bot is making choices on your behalf.</p>
<p>The AI bot playing on your behalf will compose and send a message to the other participant. The other participant will also be given the chance to send a message back.</p>
<p>The AI bot will send a message on your behalf. You may proceed to the next page.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p>Here you can type a message to send to the other participant. They will also be given the chance to send a message to you.</p>
<p>Please <strong>type your message</strong> below (maximum 50 words; leave blank to send no message):</p>
<p><em>[Field: messages — LongStringField]</em></p>
<p>0 / 50 words</p>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## BotComposing

**Shown in:** condition_4 **\| Hidden in:** condition_1, condition_2, condition_3

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Please Wait"</strong></p>
<p>The AI is composing a message…</p>
<p>This may take a few seconds. Please do not close this page.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## CommWaitPage

**Shown in:** condition_2, condition_4 **\| Hidden in:** condition_1, condition_3

*\[Default oTree WaitPage — no custom template; content below is the standard oTree waiting screen\]*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Please wait"</strong></p>
<p>Please wait for the other participants.</p>
<p><em>[A loading spinner is displayed automatically by the platform until all participants in the group have arrived at this point.]</em></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## ShowMessages

**Shown in:** condition_2, condition_4 **\| Hidden in:** condition_1, condition_3

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Messages – Game 2"</strong></p>
<p><strong>[IF: condition_4_assigned]</strong></p>
<p><strong>[IF: opponent_is_bot]</strong></p>
<p>Here are the messages you and the other player's AI bot sent to each other:</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p>Here are the messages your AI bot and the other player sent to each other:</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: opponent_is_bot]</strong></p>
<ul>
<li><p>You sent: <em>[player.messages or "(no message)"]</em></p></li>
<li><p>The other player's AI bot sent: <em>[opponent.messages or "(no message)"]</em></p></li>
</ul>
<p>Now you will choose between Choice A and Choice B.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: player_is_bot]</strong></p>
<ul>
<li><p>Your AI bot sent: <em>[player.messages or "(no message)"]</em></p></li>
<li><p>The other player sent: <em>[opponent.messages or "(no message)"]</em></p></li>
</ul>
<p>Now your bot will choose between Choice A and Choice B on your behalf.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p>Here are the messages you and the other player sent to each other:</p>
<ul>
<li><p>You sent: <em>[my_message or "(no message)"]</em></p></li>
<li><p>The other player sent: <em>[opponent_message or "(no message)"]</em></p></li>
</ul>
<p>Now you will choose between Choice A and Choice B.</p>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## BotThinking

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Please Wait"</strong></p>
<p>The AI is making its decision…</p>
<p>This may take a few seconds. Please do not close this page.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## WaitForBotDecision

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"wait_for_bot_decision"</strong></p>
<p>Please Wait The other participant’s AI is making its decision… Please wait a moment.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Decision

**Shown in:** condition_1, condition_2, condition_3, condition_4

**▸ Template variables:**

| **opponent_subject**           | player (c1, c2) \| player's AI bot (c3, c4)                                  |
|--------------------------------|------------------------------------------------------------------------------|
| **capitalized_player_subject** | You                                                                          |
| **player_subject**             | you                                                                          |
| **formatted_payoff_a**         | \$2.50                                                                       |
| **formatted_payoff_d**         | \$5.00                                                                       |
| **formatted_payoff_b**         | \$3.50                                                                       |
| **formatted_payoff_c**         | \$1.00                                                                       |
| **ai_conditions**              | False (c1, c2) \| True (c3, c4)                                              |
| **comm_conditions**            | False (c1, c3) \| True (c2, c4)                                              |
| **group_treatment**            | condition_1 (c1) \| condition_2 (c2) \| condition_3 (c3) \| condition_4 (c4) |
| **player_is_bot**              | False (c1, c2) \| False / True (c3, c4)                                      |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Decision – Game 2"</strong></p>
<p>Now you will have to make your decision. Below are the instructions from the previous page that you already read, for your reference.</p>
<p><strong>[IF: ai_conditions]</strong></p>
<p><em><strong>[↳ instructions_pd_stag_ai.html]</strong></em></p>
<p><em>You and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> are both facing the same two options to choose from: <strong>A</strong> or <strong>B</strong></em>. How much you and the other player each earn depends on the combination of the choices made by you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong>.</p>
<p>There are four possible outcomes:</p>
<ul>
<li><p>If you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> choose A, you and the other player will both receive $2.50.</p></li>
<li><p>If you and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> choose B, you and the other player will both receive $5.00.</p></li>
<li><p>If you choose A and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chooses B, you will receive $3.50 and the other player will receive $1.00.</p></li>
<li><p>If you choose B and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chooses A, you will receive $1.00 and the other player will receive $3.50.</p></li>
</ul>
<p>The bonus amounts for you and the other player can be summarized in the following table. <em>Within each of the four highlighted squares are the bonus amounts for each possible combination of choices</em>. Your bonus amount is <strong>listed first and in bold</strong>, and the other player's bonus amount is listed second. The other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> will be given the same information and will be choosing between the same choices as you.</p>
<p><strong>[ELSE]</strong></p>
<p><em><strong>[↳ instructions_pd_stag_humans.html]</strong></em></p>
<p><em>You and the other player are both facing the same two options to choose from: <strong>A</strong> or <strong>B</strong></em>. How much you and the other player each earn depends on the combination of the choices made by you and the other player.</p>
<p>There are four possible outcomes:</p>
<ul>
<li><p>If you both choose A, you and the other player will both receive $2.50.</p></li>
<li><p>If you both choose B, you and the other player will both receive $5.00.</p></li>
<li><p>If you choose A and the other player chooses B, you will receive $3.50 and they will receive $1.00.</p></li>
<li><p>If you choose B and the other player chooses A, you will receive $1.00 and they will receive $3.50.</p></li>
</ul>
<p>The bonus amounts for you and the other player can be summarized in the following table. <em>Within each of the four highlighted squares are the bonus amounts for each possible combination of your choice and the other player’s choice</em>. Your bonus amount is <strong>listed first and in bold</strong>, and the other player's bonus amount is listed second. The other player will be given the same information and will be choosing between the same choices as you.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: comm_conditions]</strong></p>
<h5 id="messages-exchanged-reminder-1">Messages Exchanged Reminder</h5>
<p><strong>[IF: ai_conditions]</strong></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p><strong>Here's a reminder of the messages your AI bot and the other player sent:</strong></p>
<ul>
<li><p>Your AI bot chose to send the message "<em>[my_message]</em>",</p></li>
<li><p>And the other player chose to send the message "<em>[opponent_message]</em>".</p></li>
</ul>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: opponent_is_bot]</strong></p>
<p><strong>Here's a reminder of the messages you and the other player's AI bot sent:</strong></p>
<ul>
<li><p>You chose to send the message "<em>[my_message]</em>",</p></li>
<li><p>And the other player's AI bot chose to send the message "<em>[opponent_message]</em>".</p></li>
</ul>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p><strong>Here's a reminder of the messages you and the other player sent:</strong></p>
<ul>
<li><p>You chose to send the message "<em>[my_message]</em>",</p></li>
<li><p>And the other player chose to send the message "<em>[opponent_message]</em>".</p></li>
</ul>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p><strong>[END IF]</strong></p>
<h5 id="decision-3">Decision</h5>
<p><strong>[IF: ai_conditions]</strong></p>
<p><strong>[IF: opponent_is_bot]</strong></p>
<p><strong>Please select your choice:</strong></p>
<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th></th>
<th></th>
<th>The other { player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</th>
<th></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td></td>
<td></td>
<td>Choice A</td>
<td>Choice B</td>
</tr>
<tr class="even">
<td>You</td>
<td>I choose Choice A</td>
<td>$2.50, $2.50</td>
<td>$3.50, $1.00</td>
</tr>
<tr class="odd">
<td></td>
<td>I choose Choice B</td>
<td>$1.00, $3.50</td>
<td>$5.00, $5.00</td>
</tr>
</tbody>
</table>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p><strong>Your bot made the following decision:</strong></p>
<p><strong>[IF: bot_cooperate]</strong></p>
<ul>
<li><p>Choice B</p></li>
</ul>
<p><strong>[ELSE]</strong></p>
<ul>
<li><p>Choice A</p></li>
</ul>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p><strong>Please select your choice:</strong></p>
<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th></th>
<th></th>
<th>The other { player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</th>
<th></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td></td>
<td></td>
<td>Choice A</td>
<td>Choice B</td>
</tr>
<tr class="even">
<td>You</td>
<td>I choose Choice A</td>
<td>$2.50, $2.50</td>
<td>$3.50, $1.00</td>
</tr>
<tr class="odd">
<td></td>
<td>I choose Choice B</td>
<td>$1.00, $3.50</td>
<td>$5.00, $5.00</td>
</tr>
</tbody>
</table>
<p><strong>[END IF]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## ResultsWaitPage

**Shown in:** condition_1, condition_2, condition_3, condition_4

*\[Default oTree WaitPage — no custom template; content below is the standard oTree waiting screen\]*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Please wait"</strong></p>
<p>Please wait for the other participants.</p>
<p><em>[A loading spinner is displayed automatically by the platform until all participants in the group have arrived at this point.]</em></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## GamesEnd

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>End of Games Message</p>
<p><strong>[IF: midgame_dropout]</strong></p>
<p>Unfortunately your partner left the game…</p>
<p>To complete your participation in the study please answer the following questions.</p>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p>Thanks for playing those two games! The responses have been recorded.</p>
<p>Please click next to reach the end of the study questionnaire.</p>
<p>────────────────────────────────────────────────</p>
<p><em>[Next button]</em></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# App: app_survey

## Survey1

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Survey"</strong></p>
<p><strong>[IF: midgame_dropout]</strong></p>
<p>Unfortunately your partner left the game…</p>
<p>To complete your participation in the study please answer the following questions.</p>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p>Finally, we’ll ask you to answer a few questions about yourself and your thoughts about and experience with artificial intelligence applications like ChatGPT and other large language models (“LLMs”).</p>
<p>────────────────────────────────────────────────</p>
<p><em>[Next button]</em></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Survey2

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Survey"</strong></p>
<p>Please answer the following questions.</p>
<p><em>[field.label]</em></p>
<p><em>[field]</em></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p>
<p>Please answer all questions before proceeding.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Survey3

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Survey"</strong></p>
<p>Please answer the following questions.</p>
<p><em>[field.label]</em></p>
<p><em>[field]</em></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p>
<p>Please answer all questions before proceeding.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Survey4

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Survey"</strong></p>
<p>Now, we would like to ask you some questions about yourself.</p>
<p><em>[field.label]</em></p>
<p><em>[field]</em></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p>
<p>Please answer all questions before proceeding.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Survey5

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>Survey</p>
<p>Now, we would like to ask you some questions about your political views.</p>
<p><em>[form.politics.label]</em></p>
<p><em>[form.politics]</em></p>
<p><em>[form.if_republican.label]</em></p>
<p><em>[form.if_republican]</em></p>
<p><em>[form.if_democrat.label]</em></p>
<p><em>[form.if_democrat]</em></p>
<p><em>[form.if_ind_other.label]</em></p>
<p><em>[form.if_ind_other]</em></p>
<p><em>[form.ideology.label]</em></p>
<p><em>[form.ideology]</em></p>
<p><strong>[IF: field.name not in 'politics if_republican if_democrat if_ind_other ideology']</strong></p>
<p><em>[field.label]</em></p>
<p><em>[field]</em></p>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p>
<p>Please answer all questions before proceeding.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## Survey6

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>Survey</p>
<p>To end the survey, we would like to ask you some questions about the games you just played.</p>
<p><strong>[IF: player_is_bot]</strong></p>
<p><em>[form.chose_B_game1.label]</em></p>
<p><strong>[ELSE]</strong></p>
<p><strong>[IF: is_condition_3_or_4]</strong></p>
<p><strong>How likely do you think it is that the other player's AI bot chose B in Game 1?</strong></p>
<p><strong>[ELSE]</strong></p>
<p><em>[form.chose_B_game1.label]</em></p>
<p><strong>[END IF]</strong></p>
<p><strong>[END IF]</strong></p>
<p><em>[form.chose_B_game1]</em></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p><em>[form.chose_B_game2.label]</em></p>
<p><strong>[ELSE]</strong></p>
<p><strong>[IF: is_condition_3_or_4]</strong></p>
<p><strong>How likely do you think it is that the other player's AI bot chose B in Game 2?</strong></p>
<p><strong>[ELSE]</strong></p>
<p><em>[form.chose_B_game2.label]</em></p>
<p><strong>[END IF]</strong></p>
<p><strong>[END IF]</strong></p>
<p><em>[form.chose_B_game2]</em></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p><em>[form.trust_ai_bot.label]</em></p>
<p><strong>[ELSE]</strong></p>
<p><strong>[IF: is_condition_3_or_4]</strong></p>
<p><strong>How trustworthy do you find the other player's AI bot?</strong></p>
<p><strong>[ELSE]</strong></p>
<p><em>[form.trust_ai_bot.label]</em></p>
<p><strong>[END IF]</strong></p>
<p><strong>[END IF]</strong></p>
<p><em>[form.trust_ai_bot]</em></p>
<p><strong>[IF: is_condition_3_or_4]</strong></p>
<p><strong>[IF: player_is_bot]</strong></p>
<p><strong>Please indicate the extent to which you agree or disagree with the following statements about the other player's behavior:</strong></p>
<p><strong>[ELSE]</strong></p>
<p><strong>Please indicate the extent to which you agree or disagree with the following statements about the other player's AI bot behavior:</strong></p>
<p><strong>[END IF]</strong></p>
<p><strong>[ELSE]</strong></p>
<p><strong>[END IF]</strong></p>
<table style="width:100%;">
<colgroup>
<col style="width: 16%" />
<col style="width: 16%" />
<col style="width: 16%" />
<col style="width: 16%" />
<col style="width: 16%" />
<col style="width: 16%" />
</colgroup>
<thead>
<tr class="header">
<th>Statement</th>
<th>Strongly Agree</th>
<th>Somewhat Agree</th>
<th>Neither Agree nor Disagree</th>
<th>Somewhat Disagree</th>
<th>Strongly Disagree</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>[form.intentions.label]</td>
<td>[IF: player.field_maybe_none('intentions') == 5]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('intentions') == 4]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('intentions') == 3]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('intentions') == 2]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('intentions') == 1]checked[END IF]&gt;</td>
</tr>
<tr class="even">
<td>[form.mind_of_its_own.label]</td>
<td>[IF: player.field_maybe_none('mind_of_its_own') == 5]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('mind_of_its_own') == 4]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('mind_of_its_own') == 3]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('mind_of_its_own') == 2]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('mind_of_its_own') == 1]checked[END IF]&gt;</td>
</tr>
<tr class="odd">
<td>[form.honest.label]</td>
<td>[IF: player.field_maybe_none('honest') == 5]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('honest') == 4]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('honest') == 3]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('honest') == 2]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('honest') == 1]checked[END IF]&gt;</td>
</tr>
<tr class="even">
<td>[form.selfish.label]</td>
<td>[IF: player.field_maybe_none('selfish') == 5]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('selfish') == 4]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('selfish') == 3]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('selfish') == 2]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('selfish') == 1]checked[END IF]&gt;</td>
</tr>
<tr class="odd">
<td>[form.sincere.label]</td>
<td>[IF: player.field_maybe_none('sincere') == 5]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('sincere') == 4]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('sincere') == 3]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('sincere') == 2]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('sincere') == 1]checked[END IF]&gt;</td>
</tr>
<tr class="even">
<td>[form.unbiased.label]</td>
<td>[IF: player.field_maybe_none('unbiased') == 5]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('unbiased') == 4]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('unbiased') == 3]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('unbiased') == 2]checked[END IF]&gt;</td>
<td>[IF: player.field_maybe_none('unbiased') == 1]checked[END IF]&gt;</td>
</tr>
</tbody>
</table>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Submit]</strong></p>
<p><strong>[IF: form.errors]</strong></p>
<p>Please answer all questions before proceeding.</p>
<p>For the final table, ensure that one option is selected for each row.</p>
<p><strong>[END IF]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# App: app_collect_results

## CollectResults

**Shown in:** condition_1, condition_2, condition_3, condition_4

**▸ Template variables:**

| **player_noun**   | You                                         |
|-------------------|---------------------------------------------|
| **opponent_noun** | player (c1, c2) \| player's AI bot (c3, c4) |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><h4 id="game-results">Game Results</h4>
<p>Before the study ends, this page will inform you about the game results and your bonus payment.</p>
<h5 id="game-1-results">Game 1 Results</h5>
<p>You chose [prisoner_decision], and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chose [prisoner_opponent_decision]. Hence, your payoff according to game 1 is [prisoner_payoff].</p>
<h5 id="game-2-results">Game 2 Results</h5>
<p>You chose [stag_decision], and the other <strong>{ player [IF condition = c1, c2] | player's AI bot [IF condition = c3, c4] }</strong> chose [stag_opponent_decision]. Hence, your payoff according to game 2 is [stag_payoff].</p>
<h4 id="your-bonus-payment">Your Bonus Payment</h4>
<p><strong>[IF: game_1_is_selected]</strong></p>
<h5 id="the-experiment-randomizer-has-choosen-game-1-as-the-game-to-define-your-bonus">The experiment randomizer has choosen Game 1 as the game to define your bonus</h5>
<p>Therefore, your <strong>bonus payment is equal to [prisoner_payoff]</strong>.</p>
<p><strong>[ELSE]</strong></p>
<h5 id="the-experiment-randomizer-has-choosen-game-2-as-the-game-to-define-your-bonus">The experiment randomizer has choosen Game 2 as the game to define your bonus</h5>
<p>Therefore, your <strong>bonus payment is equal to [stag_payoff]</strong>.</p>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Next Page]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# App: app_debriefing

## Debrief_Parent

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"Debriefing"</strong></p>
<p><strong>[IF: timed_out_flag]</strong></p>
<p><em><strong>[↳ debrief_timeout.html]</strong></em></p>
<p><em>Thanks for participating in our study! We literally can’t do our research without willing and engaged participants like you.</em> Because you are such an important part of what we do, we want to give you more information about the study. First, we want to reiterate that everything we told you in the study is 100% accurate and true. You were matched with another participant, but unfortunately, your partner exited the experiment before completing both games. As explained earlier, the bonus payments were structured based on the combined choices of you and your partner, and therefore, in order for the bonus to be awarded, both participants needed to finish both games. As you might have guessed by the survey questions, our interest is in understanding the effects advances in artificial intelligence (especially things like ChatGPT) have on human cooperation. Approximately 100 other participants like you will take part in similar versions of the study, some facing slightly different scenarios, including sessions where one side's decisions were made by a live AI connected in real time to OpenAI's GPT server rather than entered directly by that participant. All participants have received accurate and complete information about how choices and payments were designed.</p>
<p><strong>[ELSE]</strong></p>
<p><strong>[IF: is_condition_1]</strong></p>
<p><em><strong>[↳ debrief_cond1.html]</strong></em></p>
<p><em>Thanks for participating in our study! We literally can’t do our research without willing and engaged participants like you</em>. Because you are such an important part of what we do, we want to give you more information about the study. First, we want to reiterate that everything we told you in the study is 100% true. You were matched with another participant and both you and the other participant will be paid bonuses based on the combination of choices you and they made. As you might have guessed by the survey questions, our interest is in understanding the effects advances in artificial intelligence (especially things like ChatGPT) on human cooperation. Approximately 100 other participants like you will take part in the same version of the study that you just did. Others faced slightly different scenarios. Some will face the same decision between A and B, but also had the opportunity to send a free-text message (in their own words) to one another before choosing A or B. Others, while paired with another participant who got paid based on the combined choices of A and B, instead faced decisions made by a live AI connected in real time to OpenAI's GPT server. In those sessions, the GPT model made the same set of decisions you did, but on behalf of the other participant. The other participant will be paid based on the combination of the other player's choices and the AI's choices made on their behalf. In that version all participants were also given accurate and full information about how the choices and payments were designed.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: is_condition_2]</strong></p>
<p><em><strong>[↳ debrief_cond2.html]</strong></em></p>
<p><em>Thanks for participating in our study! We literally can’t do our research without willing and engaged participants like you</em>. Because you are such an important part of what we do, we want to give you more information about the study. First, we want to reiterate that everything we told you in the study is 100% true. You were matched with another participant and both you and the other participant will be paid bonuses based on the combination of choices you and they made. As you might have guessed by the survey questions, our interest is in understanding the effects advances in artificial intelligence (especially things like ChatGPT) on human cooperation. Approximately 100 other participants like you will take part in the same version of the study that you just did. Others faced slightly different scenarios. Some will face the same decision between A and B, but without the opportunity to send messages. Others, while paired with another participant who got paid based on the combined choices of A and B, instead faced decisions made by a live AI connected in real time to OpenAI's GPT server. In those sessions, the GPT model made the same set of decisions you did, but on behalf of the other participant. The other participant will be paid based on the combination of the other player's choices and the AI's choices made on their behalf. In that version all participants were also given accurate and full information about how the choices and payments were designed.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: is_condition_3]</strong></p>
<p><em><strong>[↳ debrief_cond3.html]</strong></em></p>
<p><em>Thanks for participating in our study! We literally can’t do our research without willing and engaged participants like you.</em> Because you are such an important part of what we do, we want to give you more information about the study. First, we want to reiterate that everything we told you in the study is 100% accurate and true. You were matched with another participant and both you and the other participant will be paid bonuses based on the combination of choices made in the game. If you were the one making choices, then the payments will be based on the choices you made and the choices made by a live AI on behalf of the other participant. If a bot was playing on your behalf, then you will be paid based on the choices made by your AI and the choices made by the other participant. As you might have guessed, our interest is in understanding the effects advances in artificial intelligence (especially things like ChatGPT) on human cooperation. Approximately 100 other participants like you will take part in the same version of the study that you just did. Others faced slightly different scenarios. Some will face the same decision between A and B, but also had the opportunity to send a free-text message (in their own words) to one another before choosing A or B. Others were simply randomly matched with another participant who had completed the same version. They were all in fact paid on the actual combination of decisions that the two players made. They were also fully informed by us about how the choices and payments were designed, and everything we told them was entirely accurate.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[IF: is_condition_4]</strong></p>
<p><em><strong>[↳ debrief_cond4.html]</strong></em></p>
<p><em>Thanks for participating in our study! We literally can't do our research without willing and engaged participants like you.</em> Because you are such an important part of what we do, we want to give you more information about the study. First, we want to reiterate that everything we told you in the study is 100% accurate and true.</p>
<p><strong>[IF: player_is_bot]</strong></p>
<p>You were matched with another participant who made decisions directly in the game. As you were told, an AI played on your behalf — it received the same game instructions as the active participant and made every choice in your place. <strong>Your bonus is based on the combination of the AI's choices (made for you) and the other participant's choices.</strong></p>
<p>Before the final choice was made, both sides had the opportunity to send a free-text message. The AI composed and sent a message on your behalf, and the other participant sent a message to your side. Both messages were exchanged before the final decisions were made.</p>
<p><strong>[ELSE]</strong></p>
<p>You were matched with another participant whose decisions were made by an AI acting on their behalf — as you were told, that participant did not make choices directly. The AI received the same game instructions you did and made every choice in their place. <strong>Your bonus is based on the combination of your choices and the AI's choices on behalf of the other participant.</strong></p>
<p>Before the final choice, both sides had the opportunity to send a free-text message. You composed and sent a message to the other participant's side, and the AI composed and sent a message to you on behalf of the other participant. Both messages were exchanged before the final decisions were made.</p>
<p><strong>[END IF]</strong></p>
<p>As you might have guessed, our interest is in understanding how advances in artificial intelligence (especially things like ChatGPT) affect human cooperation. Approximately 100 other participants like you will take part in the same version of the study that you just did. Others faced slightly different scenarios: some were paired with an AI without the opportunity to exchange messages first; others were matched with another human participant who made decisions directly, either with or without free-text messaging. All participants were fully informed about how choices and payments were designed, and everything we told them was entirely accurate.</p>
<p><strong>[END IF]</strong></p>
<p><strong>[END IF]</strong></p>
<p>────────────────────────────────────────────────</p>
<p><strong>[Button: Submit and Finish the Study]</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## End

**Shown in:** condition_1, condition_2, condition_3, condition_4

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>"End of Study"</strong></p>
<p>We thank you for your time spent participating in this study.</p>
<p>Your responses have been recorded.</p>
<p>Please remain seated and wait for other participants to finish.</p>
<p>Lab administrators will provide further instructions and compute your payment.</p>
<p>Do not close this page until you are instructed to do so.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>
