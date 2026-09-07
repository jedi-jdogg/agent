# Source recipes

Exact, tested ways to read each system. Prefer these over improvising.

## Gmail (connector: Gmail, account jonathan@foresiteads.com)

Search syntax notes learned the hard way:
- `label:` wants the lowercase hyphenated name, not the label id and not the display
  name with spaces. `label:a-pipeline` works. Labels with spaces become hyphens, so
  "A - Hot Leads" is `label:a---hot-leads`, "A - Urgent" is `label:a---urgent`,
  "B-Fundraising" is `label:b-fundraising`, "B - Customer Success" is
  `label:b---customer-success`.
- `search_threads` previews show only the ~5 oldest messages per thread. Always call
  `get_thread` (messageFormat `PLAIN_TEXT`) before deciding who spoke last.
- Useful sweeps:
  - New inbound from outside the company, last N days:
    `newer_than:3d -from:me -from:foresiteads.com -category:promotions -category:updates -category:social`
  - Santiago intros: `from:santiago subject:"Foresite Intro" newer_than:14d`
    (he writes from silverfirepartners.com, themanhattanedge.com, distinctelements.com,
    theapexnorth.com).
  - What Jonathan sent externally: `in:sent newer_than:7d -to:foresiteads.com`
  - A deal by contact: `from:<email> OR to:<email>` then `get_thread` on the ids stored
    in the deal's `gmail_threads`.
  - Existing drafts (do not duplicate): `list_drafts` with `view: DRAFT_VIEW_FULL`.
- Drafting: `create_draft` with `replyToMessageId` set to the id of the latest message
  in the thread so it threads correctly. Put the body in `body` (plain text). Recipients
  must be bare addresses. Do not include Jonathan's own address in `to`.
- Sending: only `send_message` to jonathan@foresiteads.com for the daily brief.

## Google Calendar (connector: Google Calendar)

- `list_events` on `jonathan@foresiteads.com` with `startTime`/`endTime` for the window.
  This calendar carries internal cadences (Foresite Team Meeting, StoreYa sync, J & K
  Sync, Escalon, Shannon Fabrics) and invitations others send.
- Calendly bookings land on the jonathan@chiefcxofficer.com calendar, which is NOT
  connected. Get them from Calendly instead (below).
- The "Streak" calendar is a legacy CRM sync and has been empty since June 2026.

## Calendly (connector: Calendly, host Jonathan Shroyer, slug quimbi)

- `users-get_current_user` once, then `meetings-list_events` with
  `user=https://api.calendly.com/users/EDCDIXDQGCAW3UXX`, `status=active`,
  `min_start_time`/`max_start_time` in UTC, `sort=start_time:asc`.
- Then `meetings-list_event_invitees` for each meeting uri to get the invitee name,
  email, time zone and the "anything to help prepare" answer. That answer is the best
  one-line brief for a first call.
- The invitee `created_at` tells you when they booked, which resolves "did they book?"
  questions without a second email.

## Foresite MCP (connector: Foresite)

Read-only queries (`database-query`, SELECT only):

```sql
-- customer book with billing state
SELECT s.tenant_id, t.name, s.status, p.name AS plan, s.created_at, s.ends_at, s.trial_ends_at
FROM subscriptions s JOIN tenants t ON t.id=s.tenant_id LEFT JOIN plans p ON p.id=s.plan_id
WHERE s.status IN ('active','past_due','paused','new') ORDER BY s.ends_at;

-- subscriptions ending in the next 14 days (renewal / churn watch)
SELECT s.tenant_id, t.name, s.status, p.name AS plan, s.ends_at
FROM subscriptions s JOIN tenants t ON t.id=s.tenant_id LEFT JOIN plans p ON p.id=s.plan_id
WHERE s.ends_at BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 14 DAY) ORDER BY s.ends_at;

-- onboarding stuck
SELECT id, tenant_id, customer_name, status, services, blocked_reason, email_sent_at, updated_at
FROM onboarding_records WHERE status NOT IN ('NO_ONBOARDING_REQUIRED') ORDER BY updated_at DESC;

-- what customers still owe us / what we owe them
SELECT ct.tenant_id, t.name, ct.owner, ct.title, ct.status, ct.created_at
FROM customer_tasks ct JOIN tenants t ON t.id=ct.tenant_id WHERE ct.status='open' ORDER BY ct.created_at;

-- recent CRM interactions logged by anyone
SELECT ci.created_at, ci.category, ci.status, ci.prospect_customer_name, c.client, ci.notes
FROM customer_interactions ci LEFT JOIN crm_customers c ON c.id=ci.crm_customer_id
ORDER BY ci.created_at DESC LIMIT 30;

-- new tenants (self-serve signups) in the last 14 days
SELECT t.id, t.name, t.domain, t.created_at, u.email FROM tenants t LEFT JOIN users u ON u.id=t.created_by
WHERE t.created_at > DATE_SUB(NOW(), INTERVAL 14 DAY) ORDER BY t.created_at DESC;
```

Gotchas: `key` is a reserved word in MariaDB, backtick it. Tenants 62, 70, 71, 85, 87
and "Arun Agent" / "Arun Bordoloi 's Business" are internal test tenants. Tenants 96
and 97 are both Nira Skin.

Tools:
- `customer-lookup` (name or tenant_id) for the 360 view before a retention email.
- `roas-report` and `payments-report` for the numbers in a recap or victory-lap email.
- `log-customer-interaction` after any real touch: prospects via `prospect_name` with
  `category=pre_sales`; customers via `tenant_id` with `follow_up` or `upselling`.
  Include `due_at` when there is a next step date. This is a write; it is expected.
- `manage-customer-success` (`entity=onboarding_record`) to read blocked onboardings.
- Never call `database-write`, `refund-payment`, `subscription-actions`,
  `create-one-off-invoice` with send=true, or `impersonate-user` from the BD agent.

## Google Drive (connector: Google Drive)

- Meeting notes: Google Meet "Notes by Gemini" docs are attached to calendar events;
  open them with `read_file_content` when you need what was said in a call.
- "Copy of Foresite AI Pipeline - Jonathan / Santiago" (sheet, last edited Jul 2026) is
  the pre-pipeline tracker; read-only reference.

## Slack

No BD or sales channel exists. Do not post pipeline content to Slack unless asked.
