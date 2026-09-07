# Foresite BD Agent

This repository is Jonathan Shroyer's business-development agent for Foresite Ads
(foresiteads.com). It holds the pipeline of prospects, customers, partners and
investors, the rules for what to do next, and the daily/weekly routines that turn
Gmail, Calendly, Google Calendar and the Foresite platform database into actions,
drafts and briefs.

## Start here

- Any BD question or task: the `bd` skill (`.claude/skills/bd/SKILL.md`) and its three
  references (`context.md` people/products/voice, `sources.md` tool recipes,
  `playbook.md` next-step rules and email patterns).
- `/bd-daily-brief` runs the morning sweep, drafts emails, writes `briefs/<date>.md`
  and emails it to jonathan@foresiteads.com. A Routine fires it weekdays at 6am Pacific.
- `/bd-log <deal> ...` records a call, meeting, email or stage change.
- `/bd-draft <deal>` writes a Gmail draft in Jonathan's voice (never sends).
- `/bd-weekly-review` produces the lifecycle report in the Sep 1 2026 format.

## Data

- `pipeline/deals.json` is the source of truth. Change it only through
  `python3 scripts/pipeline.py` (`list`, `show`, `add`, `update`, `log`, `stage`,
  `stale`, `brief-data`, `render`, `validate`). Never hand-edit.
- `pipeline/activity-log.jsonl` is the append-only audit trail; `pipeline/PIPELINE.md`
  is the rendered view (`render`).
- `briefs/` holds every daily and weekly brief.
- Customer facts (subscriptions, onboarding, tasks, ROAS) live in the Foresite DB and
  are read live through the Foresite MCP; do not copy them into deals.json beyond a
  short `value_note`.

## Hard rules

1. Draft, never send, to anyone except jonathan@foresiteads.com.
2. No free trials, no invented prices. Use `[CONFIRM: ...]` placeholders.
3. Kendra owns customer success; Kyle owns channel/enterprise. Route, do not bypass.
4. Verify from a thread or DB row before asserting a stage change.
5. Commit pipeline and brief changes at the end of every run:
   `git add pipeline briefs && git commit -m "pipeline: <date> <summary>" && git push -u origin <current branch>`.
6. Only the jonathan@foresiteads.com mailbox is connected; say so when a deal may have
   moved in jonathan@lindas.com or jonathan@chiefcxofficer.com.

## Conventions

- Python 3.11, standard library only, in `scripts/`. Run `python3 scripts/pipeline.py validate` before committing.
- Dates are ISO `YYYY-MM-DD` in Pacific time. Deal ids are lowercase slugs.
- No em dashes in anything written for Jonathan to send.
