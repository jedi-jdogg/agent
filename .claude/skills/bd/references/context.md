# Foresite BD context

## The business

Foresite Ads (foresiteads.com) is an AI-powered growth platform for e-commerce brands,
built by Jonathan Shroyer inside his own brand Linda's Electric Quilters (lindas.com)
and then sold to other DTC brands. The Linda's numbers are the reference case: in the
Sep 1 2026 report, $470K store revenue in August at 13.7 blended ROAS.

Products and plan names as they appear in the Foresite DB (`plans` table) and in
Jonathan's emails:

- Ads Only, Ads + Flows (the core monthly subscriptions), Management Fee Only (10%),
  Ad Budget Weekly / Biweekly (pass-through ad spend).
- Historic plan labels in the `clients` table: Performance Partnership, Growth
  Accelerator, Hockey Stick.
- Services in onboarding records: flows (AI email/SMS flows via Instant.one),
  ai-identities (visitor identification), ai-seo (AEO/SEO), tv-platform (CTV via Vibe),
  ai-influencers (Cracked.AI), ai-noti.
- "Olivia" is the AI. "Unlimited identities" and "5,000 flows" are package terms
  Jonathan has quoted.

Pricing facts Jonathan has stated in threads (reuse these, invent nothing else):
- No free trials. A basic package is required to get access (told Stephan at EIS, Jul 22).
- Neems Jeans was offered $1,500/mo (Aug 13).
- Apparel does 30 to 40% better than average on Foresite, especially high end, and
  especially after the 60-day AI learning period (Aug 13).
- Monthly subscription model on Stripe; ACH possible (Kendra to Magic Chocolate, Aug 20).

## People

Foresite team
- Jonathan Shroyer: founder/owner. Mailboxes: jonathan@foresiteads.com (the only one
  connected), jonathan@lindas.com, jonathan@chiefcxofficer.com (Calendly account email;
  Calendly bookings land on that calendar). Calendly: https://calendly.com/quimbi.
  Time zone America/Los_Angeles (SF), travels (London the week of Sep 7 2026).
- Kendra Jackson (kendra@foresiteads.com): customer success and operations; runs the
  Foresite Team Meeting (Tue 11am PT), Shannon Fabrics cadence, onboarding welcomes;
  owns Magic Chocolate, BionicGym, Dermaesthetics, BB GIRL, several at-risk accounts.
- Arun Bordoloi (arun@foresiteads.com): platform/integrations (Klaviyo, Meta assets,
  Instant segments). Attends StoreYa and Opensend syncs.
- Kyle (kyle@foresiteads.com): channel and enterprise block; "J & K Sync" with Jonathan.
- Adina, Thueba, Christopher, Charles, Brint, Kim, Keith Myers, Daryl: team.
- Corey Pearson, Gourav Sethi, Rey: Linda's side.
- Pa Yang (Escalon), Amanda Cram (Light Your Books): accounting, not BD.

Referral engine
- Santiago Avalos sends most intros. He writes from four domains:
  silverfirepartners.com, themanhattanedge.com, distinctelements.com, theapexnorth.com.
  Intro subject pattern: "<Brand> - Foresite Intro". He received the Sep 1 report and
  should keep getting outcome updates.
- Braden Pollock (pollockfund.com), Rick Del Rio: occasional intros.

Partners and vendors
- StoreYa (Mushon, Berk, Emma, Yafit): Google Ads execution partner; weekly clients
  sync Wed 10am PT. Sends monthly client reports.
- Instant.one (Liam Millward, Joey Smilgiewicz): AI flows and SMS; annual plus SMS
  agreed Aug 5 for Linda's.
- Opensend (Lauren, Bradley): bi-weekly sync Tue.
- Settle (Max Mohr), Drip Capital (Nithin Raj), Rosenthal (Andrew Barone): financing
  and working-capital conversations; also potential mutual deal flow.
- Deal Insider Capital (Jason Olson, Neil Patel): fundraising memorandum.
- Justin Ruiss (BWG Global): advisor.

## Jonathan's voice

Read a few of his sent messages before drafting. The pattern:

- Very short when the ask is small. "Thanks Santiago, lovely to meet Lani. Excited to
  catch up, please grab a spot on my diary. Jonathan"
- Acknowledgements are two or three words: "Awesome, ty." "Ty mate." "Sounds great,
  thanks mate." Emojis sometimes stand alone as a reply.
- British-inflected: "diary" for calendar, "mate", "game" for willing, "ty".
- Always offers calendly.com/quimbi rather than proposing times, except when a time
  zone problem needs concrete slots.
- Structured emails (recaps, offers, onboarding) use a one-line warm opener, numbered
  steps or bullets, one clear ask, sign-off "Jonathan". See the Behno Sep 2 reply and
  the Aug 13 Neems reply for the template.
- He does not oversell. He states results, offers a package, and lets them book.
- Never use em dashes in drafts. Never write "I hope this email finds you well".

## Customer health signals (from the Foresite DB)

- `subscriptions.status`: active, past_due (billing risk), paused (engagement risk),
  canceled (churn; `ends_at` is the exit date), new.
- `onboarding_records.status`: INITIATED, EMAIL_GENERATED (welcome not sent),
  READY_FOR_ORCHESTRATION, BLOCKED (see `blocked_reason`), NO_ONBOARDING_REQUIRED.
- `customer_tasks` with `owner=customer` and `status=open` are things the customer
  still owes (questionnaire, Shopify/Klaviyo access). `owner=csm` open tasks are ours.
- `clients` carries the legacy contract flags and plan labels; `crm_customers` links to
  `tenant_id` and is where `log-customer-interaction` lands.
- ROAS and revenue: `blended_roas_scorecard`, `roas-report` tool, `instant-*` tools.
