---
name: bd-daily-brief
description: Run the Foresite daily business-development brief. Sweeps Gmail, Calendly, Google Calendar and the Foresite DB, updates pipeline/deals.json, drafts the day's emails into Gmail, writes briefs/YYYY-MM-DD.md and emails it to jonathan@foresiteads.com. Use when asked for "the brief", "what should I do today", "morning BD run", or when fired by the daily Routine.
---

# Daily BD brief

Load the `bd` skill first (SKILL.md and all three references). Then run these steps in
order. Budget: about 25 tool calls of reading before you start writing; do not try to
re-read the entire mailbox.

## 0. Setup

```bash
cd <repo root>
git pull --ff-only || true
python3 scripts/pipeline.py validate
python3 scripts/pipeline.py brief-data > /tmp/brief-data.json
```
`brief-data` gives you: overdue, due_today, upcoming_due, your_turn, nudge,
team_stalled, unverified, verbal_yes, at_risk. Today's date is `as_of`.

## 1. What changed since yesterday (read)

1. Gmail, new inbound from outside: query in sources.md, last 2 days (3 on Monday).
   For each thread that touches a deal or looks like a new intro, `get_thread`
   (PLAIN_TEXT) and decide: who spoke last, does the stage change, is there a question
   to answer.
2. Gmail, Santiago intros last 7 days: any not in deals.json becomes a new deal
   (`add ... --stage awaiting_booking --ball them` if Jonathan already replied,
   `--stage intro --ball us` if not).
3. Gmail sent, last 2 days: anything Jonathan sent that closes an open `ball=us`
   item; log it and flip the ball.
4. Calendly: meetings from yesterday to +7 days with invitees. Yesterday's meetings
   become `met` (ball=us, recap due) unless a recap is already in sent mail. Newly
   booked meetings move `awaiting_booking` to `meeting_booked`.
5. Google Calendar: today's and tomorrow's external meetings on jonathan@foresiteads.com.
6. Foresite DB: the four queries in sources.md (customer book, ending within 14 days,
   onboarding stuck, open customer tasks) plus new tenants in 14 days. Compare to the
   customer records in deals.json; update `value_note`/`next_step` where the facts moved.
7. Existing Gmail drafts (`list_drafts`): do not create a duplicate for a deal that
   already has an unsent draft; mention it in the brief instead.

Log every finding as you go with `pipeline.py log/update/stage`.

## 2. Decide today's actions

Re-run `brief-data`. Apply the prioritisation in playbook.md. Pick at most seven
actions for Jonathan, each phrased as a verb plus the person plus the one-line reason.

## 3. Draft the emails

For every action whose natural next step is an email Jonathan sends himself (not a
Kendra/Kyle-owned deal), create a Gmail draft:
- reply in-thread when a thread exists (`replyToMessageId` = latest message id);
- follow the voice rules and the patterns in playbook.md;
- `[CONFIRM: ...]` placeholders for any number or date you cannot source;
- then `pipeline.py log <id> "Draft created: <subject>" --type draft --by agent --keep-ball`
  and `log-customer-interaction` in Foresite (prospects: `prospect_name`, `category=pre_sales`).

## 4. Write the brief

Write `briefs/YYYY-MM-DD.md` in this shape (keep it under ~120 lines):

```
# Foresite BD brief, <Weekday Month D>

## Do today (drafts waiting in Gmail unless marked)
1. **<Person / Deal>**: <what and why, one line>. Draft: <subject> | no draft (owner: Kendra)
...

## Money in the next 7 days
- <customer>: <cancel/renew/past_due fact> -> <recommended move>

## Calendar
- <time PT> <who> (<deal stage>) — prep line
(note Jonathan's travel time zone if known)

## Moved since yesterday
- <deal>: <old stage> -> <new stage> (<evidence>)

## Waiting on them (nudge when due)
- <deal>: silent <n>d, nudge due <date>

## Team asks (for the Tuesday meeting)
- Kendra: ...   - Kyle: ...   - Arun: ...

## Register health
<n> deals, <n> your turn, <n> nudges due, <n> unverified. Re-verified today: <list>.
Blind spots: threads in lindas.com / chiefcxofficer.com mailboxes are not visible.
```

## 5. Deliver and persist

1. `python3 scripts/pipeline.py render && python3 scripts/pipeline.py validate`
2. `git add pipeline briefs && git commit -m "brief: YYYY-MM-DD" && git push -u origin <branch>`
3. Email the brief to jonathan@foresiteads.com with `send_message`:
   subject `Foresite BD brief, <Weekday Month D>`, `body` = the markdown as plain text,
   `htmlBody` = a simple HTML rendering (headings, lists, bold). Sending to Jonathan's
   own address is the one send this agent is allowed to make.
4. Finish with a three-line summary in chat: actions count, drafts created, anything
   that needs a human decision.

If a source is unavailable (connector error), say so in the brief's Register health
section and proceed with the rest. Never silently skip a section.
