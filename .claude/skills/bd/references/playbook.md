# Next-step playbook

## Stage rules (prospects)

| Stage | Ball | Act when | Action |
|---|---|---|---|
| intro | us | same day | Reply-all thanking the referrer, welcome the person, offer calendly.com/quimbi. Log deal at `awaiting_booking`, ball=them. |
| awaiting_booking | them | 7 days silent | Nudge 1: one line, re-offer the link. If they raised a time-zone question, answer it and give two concrete slots in their zone. 14 days: nudge 2 with two slots. 21 days: mark `dormant`, tell the referrer politely. |
| meeting_booked | none | day before | Prep brief: Calendly answer, website, Shopify/Klaviyo signals if any, similar client results (K9 Power, ShaktiMat, Linda's). Day after: if no recap sent, that is `ball=us`. |
| met | us | within 24h | Send the recap plus materials (overview PDF, 4 videos) in the "Recap + next steps" format. Move to `materials_sent`, ball=them. |
| materials_sent | them | 7 days | Follow-up 1 with a fresh proof point (a client result from this month). 14 days: follow-up 2, ask directly "is this a now or a later?". 28 days: `dormant`. |
| proposal | them | 5 days | Ask for the decision or the blocker. Offer a start date. 10 days: offer a call to walk through it. |
| negotiation | us | same day | Answer every open question in numbered form, restate the offer, propose a start date. Never leave a prospect question unanswered over a weekend. |
| verbal_yes | us | same day | Agreement plus invoice out the door, kickoff booked, Kendra copied. This is the highest-value action in the pipeline; it goes first in every brief until done. |
| closed_won | none | | `stage closed_won` moves type to customer/onboarding. Tell the referrer (Santiago) the same day. |
| closed_lost | none | | Log the reason. Set a 90-day re-touch if the reason was timing. |
| dormant | them | 60 days | One-line re-touch with something new (a result, a feature). |

## Stage rules (customers)

| Signal (from Foresite DB / email) | Action |
|---|---|
| Subscription `canceled` with `ends_at` inside 14 days | Save call with a performance plan, or a clean exit that protects the reference. Decide, do not drift. |
| `past_due` | Billing fix (card, ACH) with Kendra; do not talk performance until money is fixed. |
| `paused` | Proactive performance note; find out what they are waiting for. |
| Renewal (`ends_at`) inside 10 days and performance is good | Send the recap before the renewal date. A good month is a retention asset; use it. |
| Revenue or ROAS down >30% month over month | Intervene while it is a conversation. Offer a review call. |
| Onboarding `BLOCKED` or customer task open >10 days | Chase the customer for access / questionnaire; chase the team for csm tasks. |
| Onboarding `EMAIL_GENERATED` with `email_sent_at` null >3 days | Welcome email never went out. Ping Kendra. |
| Big month (ROAS well above plan) | Expansion conversation: budget step-up, add Flows / AI SEO / TV. |

## Partners and referrers

- Santiago: send him outcomes on his intros (won, lost, booked) at least weekly. He is
  the top of the funnel; feeding him is BD work.
- Financing / capital partners (Settle, Drip, Rosenthal): treat as `partner`. The value
  is mutual deal flow. Follow up within 3 days of a call with one concrete ask.
- Agencies (Group 8A): channel. Position as "bring us your brands, we make you look
  good", not as a customer pitch.

## Prioritisation for the daily brief

Order the day's actions by expected value times urgency:

1. `verbal_yes` paperwork and anything `OVERDUE` with `ball=us` in Tier 1.
2. Customer money at risk in the next 7 days (cancel dates, past_due, renewals).
3. Prospect questions unanswered (any `YOUR TURN` in negotiation/proposal).
4. Meetings in the next 48 hours: prep notes.
5. Nudges due (batch identical ones into one 10-minute block).
6. Team asks (ball=team stalled >5 days): one line each for the Tuesday team meeting.
7. Re-verification of old items: at most 3 per day so the register keeps getting cleaner.

Cap the brief at seven actions. Everything else goes under "also open".

## Email patterns (Jonathan's voice)

Intro reply (reply-all):
```
Thanks <Referrer>, lovely to meet <First>. Excited to catch up, please grab a spot on my diary: calendly.com/quimbi.

Jonathan
```

Booking nudge with time-zone fix:
```
Hey <First>

My diary shows times in your zone once you open it, but to make it easy: I can do <Day> <time> or <Day> <time> your time. Either work?

Jonathan
```

Follow-up after materials:
```
Hey <First>

Quick one. <One-sentence proof point from this month, e.g. one of our apparel clients just did $42.9K in August at 12.3 ROAS.> Happy to walk through what that would look like for <Brand> when you are ready. Is this a now or a later for you?

Jonathan
```

Negotiation answer (numbered):
```
Hey <First>

1. <Answer to question 1, with a number.>
2. <Answer to question 2.>

The offer stands at <package> for $<x>/mo. If we start <date> you are through the 60-day learning period before <seasonal milestone>. Game?

Jonathan
```

Verbal yes to paperwork:
```
Great news, welcome aboard. Agreement and invoice are attached; once countersigned Kendra will send the access checklist (Shopify, Klaviyo, ad accounts) and we book the kickoff.

Jonathan
```

Retention recap (good month):
```
Hey <First>

August: $<rev> at <roas> ROAS. <One sentence on what drove it.> Two things I would do next: 1) <step>, 2) <step>. Want to run through it on a quick call?

Jonathan
```

Save call (bad month):
```
Hey <First>

August was not good enough: <roas> ROAS on $<spend>. Here is what I would change and what I would pause, and I would rather do that with you than let it drift. Can you grab 20 minutes this week: calendly.com/quimbi

Jonathan
```
