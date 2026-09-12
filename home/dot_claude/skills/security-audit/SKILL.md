---
name: security-audit
description: Perform a comprehensive security audit of the current project's codebase to determine whether it is safe to build, install, and run locally. Use when asked to audit, review security, check for vulnerabilities, assess safety of a codebase, or evaluate whether a project is safe to install. Covers injection attacks, auth flaws, sensitive data exposure, input validation, dependency risks, configuration issues, and supply chain concerns.
---

# Security Audit

Perform a security audit of the current project's codebase. The goal is to determine whether it is safe to build, install, and run locally.

## Approach

1. **Orient first.** Read the project README, build files, dependency manifests, and entrypoints to understand the language, framework, and architecture before diving into code.
2. **Map the attack surface.** Identify all points where the application accepts external input: CLI arguments, environment variables, config files, network listeners, IPC, file reads, deserialization boundaries, and plugin/extension loading.
3. **Audit systematically** across every category below. Use Grep and file reads — do not guess.
4. **Check dependencies.** Run the ecosystem's audit tool if available (e.g., `npm audit`, `pip-audit`, `cargo audit`, `govulncheck`, `bundler-audit`). Report any known CVEs.
5. **Review build/install scripts.** Examine `Makefile`, `setup.py`, `postinstall` hooks, Docker entrypoints, and similar — these execute with the user's privileges during install.

## Vulnerability Categories

Assess each category. If no issues are found in a category, state that explicitly.

| # | Category | What to look for |
|---|----------|-----------------|
| 1 | **Injection** | SQL injection, command injection (shell exec with unsanitized input), template injection, XSS, prompt injection, LDAP injection |
| 2 | **Authentication & Authorization** | Broken access controls, hardcoded credentials, insecure token handling, missing auth checks, privilege escalation paths |
| 3 | **Sensitive Data Exposure** | Secrets in source code, API keys/tokens in config or logs, unencrypted storage of sensitive data, overly verbose error messages leaking internals |
| 4 | **Input Validation** | Unvalidated user input, missing boundary checks, path traversal, unsafe deserialization, regex denial-of-service (ReDoS) |
| 5 | **Dependency Risk** | Known CVEs, outdated packages with available security patches, typosquatting concerns, overly broad dependency trees for the project's scope |
| 6 | **Configuration & Infrastructure** | Insecure defaults, debug mode enabled in production, permissive CORS, missing security headers, exposed management endpoints, overly permissive file permissions |
| 7 | **Supply Chain & Build** | Suspicious `postinstall`/build hooks, pinning practices (lockfiles present?), fetching remote resources during build, unsigned artifacts |

## Reporting Format

For each vulnerability found, report:

- **Location:** File path and line number
- **Severity:** Critical / High / Medium / Low
- **Category:** Which category above (by number)
- **Description:** What the vulnerability is and a concrete exploitation scenario
- **Remediation:** A specific, actionable fix (not generic advice)

## Output Structure

1. **Executive Summary** — One paragraph: overall risk assessment and whether the project appears safe to install and run locally.
2. **Findings** — Grouped by severity (Critical first, then High, Medium, Low). Use the reporting format above for each finding.
3. **Dependency Audit Results** — Output from the ecosystem's audit tool, or a note if none is available.
4. **Positive Observations** — Briefly note any good security practices observed (e.g., input validation, least privilege, dependency pinning).
5. **Verdict** — A clear, one-line recommendation: safe to use locally, safe with caveats, or not recommended (with explanation).
