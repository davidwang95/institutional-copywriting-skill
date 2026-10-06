# Evaluating institutional copywriting

This evaluation uses original, synthetic inputs about invented firms Alpha and Orion. The fixtures contain no private client material and are not statements about real entities. They test preservation of meaning during rewriting, not investment accuracy or the quality of the invented analysis. The bundled examples are proposed reference outputs, not evidence that any agent or client has been tested.

## What to score

Score each dimension from 0 to 2 against the user's task and supplied source. Do not reward polished language that conceals a factual change.

| Dimension | 2 — meets the standard | 1 — needs revision | 0 — fails |
| --- | --- | --- | --- |
| Fidelity | Preserves material figures, units, periods, metric definitions, comparisons, attribution and quoted words. | Contains minor imprecision that does not alter a material claim. | Changes or invents a material fact, number, basis, attribution or quotation, or omits a condition that changes meaning. |
| Evidence and uncertainty | Distinguishes reported facts, estimates, scenarios and interpretation; preserves conditions, limitations, negative evidence and unresolved conflicts. | Qualifiers remain broadly accurate but their placement or phrasing weakens clarity. | Claims certainty, causation or evidentiary support the source does not provide; silently resolves missing or contradictory evidence. |
| Argument hierarchy | Leads with the strongest supported point and connects support, implication and caveat in a coherent order. | The relevant argument is present but buried, repetitive or weakly connected. | The main point is unsupported, misleading, absent or disconnected from the evidence. |
| Specificity and readability | Uses concrete metrics and subjects, concise sentences and clear logical connections without unnecessary repetition. | Understandable but vague, dense, repetitive or awkward in places. | Meaning is difficult to recover, materially vague or obscured by inflated language. |
| Institutional register | Uses measured, analytical language suited to a professional investment audience; assertions match the source's strength. | Mostly appropriate, with minor promotional, conversational or formulaic language. | Uses hype, unsupported conviction, promises, sensationalism or a tone unsuitable for the requested audience. |
| Format | Meets the requested artifact, structure, length and quotation requirements. Headlines and bullets each remain faithful. | A small format deviation leaves the result readily usable. | Substantially ignores the requested form, length or required components. |

Fidelity and evidence/uncertainty are hard gates. Any material alteration scores 0 in the relevant gate and fails the output regardless of the total. Materiality turns on whether a reader could reach a different substantive conclusion, not whether the altered text sounds plausible. Examples include changing gross to net, H2 to FY, a scenario to guidance, an association to causation, or an undisclosed event to a nonexistent event. An unsupported headline fails even if a later bullet restores a caveat.

A suggested acceptance threshold is at least 10 of 12, with both hard gates scoring 2 and no dimension scoring 0. A score of 1 in a hard gate calls for review and revision before acceptance. Record the reason and exact output span for every deduction. Treat the threshold as a review policy, not a statistical measure of reliability.

## Run procedure

1. Record the skill package revision, client and version, model where available, invocation method, date, settings and any surrounding instructions. Use a clean conversation for each case so earlier cases do not supply missing facts.
2. Send the case's `task` and `source` to a real agent or client with the skill available. For an explicit invocation, name the skill in the request. For an implicit invocation, use the natural task wording. Capture the actual response verbatim before comparing it with fixtures.
3. Check the requested format and compare each material assertion with the source and the case's plain-language `invariants`. Inspect the headline, captions and bullets individually, as well as the full output. An output may differ substantially from `acceptable_output` and still pass.
4. Run available deterministic checks, then score all six rubric dimensions with a short rationale. Use a second reviewer for borderline or consequential cases when practical; record disagreements and their resolution rather than averaging away a hard-gate failure.
5. Preserve a run record containing the source case ID, actual output, routing observation if available, deterministic-check results, rubric scores, hard-gate decision and reviewer notes. Report counts of tested, passed, failed and unscored outputs by client. Do not claim routing, compatibility or quality has been tested for a client without an actual run record.

When an actual output fails, first identify the changed claim or unmet task requirement. Revise the skill only if the failure reflects a repeatable instruction gap; rerun the failed case and related cases after revision. Do not tailor wording solely to satisfy a literal anchor. Keep a small set of newly written holdout prompts for subsequent runs, covering the same risks with different figures and language.

## Structural checks and fixture smoke checks

Structural validation checks whether the package and test data have the expected shape: JSON parses; `schema_version` is 1; case IDs are unique; required fields have the expected types; the suite is non-empty; the case count is reported; and references resolve. These checks say nothing about an agent's writing quality or whether a client routes to the skill.

Fixture smoke checks compare bundled `acceptable_output` and `rejected_output` examples with `required_literals` and `forbidden_literals`. Required literals are case-insensitive phrase anchors chosen to catch a few predictable losses. Forbidden literals are known bad strings in these fixtures. They are narrow deterministic checks, not semantic assertions. A compliant paraphrase may fail an anchor, and a misleading output can include all required phrases. A forbidden phrase can also appear legitimately in a denial or quotation; the reviewer must judge context. Fixture checks demonstrate that the test harness behaves as designed on its own examples, not that a model, agent or client passed the evaluation.

For actual outputs, literal results are triage signals. Read the source and output together and score the rubric even when every literal check passes. Do not demand word-for-word copying of the reference rewrite, and do not count a disclaimer as repairing a materially false statement elsewhere.

## Routing checks

Routing observations are separate from output-quality scores. If the client exposes a skill-use indicator or trace, record it. If it does not, mark invocation as unverified; writing that resembles the skill's style is not proof of activation.

**Explicit positive cases:** ask, “Use the institutional-copywriting skill to revise this earnings paragraph for an investment committee,” then provide a synthetic case. Also ask for a slide headline or fund-letter paragraph by explicitly naming the skill. The expected routing is use of the named skill, with the same fidelity requirements as any other invocation.

**Implicit positive cases:** ask, “Tighten this research note for institutional investors while preserving the figures and caveats,” or, “Turn this investment thesis into one slide headline and two supporting bullets.” Supply a synthetic source with sufficient evidence. These requests fit the skill's intended work; evaluate whether the client activates it where observable and whether the resulting artifact passes the rubric.

**Negative cases:** ask for a literal transcription of a provided quotation with no rewriting, a calculation of a portfolio's standard deviation, debugging a Python script, or a casual birthday message. The expected behavior is to handle the requested task without imposing an institutional rewrite. A request to verify whether an issuer actually breached a covenant also requires evidence gathering before prose editing; the skill should not substitute a polished assertion for that work. Evaluate these routing boundaries separately from the ten rewriting fixtures.

## Coverage and limits

The ten fixtures cover exact figures, units and periods; percentages versus percentage points; conditional forecasts; estimate attribution; quotation integrity; correlation versus causation; gross/net and benchmark bases; negative evidence; contradictory figures and missing adjustment definitions; and headline fidelity. They are deliberately compact. They do not establish robustness on long documents, legal disclosures, non-English sources, live data or private workflows. Extend the suite with consented material or additional synthetic cases when those contexts become part of the intended use, and describe each tested scope precisely.
