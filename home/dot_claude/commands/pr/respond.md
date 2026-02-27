---
allowed-tools: Task, Bash(echo:*), Bash(gh auth status:*), Bash(gh pr view:*), Bash(gh repo view:*), Bash(gh pr list:*), Bash(gh api:*), Bash(git branch:*), Bash(git status:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(./mvnw test:*), Bash(rg:*), Bash(date:*), Read, Write, Edit, MultiEdit, Grep
description: Interactive PR comment response system with automated code changes and reply posting
---

## Context

- Session ID: !`date +%s%N`
- Current branch: !`git branch --show-current 2>/dev/null || echo "detached-head"`
- Repository: !`gh repo view --json nameWithOwner,url --jq '.nameWithOwner // "unknown"' 2>/dev/null || echo "unknown"`
- GitHub auth status: !`gh auth status 2>&1 | head -1 || echo "Not authenticated"`

## Your task

**CRITICAL: This command provides an interactive system for responding to PR review comments with automated code changes and reply posting.**

STEP 1: Initialize PR response session

- CREATE session state: `/tmp/pr-respond-state-$SESSION_ID.json`
- INITIALIZE response session with timestamp and context
- PARSE arguments from $ARGUMENTS for PR number
- SET session data:
  ```json
  {
    "sessionId": "$SESSION_ID",
    "timestamp": "ISO_8601_TIMESTAMP",
    "prNumber": null,
    "repository": "auto-detect",
    "responsePhase": "initialization",
    "comments": [],
    "responsePlan": "/tmp/pr-responses-$SESSION_ID.md",
    "completedResponses": [],
    "errorLog": []
  }
  ```

STEP 2: Parse arguments and validate PR

IF $ARGUMENTS is empty:
- FETCH current branch PR: `gh pr list --head $(git branch --show-current) --json number,title,state`
- IF current branch has PR, use that PR number
- ELSE prompt for PR number

ELSE IF $ARGUMENTS is numeric:
- SET prNumber = $ARGUMENTS
- VALIDATE PR exists and is accessible

ELSE:
- LOG invalid arguments to session state
- PROVIDE usage examples

STEP 3: Retrieve PR review comments comprehensively

TRY:

- FETCH PR metadata: `gh pr view $PR_NUMBER --json title,body,state,author,url,number`
- SAVE PR metadata to: `/tmp/pr-respond-$SESSION_ID/pr-metadata.json`

**RETRIEVE ALL REVIEW COMMENTS:**

- FETCH review comments: 
  ```bash
  gh api -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" \
    "/repos/{owner}/{repo}/pulls/$PR_NUMBER/comments" \
    --jq '.[] | {id, body, path, line, original_line, diff_hunk, user: .user.login, created_at, updated_at, html_url, in_reply_to_id}'
  ```

- FETCH general PR comments:
  ```bash
  gh api -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" \
    "/repos/{owner}/{repo}/issues/$PR_NUMBER/comments" \
    --jq '.[] | {id, body, user: .user.login, created_at, updated_at, html_url}'
  ```

- SAVE all comments to: `/tmp/pr-respond-$SESSION_ID/all-comments.json`

CATCH (github_api_error):
- LOG API errors to session state
- CHECK GitHub authentication status
- PROVIDE troubleshooting guidance

STEP 4: Generate interactive response plan

**CREATE comprehensive response markdown file:**

- ANALYZE each comment for:
  - Comment type (code review, general feedback, question)
  - Actionable items vs informational
  - File references and line numbers
  - Required response type (code change, explanation, clarification)

**GENERATE response options for each comment:**

FOR EACH comment:
- CREATE checkbox item with comment reference
- GENERATE idea:// link to relevant file (if applicable)
- PROVIDE 3-4 response options:
  - Code change option (if applicable)
  - Comment response with reasoning
  - Clarification request
  - "Other" option for custom response
- MARK recommended option based on comment analysis

**RESPONSE PLAN TEMPLATE:**
```markdown
# PR Response Plan - PR #$PR_NUMBER

## Summary
- **PR Title**: $PR_TITLE  
- **Total Comments**: $COMMENT_COUNT
- **Files Affected**: $FILES_LIST
- **Response Session**: $SESSION_ID

---

## Review Comments to Address

### Comment 1 - [Username] on [$FILENAME:$LINE](idea://open?file=$FILEPATH&line=$LINE)
> $COMMENT_BODY

**Context**: $DIFF_HUNK_CONTEXT

- [ ] **Option A**: Make code change - $SUGGESTED_CHANGE
- [ ] **Option B**: Respond with comment - $SUGGESTED_RESPONSE *(RECOMMENDED)*
- [ ] **Option C**: Request clarification - $CLARIFICATION_REQUEST  
- [ ] **Other**: *(specify custom response)*

**Analysis**: $AUTOMATED_ANALYSIS

---

### Comment 2 - [Username] on General Discussion
> $COMMENT_BODY

- [ ] **Option A**: Acknowledge and explain approach - $EXPLANATION
- [ ] **Option B**: Implement suggested improvement - $IMPROVEMENT_PLAN
- [ ] **Other**: *(specify custom response)*

---

## Instructions
1. Review each comment and select your preferred response option
2. Edit any response text as needed
3. Add any custom responses in "Other" sections
4. Save this file and type "Go" to begin execution
```

**SAVE response plan to**: `/tmp/pr-responses-$SESSION_ID.md`

**GENERATE idea:// link for the response plan file**

STEP 5: Present response plan to user

- DISPLAY response plan summary:
  - Total comments found
  - Types of comments (code review, general, questions)  
  - Recommended actions breakdown
  
- PROVIDE idea:// link: `idea://open?file=/tmp/pr-responses-$SESSION_ID.md`

- PROMPT user: "Please review and edit the response plan, then type 'Go' to begin execution."

- WAIT for "Go" command from user

STEP 6: Execute response plan (triggered by "Go" command)

**PARSE updated response plan file for selected options**

FOR EACH comment with selected response:

CASE response_type:
WHEN "code_change":

TRY:
- READ file referenced in comment
- APPLY suggested code change using Edit/MultiEdit tools
- VALIDATE syntax and basic correctness
- RUN tests: `./mvnw test`
- IF tests fail:
  - ANALYZE test failures
  - FIX failing tests
  - RE-RUN tests until passing

- PROMPT user: "Code changes made and tests passing. Commit this change? (y/N)"
- IF user confirms:
  - STAGE changes: `git add .`
  - COMMIT with descriptive message: `git commit -m "Address PR comment: $COMMENT_SUMMARY\n\nRef: $COMMENT_URL"`
  - PUSH to PR branch: `git push`

CATCH (test_failure):
- LOG test failures
- PROMPT user for manual intervention
- PROVIDE test failure details

WHEN "comment_response":
- EXTRACT selected response text from response plan
- POST reply to review comment:
  ```bash
  gh api --method POST \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "/repos/{owner}/{repo}/pulls/$PR_NUMBER/comments/$COMMENT_ID/replies" \
    -f "body=$RESPONSE_TEXT"
  ```

WHEN "general_comment":
- POST general PR comment:
  ```bash
  gh api --method POST \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "/repos/{owner}/{repo}/issues/$PR_NUMBER/comments" \
    -f "body=$RESPONSE_TEXT"
  ```

- UPDATE session state with completed response
- MARK comment as addressed in response plan

STEP 7: Session completion and summary

- UPDATE session state with:
  - All responses executed
  - Code changes committed and pushed  
  - Comments posted successfully
  - Any errors or skipped items

- GENERATE completion summary:
  - Total comments addressed: X/Y
  - Code changes made: X files modified
  - Comments posted: X replies
  - Commits created: X
  - Time taken: X minutes

- ARCHIVE session files: `/tmp/pr-respond-archive-$SESSION_ID/`
- CLEAN UP temporary files (keeping archive)

## Implementation Details

**Comment Analysis Patterns:**

```bash
# Detect code change requests
rg -i "rename|refactor|change|move|extract|should be|consider" /tmp/pr-respond-$SESSION_ID/all-comments.json

# Detect questions requiring clarification
rg -i "why|how|what.*think|clarify|explain" /tmp/pr-respond-$SESSION_ID/all-comments.json

# Detect suggestions vs requirements
rg -i "suggest|recommend|might|could" /tmp/pr-respond-$SESSION_ID/all-comments.json
```

**File Reference Resolution:**

```bash
# Extract file paths from review comments
jq -r '.[] | select(.path != null) | "\(.path):\(.line // .original_line)"' \
  /tmp/pr-respond-$SESSION_ID/all-comments.json > /tmp/pr-respond-$SESSION_ID/file-references.txt

# Generate idea:// links for each file reference
while read -r fileref; do
  file=$(echo "$fileref" | cut -d: -f1)
  line=$(echo "$fileref" | cut -d: -f2)
  echo "idea://open?file=$PWD/$file&line=$line"
done < /tmp/pr-respond-$SESSION_ID/file-references.txt
```

**Response Option Generation Logic:**

```javascript
// Pseudo-code for response option generation
function generateResponseOptions(comment) {
  const options = [];
  
  if (containsCodeSuggestion(comment.body)) {
    options.push({
      type: 'code_change',
      description: extractSuggestedChange(comment.body),
      action: 'implement_suggestion'
    });
  }
  
  if (isQuestion(comment.body)) {
    options.push({
      type: 'comment_response', 
      description: generateExplanation(comment.body),
      recommended: true
    });
  }
  
  options.push({
    type: 'custom',
    description: 'Other: (specify custom response)'
  });
  
  return options;
}
```

**Test Execution and Failure Handling:**

```bash
# Run tests with detailed output
./mvnw test 2>&1 | tee /tmp/pr-respond-$SESSION_ID/test-output.log

# Parse test failures
if [ $? -ne 0 ]; then
  echo "Tests failed. Analyzing failures..."
  
  # Extract failed test names
  rg "FAILED.*Test" /tmp/pr-respond-$SESSION_ID/test-output.log | \
    sed 's/.*FAILED.*\(.*Test\).*/\1/' > /tmp/pr-respond-$SESSION_ID/failed-tests.txt
  
  # Provide failure summary
  echo "Failed tests:"
  cat /tmp/pr-respond-$SESSION_ID/failed-tests.txt
fi
```

**Commit Message Templates:**

- **Code Change**: `Address PR comment: {brief_description}\n\nImplemented suggested change in {file_name}.\n\nRef: {comment_url}`
- **Test Fix**: `Fix tests after addressing PR comment\n\nUpdated tests to reflect changes in {file_name}.\n\nRef: {comment_url}`
- **Refactoring**: `Refactor {component} per PR feedback\n\n{detailed_description}\n\nRef: {comment_url}`

**Error Recovery & Fallback:**

- **API Rate Limiting**: Implement exponential backoff for GitHub API calls
- **Test Failures**: Provide detailed failure analysis and manual intervention prompts
- **File Not Found**: Skip file-specific responses, continue with general comments
- **Permission Denied**: Fallback to manual instructions for user execution

**Progress Tracking:**

```bash
# Real-time progress indicator
echo "Progress: $COMPLETED_RESPONSES/$TOTAL_COMMENTS responses processed"
echo "- Code changes: $CODE_CHANGES_MADE"
echo "- Comments posted: $COMMENTS_POSTED" 
echo "- Errors: $ERROR_COUNT"
```

**Session State Management:**

```json
{
  "sessionId": "1234567890123",
  "prNumber": 42,
  "repository": "owner/repo",
  "totalComments": 5,
  "responses": [
    {
      "commentId": "comment_123",
      "type": "code_change",
      "status": "completed",
      "commitSha": "abc123",
      "timestamp": "2024-01-01T12:00:00Z"
    },
    {
      "commentId": "comment_456", 
      "type": "comment_response",
      "status": "posted",
      "replyId": "reply_789",
      "timestamp": "2024-01-01T12:05:00Z"
    }
  ],
  "errors": []
}
```