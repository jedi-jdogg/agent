---
name: bd-weekly-review
description: Produce the weekly Foresite "BD & Customer Lifecycle Report" (the format Jonathan sent Santiago on Sep 1 2026) from the pipeline plus live Foresite DB numbers. Use for "weekly review", "pipeline report", "lifecycle report", "update the report for Santiago", or on Sunday/Monday when asked for the big picture.
---

# Weekly BD and customer lifecycle report

Load the `bd` skill. This is a read-heavy run; allow ~40 tool calls.

## Gather

1. `python3 scripts/pipeline.py brief-data` and `list --json` for the register.
2. Foresite DB:
   - Collections by month for the last 3 months (`transactions` grouped by month and
     tenant; use `payments-report` if the table shape is unclear).
   - Per-client revenue and blended ROAS for the current and prior month
     (`blended_roas_scorecard`, or `roas-report` per tenant for the top 20).
   - Subscriptions: active/past_due/paused/canceled with `ends_at`.
   - Onboarding records not complete; open customer tasks.
3. Gmail: intros received this week, meetings recapped, proposals sent (`in:sent
   newer_than:7d -to:foresiteads.com`), plus any "Foresite Report" thread to see what
   Santiago last received.
4. Calendly: meetings held this week and booked for next week, with invitee answers.

## Write `briefs/weekly-YYYY-MM-DD.md`

Mirror the Sep 1 report structure exactly; Jonathan and Santiago already know how to
read it:

1. Header: as-of date, sources, changes from the previous version, caveats.
2. Executive summary (5 bullets, each with a number).
3. Active client book with live performance: client, lifetime, prior month rev/ROAS,
   current month rev/ROAS, signal.
4. Retention interventions, ranked, each with the specific move.
5. Winback book.
6. Booked meetings (verified in Calendly).
7. What closed / resolved since last report.
8. Full BD opportunity register by tier (Tier 1 in a table with Contact, State, Ball;
   Tiers 2 to 6 as dense inline lists). Mark anything not re-verified this week with ◇.
9. High-priority BD: a numbered top 10, then one paragraph on structural fixes.

Numbers must come from the DB queries you ran this session; label month-to-date.

## Deliver

- `pipeline.py render`; commit `briefs/weekly-*.md` and pipeline changes; push.
- Create a Gmail draft to santiago@silverfirepartners.com with subject
  "Foresite Report" and the report body (Jonathan sends it; do not send). Also send a
  copy to jonathan@foresiteads.com (this send is allowed).
- In chat: the five executive bullets and the top three actions.
