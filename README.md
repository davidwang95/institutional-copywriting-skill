# Institutional copywriting skill

A reusable skill for evidence-led investment and business writing: research notes, committee memos, executive summaries, and presentation copy. It removes inflated phrasing and repetitive AI mannerisms while keeping the writer's institutional register, facts, uncertainty, and attribution.

The package uses the shared Agent Skills structure and only `name` and `description` frontmatter. It needs no tool integration, network access, extra dependencies, or client-specific runtime. It does not claim ASD-STE100 compliance or detect AI authorship.

## Install

```sh
git clone https://github.com/davidwang95/institutional-copywriting-skill.git
cd institutional-copywriting-skill
```

Clone or download this repository. Copy the **entire `institutional-copywriting` folder**, including `references`, into the relevant skills directory. The repository's outer folder is not the skill. The commands below are run from the repository root and stop if the destination already exists.

| Client | Project installation | Optional personal installation | Explicit use |
| --- | --- | --- | --- |
| Codex | `.agents/skills/institutional-copywriting/` | `~/.agents/skills/institutional-copywriting/` | `$institutional-copywriting` or select via `/skills` |
| Claude Code | `.claude/skills/institutional-copywriting/` | `~/.claude/skills/institutional-copywriting/` | `/institutional-copywriting` |

These paths and invocations were verified against [OpenAI's current skill docs](https://learn.chatgpt.com/docs/build-skills) and [Claude Code's skill docs](https://code.claude.com/docs/en/skills) on 6 October 2026. Both clients can also match skills to requests automatically. Discovery and reload behavior depend on the client version; confirm that the skill appears in its skill list before use.

**Project installation, macOS/Linux**

From the repository root, choose the destination in your target project:

```sh
# Replace /path/to/project with the project that should use the skill.
project=/path/to/project
destination="$project/.agents/skills/institutional-copywriting" # Codex
# For Claude Code instead: destination="$project/.claude/skills/institutional-copywriting"
if [ -e "$destination" ]; then
  echo "Destination exists; review it before updating." >&2
  exit 1
fi
mkdir -p "$(dirname "$destination")"
cp -R institutional-copywriting "$destination"
```

**Project installation, Windows PowerShell**

```powershell
# Replace this path with the project that should use the skill.
$projectPath = 'C:\path\to\project'
$destination = Join-Path $projectPath '.agents\skills\institutional-copywriting' # Codex
# For Claude Code instead:
# $destination = Join-Path $projectPath '.claude\skills\institutional-copywriting'
if (Test-Path -LiteralPath $destination) { throw 'Destination exists; review it before updating.' }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
Copy-Item -LiteralPath '.\institutional-copywriting' -Destination $destination -Recurse
```

For a personal installation, use the same copy operation with `~/.agents/skills/institutional-copywriting` or `~/.claude/skills/institutional-copywriting`. In PowerShell, build that path with `Join-Path $HOME '.agents\skills\institutional-copywriting'` or `Join-Path $HOME '.claude\skills\institutional-copywriting'`. Installing personally makes the skill available beyond one project. No global installation is performed by this repository.

To update, review the existing skill and replace only its own folder with the new version. To remove it, remove that installed folder. Do not change unrelated client settings.

## Use

In Codex:

```text
$institutional-copywriting Revise the following investment-committee summary.
Preserve all figures, attribution, conditions, and uncertainty. Return the revised
copy and flag any unsupported central claim. [Paste source text.]
```

In Claude Code:

```text
/institutional-copywriting Turn the supplied analysis into a takeaway title and
three concise slide bullets. Keep the period, comparison basis, source, and
material qualifiers. Do not add evidence. [Paste source text.]
```

Supply the audience, purpose, format, source material, and any length or confidentiality constraints. For a factual gap, the skill flags the problem instead of inventing support. It does not research, send, or publish copy unless separately authorized.

## Package

- [SKILL.md](institutional-copywriting/SKILL.md): core workflow and evidence constraints.
- [Format guidance](institutional-copywriting/references/formats.md): slide hierarchy, summaries, memos, and source placement.
- [Synthetic before/after examples](institutional-copywriting/references/examples.md): concrete transformations with fidelity explanations.
- [Evaluation rubric](institutional-copywriting/references/evaluation.md) and [cases](evals/cases.json): regression scenarios and semantic review criteria.
- [Design sources and licenses](SOURCES.md): official docs and pinned public inspirations.

## Validate and evaluate

With Python 3.10 or newer, no third-party packages:

```sh
python scripts/validate.py
python -m unittest discover -s scripts -p 'test_*.py' -v
python scripts/check_cases.py --fixtures
```

These check the package, internal links, fixture schema, and deliberately good/bad assertion examples. Phrase checks are diagnostic and can miss semantic errors or reject valid paraphrases. They do not certify facts or measure writing quality.

To evaluate actual outputs, supply a JSON object mapping case IDs to their output strings:

```sh
python scripts/check_cases.py --outputs /path/to/results.json
```

Then score each output with the rubric. Test discovery and invocation in each installed client, save the prompt, client/model version, trace where available, output, and semantic review. Include explicit, implicit, and negative routing cases. See [validation scope](VALIDATION.md) for what was actually tested in this release.

All published examples and test scenarios are original and synthetic. No private reference document is included. Original materials are [MIT licensed](LICENSE).
