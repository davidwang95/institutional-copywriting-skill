# Validation scope

Release review date: 6 October 2026.

This package uses a shared `SKILL.md` with `name` and `description` frontmatter and relative supporting references. Installation paths and invocation syntax were checked against the official documentation linked in [SOURCES.md](SOURCES.md).

## Checks performed

- The bundled skill-creator `quick_validate.py` accepted the skill metadata and instructions.
- The dependency-free package validator passed, including frontmatter, local references, and the ten-case fixture schema.
- All 24 unit tests passed. They cover malformed inputs, duplicate IDs and JSON keys, missing or unknown outputs, local-link errors, and limits of literal diagnostics.
- The fixture smoke check passed for all ten synthetic cases: ten acceptable examples passed their literal checks and ten deliberately rejected examples failed them. These are harness checks, not model-quality results.
- The selected public files were reviewed as UTF-8 text resources and scanned for private input identifiers, local source paths, and credential patterns. The package contains no source PDFs, slide decks, extracted source text, or source images.
- The Windows PowerShell installation copy was exercised in isolated project directories for both `.agents/skills` and `.claude/skills`. Every copied skill file matched its source SHA-256. This verifies the copy procedure, not client discovery or activation.
- Three fresh synthetic requests were completed by an independent delegated agent that explicitly read the skill and did not read the fixture outputs. The agent and publishing reviewer checked the responses for preserved meaning and institutional register. All three passed; see the source prompts, actual outputs, and review notes in [holdout-review.md](evals/holdout-review.md).

## Limits

Structural checks and literal fixture diagnostics do not prove semantic correctness. A review must still compare each material assertion with its source, including numbers, units, periods, attribution, conditions, and the strength of the claim.

This release has not been installed or invoked in live Codex and Claude Code clients. Automatic discovery, slash-command routing, reload behavior, and cross-client runtime behavior remain unverified. No claim of ASD-STE100 compliance, factual certification, or AI-authorship detection is made.

All published scenarios and examples are original and synthetic. Private style-study inputs are excluded from the package.
