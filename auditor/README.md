# nlpm-auditor

*A Codex-operated health inspector for NL programming ecosystems — making the rounds so the restaurants don't have to wonder about their own kitchens.*

The pipeline currently discovers Claude Code plugin and skill repositories as
static audit targets. Its execution surface is Codex-only: [NLPM](https://github.com/xiaolai/nlpm)
provides the 100-point rubric and `openai/codex-action@v1` performs automated
analysis.

## How It Works

```mermaid
graph LR
    subgraph "Weekly Cron"
        D[Discover] -->|creates issues| R[(Registry)]
    end

    subgraph "Human Review"
        R --> H{Worth auditing?}
        H -->|label: audit-ready| A[Audit]
        H -->|close| X[Skip]
    end

    subgraph "Codex Action"
        A -->|scores artifacts| Report[Audit Report]
        Report --> H2{Has real bugs?}
        H2 -->|label: contribute-approved| C[Contribute PRs]
        H2 -->|close| X2[No action]
    end

    subgraph "Completion"
        C -->|submits PRs| T[Track]
        T -->|PRs merged| CS[Case Study]
        CS -->|auto-generated| Done[Complete]
    end
```

## Pipeline

| Workflow | Trigger | What it does |
|----------|---------|-------------|
| `auditor-discover.yml` | Weekly cron / manual | Trawls GitHub for Claude Code repos with 500+ stars and 5+ NL artifacts — casting the net |
| `auditor-audit.yml` | Issue labeled `audit-ready` | Clones the repo and gives it a physical — NLPM scores every artifact, writes the diagnosis |
| `auditor-contribute.yml` | Issue labeled `contribute-approved` | Knocks on the maintainer's door with a fix — forks, branches, PRs for verified bugs only (max 5) |
| `auditor-track.yml` | Every 4 hours / manual | Checks the mailbox — did the maintainer merge, close, or ignore? Updates the registry |
| `auditor-case-study.yml` | Issue labeled `case-study-ready` | Writes up the story — gathers evidence, drafts article, polishes prose, paints the cover, commits the whole thing |
| `auditor-daily-report.yml` | Daily / manual | Takes the pulse — pipeline state, PR scorecard, rule frequency, rejection lessons, self-evolution signals |

## Issue Label Lifecycle

```mermaid
stateDiagram-v2
    [*] --> audit_candidate : discover.yml
    audit_candidate --> audit_ready : human approves
    audit_candidate --> [*] : human closes

    audit_ready --> audit_complete : audit.yml scores
    audit_complete --> contribute_approved : human approves PRs
    audit_complete --> [*] : no real bugs

    contribute_approved --> prs_submitted : contribute.yml
    prs_submitted --> case_study_ready : track.yml detects merges
    prs_submitted --> [*] : all PRs rejected

    case_study_ready --> complete : case-study.yml writes article
    complete --> [*] : issue closed
```

| Label | Meaning |
|-------|---------|
| `audit-candidate` | Discovered by crawler, awaiting human review |
| `audit-ready` | Approved for audit — triggers `audit.yml` |
| `audit-complete` | Audit report generated |
| `contribute-approved` | Human approved PR submission — triggers `contribute.yml` |
| `prs-submitted` | PRs have been submitted to the target repo |
| `case-study-ready` | PRs merged — triggers `case-study.yml` |
| `complete` | Case study published, issue closed |

## Case Study Generation

Every good audit deserves a good story. When `case-study-ready` is applied, the pipeline writes one:

1. **Gathers evidence** — like a journalist assembling source material before writing a word:
   - Repo metadata, all PRs (states, timestamps, URLs), tracking issues
   - Commits mentioning NLPM or agent co-authorship
   - Maintainer review comments — what they said matters more than what we said
   - The original audit report

2. **Writes the draft** — Codex Action follows a proven template (disclosure, audit results with mermaid charts, PRs submitted, maintainer response, timeline, limitations)

3. **Polishes the prose** — a second pass adds literary texture: similes, metaphors, punch lines. Restraint is elegance — 8-15 touches, no more

4. **Validates mermaid** — every diagram block is syntax-checked; broken ones get fixed automatically

5. **Paints the cover** — DALL-E generates an editorial illustration in warm amber and navy

6. **Commits the package** — article + image to `case-studies/`, registry updated, issue closed. The story tells itself from that point on.

## Rules of Engagement

We're guests in other people's repos. Behave accordingly. The four hard
rules below come directly from the lesson at `google-gemini/gemini-skills#39`
(markmcd, 2026-04-28). They are encoded into the contribute workflow as
mechanical gates, not just guidance — see `.github/workflows/auditor-contribute.yml`.

1. **Only contribute concretely.** Per-PR fixes only. Never an umbrella
   "audit findings" issue. The PR body's `nlpm-metadata` block carries
   all provenance. The contribute workflow has a backstop step that
   closes any stray issue and fails the run, so this rule is mechanical.

2. **High confidence, with evidence.** Only findings marked
   `confidence: high` in the audit sidecar reach the contribute step —
   the workflow filters before dispatching the agent. `high` requires
   the scorer to have reproduced the breakage during the audit pass
   (ran the snippet, followed the link, parsed the YAML). The agent
   re-verifies before opening the PR; no reproduction, no PR. Each PR
   body is three labelled lines: **Bug**, **Evidence**, **Fix**.

3. **Assume the authors' good intent and competence.** Findings about
   style, naming, content priorities, or anything that could be a
   deliberate authorial choice are dropped — silently. Default to
   `medium` confidence when unsure; `medium` never ships. A drop is
   the system working, not a failure.

4. **Never leave the maintainer with the burden of reviewing our report.**
   The PR body has no questions, no "is this intentional?", no link to
   our audit, no "please consider". A maintainer should be able to
   decide yes/no in 30 seconds.

Plus the operational floor:

5. **Never PR convention preferences** — if their YAML works, it's their YAML
6. **First contact: max 3 PRs; thereafter max 5** — focused visit, not a renovation
7. **Max 2 repos per week** — good neighbors don't ring every doorbell on the street
8. **Accept "no" gracefully** — close the PR, say thank you, take the lesson home. The pushback gate enforces this on subsequent runs.

## Setup

1. Create the repo on GitHub
2. Add secrets:
   - `OPENAI_API_KEY` — for Codex Action and OpenAI image generation
   - `PAT_TOKEN` — GitHub PAT with `public_repo` scope (for forking and PRing to other repos)
3. Create the issue labels listed above
4. Run `discover.yml` manually to seed the registry

## Directory Structure

```
registry/repos.json          — The patient file: every repo and where it is in the pipeline
audits/                      — The X-rays: per-repo scoring reports
case-studies/                — The published stories: date-prefixed articles
case-studies/images/         — Cover art: compressed, date-prefixed
reports/                     — Daily health checks: pipeline state + self-evolution signals
feedback/log.json            — The learning journal: rule stats, PR outcomes, rejection patterns
```

Naming: `YYYY-MM-DD-owner-name.md`, `YYYY-MM-DD-owner-name-cover.png`, `YYYY-MM-DD.md` (reports)

## Self-Evolution

The daily report tracks signals that should feed back into NLPM itself:

| Signal | What it means | Action |
|--------|--------------|--------|
| Rule fires 20+ times across audits | Might be noise, not signal | Review rule — is it finding real bugs or just being pedantic? |
| PR rejected by maintainer | NLPM flagged something the maintainer considers valid | Soften or remove the rule (like scalar-string `tools:` → nlpm v0.7.0) |
| PR merged by maintainer | Rule found a real bug | Protect this rule — it earns its keep |
| Same defect pattern in 3+ repos | Ecosystem-wide issue | Consider adding a new rule to the 50 |
| Acceptance rate dropping | NLPM is drifting toward opinions | Tighten the bug-vs-convention filter |

The feedback loop: **audit → contribute → track outcomes → update NLPM rules → audit better next time.**

## Prerequisites

- GitHub Actions enabled
- `PAT_TOKEN` secret with `public_repo` scope
- `OPENAI_API_KEY` secret (for Codex Action and cover images)
