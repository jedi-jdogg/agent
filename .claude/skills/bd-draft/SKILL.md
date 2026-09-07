---
name: bd-draft
description: Draft a business-development email in Jonathan's voice and save it as a Gmail draft (never send). Use for "draft a reply to X", "write the follow-up to Y", "send Z the recap" (still a draft), "nudge A", "answer B's question", or any prospect/customer/partner email. Argument: a deal id or a person's name.
---

# Draft a BD email

Load the `bd` skill (voice rules in references/context.md, patterns in
references/playbook.md).

1. `python3 scripts/pipeline.py show <id>` for stage, contacts, threads, next_step.
2. Read the latest thread in full (`get_thread`, PLAIN_TEXT) so the draft answers what
   was actually asked and does not repeat what was already said. Read one or two of
   Jonathan's own recent replies in the thread to calibrate length and tone.
3. If numbers are needed (ROAS, revenue, spend), pull them from the Foresite MCP
   (`roas-report`, `customer-lookup`, `payments-report`) and quote them exactly.
   Anything you cannot source becomes `[CONFIRM: ...]`.
4. Check `list_drafts` for an existing unsent draft to the same person; update it
   (`update_draft`) instead of creating a second one.
5. `create_draft`: `to` = the counterpart(s), `cc` = whoever was on the thread from
   Foresite (usually kendra@foresiteads.com when onboarding or money is involved),
   `replyToMessageId` = latest message id, `subject` only for a new thread, `body` in
   plain text. Sign off "Jonathan". No em dashes.
6. `pipeline.py log <id> "Draft created: <one line>" --type draft --by agent --keep-ball`
   and set `next_step` to "Review and send draft: <subject>" with `ball=us`.
7. Mirror to Foresite with `log-customer-interaction` (status `pending`).
8. Show Jonathan the draft text in chat, the Gmail draft id, and one sentence on why
   this angle.

Owner check: if the deal's `owner` is kendra, kyle or another teammate, do not draft to
the customer. Draft a two-line internal note to that owner instead and say so.
