Ultra-think.

## Goal
To guide an AI assistant in creating a detailed Product Requirements Document (PRD) in Markdown. The PRD should be clear, 
actionable, and suitable for a junior developer to understand and implement the feature.  It should be based on the prompt:

$ARGUMENTS

## Variables
Variables will be prefixed with `$` and should be used to dynamically generate file names and content.

```
$task_name := Suitable task name in snake_case format, derived from the prompt.
$YYYYmmdd_hhmmsss := Current date and time in YYYYmmdd_hhmmsss format, e.g., 20231001_123456
$questions_file := "tasks/" $task_name + "_prd_questions_" + $YYYYmmdd_hhmmsss + ".md"
$prd_file := "tasks/" $task_name + "_prd_" + $YYYYmmdd_hhmmsss + ".md"
```

## Process
* **Prepare Clarifying Questions:** AI *must* ask clarifying questions to gather sufficient detail: Analyze the user prompt
and think carefully about it from each dimension. Itemize every single point of uncertainty. Then, prepare a list of clarifying 
questions that remove all of these uncertainties. The goal is to understand the "what" and "why" of the feature, not necessarily 
the "how" (which the developer will figure out). Provide options in letter/number lists so I can respond easily with my selections.
Each clarifying question should list out reasonable options for the user to choose from, tag recommended options and  allow them 
to specify their own answer.  

Use the format below:

```markdown
* Question: Since @PreAuthorize with .block() can cause thread blocking in reactive applications, which approach should we take?
[ ] (Recommended) Option A: Create a custom @RateLimited annotation with a reactive WebFilter that processes before the controller method
[ ] Option B: Use a reactive service method in @PreAuthorize that returns Mono<Boolean> without blocking
[ ] Option C: Accept the blocking behavior for now and optimize later
[ ] Other:
```
*  **Write out the questions:** Write out the clarifying questions to `$questions_file`.  Ask the user to respond to these questions.
*  **Generate PRD:** Based on the initial prompt and the user's answers to the clarifying questions, generate a PRD using the structure outlined below in the **PRD Structure** section.
*  **Save PRD:** Save the generated document into `$prd_file`

## Clarifying Questions (Examples)

The AI should adapt its questions based on the prompt, but here are some common areas to explore:

*   **Problem/Goal:** "What problem does this feature solve for the user?" or "What is the main goal we want to achieve with this feature?"
*   **Target User:** "Who is the primary user of this feature?"
*   **Core Functionality:** "Can you describe the key actions a user should be able to perform with this feature?"
*   **User Stories:** "Could you provide a few user stories? (e.g., As a [type of user], I want to [perform an action] so that [benefit].)"
*   **Acceptance Criteria:** "How will we know when this feature is successfully implemented? What are the key success criteria?"
*   **Scope/Boundaries:** "Are there any specific things this feature *should not* do (non-goals)?"
*   **Data Requirements:** "What kind of data does this feature need to display or manipulate?"
*   **Design/UI:** "Are there any existing design mockups or UI guidelines to follow?" or "Can you describe the desired look and feel?"
*   **Edge Cases:** "Are there any potential edge cases or error conditions we should consider?"

## PRD Structure

The generated PRD should include the following sections:

1.  **Introduction/Overview:** Briefly describe the feature and the problem it solves. State the goal.
2.  **Goals:** List the specific, measurable objectives for this feature.
3.  **User Stories:** Detail the user narratives describing feature usage and benefits.
4.  **Functional Requirements:** List the specific functionalities the feature must have. Use clear, concise language (e.g., 
    "The system must allow users to upload a profile picture."). Number these requirements.
5.  **Non-Goals (Out of Scope):** Clearly state what this feature will *not* include to manage scope.
6.  **Design Considerations (Optional):** Link to mockups, describe UI/UX requirements, or mention relevant components/styles if applicable.
7.  **Technical Considerations (Optional):** Mention any known technical constraints, dependencies, or suggestions 
    (e.g., "Should integrate with the existing Auth module").
8.  **Success Metrics:** How will the success of this feature be measured? (e.g., "Increase user engagement by 10%", 
    "Reduce support tickets related to X").
9.  **Open Questions:** List any remaining questions or areas needing further clarification.

## Target Audience

Assume the primary reader of the PRD is a **junior developer**. Therefore, requirements should be explicit, unambiguous, 
and avoid jargon where possible. Provide enough detail for them to understand the feature's purpose and core logic.

## Output

*   **Format:** Markdown (`.md`)
*   **Location:** `/tasks/`

## Final instructions

1. Do NOT start implementing the PRD
2. Make sure to ask the user clarifying questions
3. Take the user's answers to the clarifying questions and improve the PRD