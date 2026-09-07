---
name: bd-log
description: Log a BD activity or update a deal in the Foresite pipeline. Use when Jonathan says things like "log that I spoke to X", "we met Y today", "Z said yes", "mark A as lost", "move B to proposal", "add new prospect C", or pastes meeting notes. Updates pipeline/deals.json and mirrors the touch into the Foresite CRM.
---

# Log a BD activity

Load the `bd` skill. Then:

1. Resolve the deal: `python3 scripts/pipeline.py list | grep -i <name>`; if none,
   `add` it (ask nothing; infer type/stage from what was said and say what you chose).
2. Record the touch:
   `python3 scripts/pipeline.py log <id> "<what happened>" --type email|meeting|call|note --by us|them --date YYYY-MM-DD [--thread <gmail id>]`
   A touch by `them` flips the ball to `us` and vice versa; add `--keep-ball` if that is
   wrong for this case.
3. If the stage moved: `python3 scripts/pipeline.py stage <id> <new_stage> "<reason>"`.
   `closed_won` automatically converts a prospect to a customer in onboarding.
4. Set the next step: `update <id> "next_step=<verb + object>" next_due=YYYY-MM-DD ball=us|them|team`.
5. Mirror to Foresite: `log-customer-interaction` with `notes` = the same text,
   `prospect_name` for prospects (category `pre_sales`) or `tenant_id` for customers
   (category `follow_up`, or `upselling` if it is expansion), `due_at` = next_due.
6. If notes were pasted (meeting notes, a Gemini notes doc), put the substance in the
   log note and, if a recap email is owed, offer to run `/bd-draft <id>` right away.
7. `render`, then `git add pipeline && git commit -m "pipeline: log <id>" && git push -u origin <branch>`.

Reply with two lines: what was logged, and the next step now on file.
