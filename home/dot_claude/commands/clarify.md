## My question
$ARGUMENTS

## Your task
Analyze the user prompt and think carefully about it from each dimension. Itemize every single point of uncertainty. Then, prepare a list of clarifying
questions that remove all of these uncertainties. For each question provide options in letter/number lists so I can respond easily with my selections.

Example output:

```markdown
Clarifying Questions:
  1. Output Format - What should the jq script return?
  - A. (Recommended) Boolean (true/false)
  - B. Exit code only (0 for success/has session, 1 for no session)
  - C. A message like "Active session found" or "No active session"
  - D. The actual session_info object(s) if found, empty otherwise
  - Other:

  2. Session Detection Logic - What constitutes an "active" session?
  - A. Any non-empty session_info object (has any properties)
  - B. Specifically check for access_token field in session_info
  - C. (Recommended) Check for both access_token AND refresh_token
  - D. Check that status is "ready" AND session_info is non-empty
  - Other:
```
