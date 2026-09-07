# Foresite BD Agent

A Claude Code agent that runs business development for [Foresite Ads](https://foresiteads.com):
it tracks every prospect, customer, partner and investor relationship, decides the next
step, drafts the emails, and briefs Jonathan every weekday morning.

## What it connects to

| System | Used for | Access |
|---|---|---|
| Gmail (jonathan@foresiteads.com) | What was said; drafts for review | read + draft (send only to self) |
| Calendly (calendly.com/quimbi) | What is booked, who booked, their prep note | read |
| Google Calendar | Internal cadences, invitations | read |
| Foresite MCP (production DB) | Customer stage, subscriptions, onboarding, ROAS; CRM interaction log | read + `log-customer-interaction` |
| Google Drive | Meeting notes, legacy pipeline sheet | read |

Only one mailbox is connected. Mail handled from jonathan@lindas.com or
jonathan@chiefcxofficer.com is visible only when jonathan@foresiteads.com is copied.

## Layout

```
CLAUDE.md                          project rules Claude Code loads automatically
.claude/skills/bd/                 the agent: operating rules + references (people, sources, playbook)
.claude/skills/bd-daily-brief/     morning routine
.claude/skills/bd-log/             log an activity / move a stage
.claude/skills/bd-draft/           write a Gmail draft in Jonathan's voice
.claude/skills/bd-weekly-review/   weekly lifecycle report (Sep 1 2026 format)
.claude/agents/bd-agent.md         subagent definition for delegated sweeps
scripts/pipeline.py                CLI over the pipeline store (stdlib only)
pipeline/deals.json                source of truth (never hand-edit)
pipeline/activity-log.jsonl        append-only audit trail
pipeline/PIPELINE.md               rendered view
briefs/                            daily and weekly briefs
```

## Daily use

```
/bd-daily-brief                 run the sweep now (also fired weekdays 6am PT by a Routine)
/bd-log behno "kickoff booked for Sep 15" --type meeting
/bd-draft neems-jeans           draft Andre's answer into Gmail
/bd-weekly-review               regenerate the lifecycle report
python3 scripts/pipeline.py stale        what needs attention
python3 scripts/pipeline.py show behno   one deal in full
```

## Pipeline model

Stages for prospects: intro, awaiting_booking, meeting_booked, met, materials_sent,
proposal, negotiation, verbal_yes, closed_won, closed_lost, dormant. Customers:
onboarding, active, at_risk, churned, winback. Relationships: exploring, partner_active.
`ball` says who owes the next move (us, them, team, none); `next_due` and the stage's
nudge window drive the daily flags (OVERDUE, YOUR TURN, NUDGE, TEAM STALLED,
UNVERIFIED).

Seeded 2026-09-07 from the Sep 1 2026 "BD & Customer Lifecycle Report v2" and a Gmail,
Calendly and Foresite DB sweep.
