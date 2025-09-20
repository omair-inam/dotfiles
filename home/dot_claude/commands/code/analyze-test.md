---
allowed-tools: Bash(grep:*), Bash(find:*), Bash(wc:*), Bash(head:*), Bash(tail:*)
description: Comprehensive assessment of unit test quality with actionable improvement suggestions
---

# Unit Test Quality Assessment

## Context
Analyze the provided unit test file(s) to assess their quality, completeness, and adherence to testing best practices.

## Target Files
$ARGUMENTS

## Assessment Criteria

### 1. Test Coverage Analysis
- **Completeness:** Are all public methods tested?
- **Edge Cases:** Are boundary conditions and edge cases covered?
- **Error Scenarios:** Are exception cases and error paths tested?
- **Happy Path:** Are typical use cases thoroughly tested?

### 2. Test Structure & Organization
- **Naming Convention:** Do test names clearly describe what is being tested?
- **Test Independence:** Can tests run in any order without affecting each other?
- **Setup/Teardown:** Is test initialization and cleanup properly handled?
- **Test Grouping:** Are related tests logically organized?

### 3. Test Quality Metrics
- **Assertions:**
    - Are assertions specific and meaningful?
    - Is there at least one assertion per test?
    - Are assertions testing the right things?
- **Mocking:**
    - Is mocking used appropriately (not over-mocked)?
    - Are dependencies properly isolated?
    - Are mock verifications meaningful?
- **Test Data:**
    - Is test data realistic and representative?
    - Are magic numbers avoided in favor of named constants?
    - Is test data properly parameterized where applicable?

### 4. Readability & Maintainability
- **Arrange-Act-Assert Pattern:** Do tests follow AAA or Given-When-Then structure?
- **Code Duplication:** Is common setup extracted to helper methods?
- **Comments:** Are complex test scenarios adequately documented?
- **Test Size:** Are tests focused on single behaviors (not testing multiple things)?

### 5. Performance Considerations
- **Test Speed:** Are tests reasonably fast?
- **Resource Management:** Are resources (files, connections, etc.) properly cleaned up?
- **Integration vs Unit:** Are true unit tests separated from integration tests?

### 6. Framework-Specific Best Practices
- **Annotations:** Are framework annotations used correctly?
- **Parameterized Tests:** Are data-driven tests used where appropriate?
- **Test Fixtures:** Are shared test fixtures used efficiently?

## Output Format

Provide assessment in the following structure:

### 📊 Overall Assessment
[High-level summary of test quality - Excellent/Good/Needs Improvement/Poor]

### ✅ Strengths
- [List what the tests do well]

### ⚠️ Areas for Improvement
- [List specific issues found]

### 🔧 Actionable Recommendations
1. **Critical Issues** (Must Fix)
    - [Issues that could cause test failures or false positives]

2. **Important Improvements** (Should Fix)
    - [Issues affecting maintainability or coverage]

3. **Nice to Have** (Could Fix)
    - [Minor improvements for better practices]

### 📝 Specific Code Examples
```[language]
// Current approach
[problematic code snippet]

// Recommended approach
[improved code snippet]
```

### 📈 Metrics Summary
- Test Count: [number]
- Average Assertions per Test: [number]
- Mocked Dependencies: [number]
- Test Coverage Estimate: [percentage or qualitative assessment]
- Code Smells Identified: [number]

### 🎯 Priority Actions
1. [Most important change to make]
2. [Second priority]
3. [Third priority]

## Additional Considerations

- If multiple test files are provided, assess them collectively and note patterns
- Consider the testing framework being used (JUnit, Jest, pytest, etc.)
- Evaluate against language-specific idioms and conventions
- Check for anti-patterns specific to the testing framework
- Consider the balance between test thoroughness and maintainability

## Notes
- Focus on providing constructive, actionable feedback
- Prioritize improvements by impact on test reliability and maintainability
- Include code examples for complex recommendations
- Consider the context and type of code being tested (e.g., business logic vs. infrastructure)