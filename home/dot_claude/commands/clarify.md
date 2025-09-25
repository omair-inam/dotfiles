$ARGUMENTS

Analyze the user prompt and think carefully about it from each dimension. Itemize every single point of uncertainty. Then, prepare a list of clarifying
questions that remove all of these uncertainties. For each question provide options in letter/number lists so I can respond easily with my selections.

Example:

```markdown
* Question: Since @PreAuthorize with .block() can cause thread blocking in reactive applications, which approach should we take?
[ ] Option A: Create a custom @RateLimited annotation with a reactive WebFilter that processes before the controller method
[ ] Option B: Use a reactive service method in @PreAuthorize that returns Mono<Boolean> without blocking
[ ] Option C: Accept the blocking behavior for now and optimize later
[ ] Other:
```