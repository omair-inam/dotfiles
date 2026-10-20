# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit Task `model`). Alias entries in a panel list still count toward its fan-out.
# budget: medium (high), with per-role overrides
feature, refactoring: opus high
bug-fix: sonnet high
perf-issue: opus high
hillclimb: opus xhigh
judgment and prose: opus high
hardest tasks: opus xhigh
how explorer: sonnet medium
how explainer: opus medium
why investigators: sonnet medium
why synthesizer: opus high
reflect tooling: sonnet medium
reflect judgment, divergent, synthesizer: opus high
arena runners: opus high, fable high, sonnet high
arena cross-judge pool: opus high, fable high, sonnet high
swarm workers: sonnet high
architect runners: opus high, fable high, sonnet high
interrogate reviewers: opus high, fable high, sonnet high
