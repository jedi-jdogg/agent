#!/usr/bin/env python3
"""Foresite BD pipeline store.

Single source of truth: pipeline/deals.json. Append-only audit trail:
pipeline/activity-log.jsonl. Rendered view: pipeline/PIPELINE.md.

Usage (run from repo root):
  scripts/pipeline.py list [--type T] [--stage S] [--ball us|them] [--tier N] [--json]
  scripts/pipeline.py show ID
  scripts/pipeline.py add --id ID --name NAME --type TYPE --stage STAGE [options]
  scripts/pipeline.py update ID field=value [field=value ...]
  scripts/pipeline.py log ID "what happened" [--type email|meeting|call|note|stage|draft]
                              [--by us|them] [--date YYYY-MM-DD] [--thread GMAIL_THREAD_ID]
  scripts/pipeline.py stage ID NEW_STAGE ["reason"]
  scripts/pipeline.py stale [--days N]
  scripts/pipeline.py brief-data [--date YYYY-MM-DD]
  scripts/pipeline.py render
  scripts/pipeline.py validate

Only the standard library is used. Dates are ISO (YYYY-MM-DD), Pacific-time days.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEALS_PATH = os.path.join(ROOT, "pipeline", "deals.json")
LOG_PATH = os.path.join(ROOT, "pipeline", "activity-log.jsonl")
RENDER_PATH = os.path.join(ROOT, "pipeline", "PIPELINE.md")

TYPES = ["prospect", "customer", "winback", "partner", "investor", "vendor", "advisor", "channel"]

# Stage -> (label, days of silence before we nudge when ball is with THEM)
STAGES = {
    # prospect funnel
    "intro": ("Intro received, not yet replied", 2),
    "awaiting_booking": ("Replied, waiting for them to book", 7),
    "meeting_booked": ("Meeting on calendar", None),
    "met": ("Met, no materials sent yet", 1),
    "materials_sent": ("Materials / recap sent, nurturing", 7),
    "proposal": ("Proposal or pricing sent", 5),
    "negotiation": ("Active back-and-forth on terms", 3),
    "verbal_yes": ("Said yes, paperwork not done", 2),
    "closed_won": ("Signed / paying", None),
    "closed_lost": ("Lost or declined", None),
    "dormant": ("Went quiet after 3+ nudges; re-touch in 60d", 60),
    # customer lifecycle
    "onboarding": ("Customer onboarding in progress", 5),
    "active": ("Active paying customer", None),
    "at_risk": ("Active but performance/billing/engagement risk", 3),
    "churned": ("Canceled / ended", None),
    "winback": ("Former customer, re-engagement target", 30),
    # relationships
    "exploring": ("Partner/investor/channel conversation open", 7),
    "partner_active": ("Working relationship with recurring cadence", None),
}
BALL = ["us", "them", "team", "none"]
PROSPECT_TIER_ORDER = {1: "Tier 1 — proposal / negotiation / verbal yes",
                       2: "Tier 2 — met, nurturing",
                       3: "Tier 3 — intro'd, awaiting booking",
                       4: "Tier 4 — needs re-verification",
                       5: "Tier 5 — channel & enterprise",
                       6: "Tier 6 — dormant / outbound fuel"}


# ----------------------------------------------------------------- io helpers
def load() -> dict:
    if not os.path.exists(DEALS_PATH):
        return {"meta": {"updated": None}, "deals": []}
    with open(DEALS_PATH, encoding="utf-8") as f:
        return json.load(f)


def save(data: dict) -> None:
    data["meta"]["updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    data["deals"].sort(key=lambda d: (d.get("tier") or 9, d["name"].lower()))
    os.makedirs(os.path.dirname(DEALS_PATH), exist_ok=True)
    with open(DEALS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def append_log(entry: dict) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def find(data: dict, deal_id: str) -> dict:
    for d in data["deals"]:
        if d["id"] == deal_id:
            return d
    # fuzzy fallback on name
    hits = [d for d in data["deals"] if deal_id.lower() in d["name"].lower()]
    if len(hits) == 1:
        return hits[0]
    if hits:
        sys.exit(f"ambiguous id '{deal_id}': {', '.join(h['id'] for h in hits)}")
    sys.exit(f"no deal with id '{deal_id}' (use `list` to see ids)")


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def parse_date(s: str | None) -> date | None:
    if not s:
        return None
    return datetime.strptime(s[:10], "%Y-%m-%d").date()


def days_between(a: date | None, b: date) -> int | None:
    return None if a is None else (b - a).days


def parse_contact(s: str) -> dict:
    """'Name <email>|Role' or 'Name <email>' or 'email'."""
    role = None
    if "|" in s:
        s, role = [p.strip() for p in s.split("|", 1)]
    m = re.match(r"^(.*?)\s*<([^>]+)>$", s.strip())
    if m:
        name, email = m.group(1).strip(), m.group(2).strip()
    elif "@" in s:
        name, email = s.split("@")[0], s.strip()
    else:
        name, email = s.strip(), None
    c = {"name": name, "email": email}
    if role:
        c["role"] = role
    return c


# ----------------------------------------------------------------- commands
def cmd_list(args):
    data = load()
    rows = data["deals"]
    if args.type:
        rows = [d for d in rows if d.get("type") == args.type]
    if args.stage:
        rows = [d for d in rows if d.get("stage") == args.stage]
    if args.ball:
        rows = [d for d in rows if d.get("ball") == args.ball]
    if args.tier:
        rows = [d for d in rows if d.get("tier") == args.tier]
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    today = date.today()
    print(f"{'id':<26}{'type':<10}{'stage':<17}{'ball':<6}{'last':<7}{'due':<11}next step")
    for d in rows:
        age = days_between(parse_date(d.get("last_touch")), today)
        print(f"{d['id']:<26}{d.get('type',''):<10}{d.get('stage',''):<17}{d.get('ball',''):<6}"
              f"{(str(age)+'d') if age is not None else '-':<7}{d.get('next_due') or '-':<11}"
              f"{(d.get('next_step') or '')[:60]}")
    print(f"\n{len(rows)} deals")


def cmd_show(args):
    d = find(load(), args.id)
    print(json.dumps(d, indent=2, ensure_ascii=False))


def cmd_add(args):
    data = load()
    deal_id = args.id or slug(args.name)
    if any(d["id"] == deal_id for d in data["deals"]):
        sys.exit(f"deal '{deal_id}' already exists; use update")
    if args.type not in TYPES:
        sys.exit(f"type must be one of {TYPES}")
    if args.stage not in STAGES:
        sys.exit(f"stage must be one of {list(STAGES)}")
    today = date.today().isoformat()
    d = {
        "id": deal_id,
        "name": args.name,
        "type": args.type,
        "stage": args.stage,
        "tier": args.tier,
        "contacts": [parse_contact(c) for c in (args.contact or [])],
        "referrer": args.referrer,
        "owner": args.owner or "jonathan",
        "tenant_id": args.tenant_id,
        "value_note": args.value,
        "ball": args.ball or "us",
        "last_touch": args.last_touch or today,
        "last_touch_by": args.by or "them",
        "next_step": args.next_step,
        "next_due": args.due,
        "gmail_threads": args.thread or [],
        "notes": args.notes or "",
        "verified": today,
        "history": [{"date": today, "type": "stage", "by": "agent",
                     "note": f"Added at stage {args.stage}" + (f": {args.notes}" if args.notes else "")}],
    }
    data["deals"].append(d)
    save(data)
    append_log({"ts": datetime.now().isoformat(timespec="seconds"), "deal": deal_id,
                "type": "add", "note": f"added ({args.type}/{args.stage})"})
    print(f"added {deal_id}")


def cmd_update(args):
    data = load()
    d = find(data, args.id)
    changes = []
    for kv in args.fields:
        if "=" not in kv:
            sys.exit(f"expected field=value, got '{kv}'")
        k, v = kv.split("=", 1)
        if k == "stage" and v not in STAGES:
            sys.exit(f"stage must be one of {list(STAGES)}")
        if k == "ball" and v not in BALL:
            sys.exit(f"ball must be one of {BALL}")
        if k == "type" and v not in TYPES:
            sys.exit(f"type must be one of {TYPES}")
        if k == "tier":
            v = int(v) if v else None
        elif k == "tenant_id":
            v = int(v) if v else None
        elif k in ("gmail_threads",):
            v = [x for x in v.split(",") if x]
        elif k == "contacts":
            v = [parse_contact(c) for c in v.split(";") if c.strip()]
        elif k == "add_contact":
            d.setdefault("contacts", []).append(parse_contact(v))
            changes.append(f"contact+{v}")
            continue
        elif k == "add_thread":
            if v not in d.setdefault("gmail_threads", []):
                d["gmail_threads"].append(v)
            changes.append(f"thread+{v}")
            continue
        elif v in ("", "null", "None"):
            v = None
        old = d.get(k)
        d[k] = v
        changes.append(f"{k}: {old!r} -> {v!r}")
    d["verified"] = date.today().isoformat()
    save(data)
    append_log({"ts": datetime.now().isoformat(timespec="seconds"), "deal": d["id"],
                "type": "update", "note": "; ".join(changes)})
    print(f"updated {d['id']}: " + "; ".join(changes))


def cmd_log(args):
    data = load()
    d = find(data, args.id)
    when = args.date or date.today().isoformat()
    entry = {"date": when, "type": args.type, "by": args.by, "note": args.note}
    if args.thread:
        entry["thread"] = args.thread
        if args.thread not in d.setdefault("gmail_threads", []):
            d["gmail_threads"].append(args.thread)
    d.setdefault("history", []).append(entry)
    d["history"].sort(key=lambda h: h["date"])
    if args.type in ("email", "meeting", "call") and args.by in ("us", "them"):
        if not d.get("last_touch") or when >= d["last_touch"]:
            d["last_touch"] = when
            d["last_touch_by"] = args.by
            # a touch by them puts the ball with us, and vice versa, unless overridden
            if not args.keep_ball:
                d["ball"] = "us" if args.by == "them" else "them"
    d["verified"] = date.today().isoformat()
    save(data)
    append_log({"ts": datetime.now().isoformat(timespec="seconds"), "deal": d["id"],
                "type": args.type, "by": args.by, "date": when, "note": args.note})
    print(f"logged {args.type} on {d['id']} ({when}, by {args.by}); ball now with {d['ball']}")


def cmd_stage(args):
    data = load()
    d = find(data, args.id)
    if args.new_stage not in STAGES:
        sys.exit(f"stage must be one of {list(STAGES)}")
    old = d["stage"]
    d["stage"] = args.new_stage
    today = date.today().isoformat()
    d.setdefault("history", []).append({"date": today, "type": "stage", "by": "agent",
                                        "note": f"{old} -> {args.new_stage}" + (f": {args.reason}" if args.reason else "")})
    if args.new_stage in ("closed_won", "closed_lost", "churned"):
        d["ball"] = "none"
        d["next_step"] = None
        d["next_due"] = None
    if args.new_stage == "closed_won" and d["type"] == "prospect":
        d["type"] = "customer"
        d["stage"] = "onboarding"
        d["ball"] = "team"
        d["history"][-1]["note"] += " (prospect -> customer/onboarding)"
    d["verified"] = today
    save(data)
    append_log({"ts": datetime.now().isoformat(timespec="seconds"), "deal": d["id"],
                "type": "stage", "note": f"{old} -> {d['stage']}" + (f": {args.reason}" if args.reason else "")})
    print(f"{d['id']}: {old} -> {d['stage']}")


def classify(d: dict, today: date) -> list[str]:
    """Return list of flags for a deal relative to today."""
    flags = []
    stage = d.get("stage")
    if stage in ("closed_won", "closed_lost", "churned", "active", "partner_active"):
        return flags
    last = parse_date(d.get("last_touch"))
    age = days_between(last, today)
    due = parse_date(d.get("next_due"))
    if due:
        if due < today:
            flags.append(f"OVERDUE {(today - due).days}d")
        elif due == today:
            flags.append("DUE TODAY")
        elif (due - today).days <= 2:
            flags.append(f"DUE {due.isoformat()}")
    ball = d.get("ball")
    if ball == "us" and age is not None and age >= 1:
        flags.append(f"YOUR TURN {age}d")
    nudge_after = STAGES.get(stage, ("", None))[1]
    if ball == "them" and nudge_after and age is not None and age >= nudge_after:
        flags.append(f"NUDGE (silent {age}d)")
    if ball == "team" and age is not None and age >= 5:
        flags.append(f"TEAM STALLED {age}d")
    verified = parse_date(d.get("verified"))
    if verified and (today - verified).days > 21:
        flags.append("UNVERIFIED 3w+")
    return flags


def cmd_stale(args):
    data = load()
    today = date.today()
    out = []
    for d in data["deals"]:
        flags = classify(d, today)
        if flags:
            out.append((d, flags))
    for d, flags in sorted(out, key=lambda x: (x[0].get("tier") or 9, x[0]["name"])):
        print(f"[{d.get('tier') or '-'}] {d['name']:<32} {d['stage']:<16} {', '.join(flags)}")
    print(f"\n{len(out)} deals need attention")


def cmd_brief_data(args):
    data = load()
    today = parse_date(args.date) or date.today()
    buckets = {"overdue": [], "due_today": [], "your_turn": [], "nudge": [], "team_stalled": [],
               "upcoming_due": [], "unverified": [], "verbal_yes": [], "at_risk": []}
    for d in data["deals"]:
        flags = classify(d, today)
        item = {"id": d["id"], "name": d["name"], "type": d["type"], "stage": d["stage"],
                "tier": d.get("tier"), "ball": d.get("ball"), "last_touch": d.get("last_touch"),
                "next_step": d.get("next_step"), "next_due": d.get("next_due"),
                "contacts": d.get("contacts", []), "gmail_threads": d.get("gmail_threads", []),
                "value_note": d.get("value_note"), "flags": flags}
        for f in flags:
            if f.startswith("OVERDUE"):
                buckets["overdue"].append(item)
            elif f == "DUE TODAY":
                buckets["due_today"].append(item)
            elif f.startswith("DUE "):
                buckets["upcoming_due"].append(item)
            elif f.startswith("YOUR TURN"):
                buckets["your_turn"].append(item)
            elif f.startswith("NUDGE"):
                buckets["nudge"].append(item)
            elif f.startswith("TEAM"):
                buckets["team_stalled"].append(item)
            elif f.startswith("UNVERIFIED"):
                buckets["unverified"].append(item)
        if d["stage"] == "verbal_yes":
            buckets["verbal_yes"].append(item)
        if d["stage"] == "at_risk":
            buckets["at_risk"].append(item)
    counts = {}
    for d in data["deals"]:
        counts[d["stage"]] = counts.get(d["stage"], 0) + 1
    print(json.dumps({"as_of": today.isoformat(), "stage_counts": counts,
                      "total": len(data["deals"]), **buckets}, indent=2, ensure_ascii=False))


def cmd_render(args):
    data = load()
    today = date.today()
    lines = [f"# Foresite BD Pipeline", "",
             f"_Rendered {today.isoformat()} from `pipeline/deals.json` ({len(data['deals'])} records). "
             f"Do not edit by hand; use `scripts/pipeline.py`._", ""]

    def table(rows):
        lines.append("| Deal | Stage | Contact | Ball | Last touch | Next step | Due | Flags |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for d in rows:
            c = d.get("contacts") or [{}]
            contact = c[0].get("name") or c[0].get("email") or ""
            age = days_between(parse_date(d.get("last_touch")), today)
            last = f"{d.get('last_touch') or ''} ({age}d)" if age is not None else ""
            flags = ", ".join(classify(d, today))
            lines.append(f"| **{d['name']}** | {d['stage']} | {contact} | {d.get('ball','')} | {last} | "
                         f"{(d.get('next_step') or '').replace('|','/')} | {d.get('next_due') or ''} | {flags} |")
        lines.append("")

    prospects = [d for d in data["deals"] if d["type"] == "prospect"]
    lines.append("## Prospects")
    lines.append("")
    for tier in sorted({d.get("tier") or 9 for d in prospects}):
        rows = [d for d in prospects if (d.get("tier") or 9) == tier]
        lines.append(f"### {PROSPECT_TIER_ORDER.get(tier, f'Tier {tier}')} ({len(rows)})")
        lines.append("")
        table(sorted(rows, key=lambda d: d["name"]))
    for t, title in [("customer", "Customers (lifecycle watch)"), ("winback", "Winback book"),
                     ("partner", "Partners & referrers"), ("channel", "Channel & enterprise"),
                     ("investor", "Investors"), ("vendor", "Vendors"), ("advisor", "Advisors")]:
        rows = [d for d in data["deals"] if d["type"] == t]
        if rows:
            lines.append(f"## {title} ({len(rows)})")
            lines.append("")
            table(sorted(rows, key=lambda d: d["name"]))
    with open(RENDER_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {os.path.relpath(RENDER_PATH, ROOT)}")


def cmd_validate(args):
    data = load()
    ids = set()
    problems = 0
    for d in data["deals"]:
        for req in ("id", "name", "type", "stage"):
            if not d.get(req):
                print(f"missing {req}: {d}")
                problems += 1
        if d["id"] in ids:
            print(f"duplicate id {d['id']}")
            problems += 1
        ids.add(d["id"])
        if d.get("type") not in TYPES:
            print(f"{d['id']}: bad type {d.get('type')}")
            problems += 1
        if d.get("stage") not in STAGES:
            print(f"{d['id']}: bad stage {d.get('stage')}")
            problems += 1
        if d.get("ball") not in BALL:
            print(f"{d['id']}: bad ball {d.get('ball')}")
            problems += 1
        for k in ("last_touch", "next_due", "verified"):
            if d.get(k):
                try:
                    parse_date(d[k])
                except ValueError:
                    print(f"{d['id']}: bad date in {k}: {d[k]}")
                    problems += 1
    print(f"{len(data['deals'])} deals, {problems} problems")
    sys.exit(1 if problems else 0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list"); s.add_argument("--type"); s.add_argument("--stage"); s.add_argument("--ball")
    s.add_argument("--tier", type=int); s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_list)

    s = sub.add_parser("show"); s.add_argument("id"); s.set_defaults(fn=cmd_show)

    s = sub.add_parser("add")
    s.add_argument("--id"); s.add_argument("--name", required=True); s.add_argument("--type", required=True)
    s.add_argument("--stage", required=True); s.add_argument("--tier", type=int)
    s.add_argument("--contact", action="append", help="'Name <email>|Role' (repeatable)")
    s.add_argument("--referrer"); s.add_argument("--owner"); s.add_argument("--tenant-id", type=int)
    s.add_argument("--value"); s.add_argument("--ball"); s.add_argument("--last-touch"); s.add_argument("--by")
    s.add_argument("--next-step"); s.add_argument("--due"); s.add_argument("--thread", action="append")
    s.add_argument("--notes"); s.set_defaults(fn=cmd_add)

    s = sub.add_parser("update"); s.add_argument("id"); s.add_argument("fields", nargs="+"); s.set_defaults(fn=cmd_update)

    s = sub.add_parser("log"); s.add_argument("id"); s.add_argument("note")
    s.add_argument("--type", default="note", choices=["email", "meeting", "call", "note", "stage", "draft", "task"])
    s.add_argument("--by", default="us", choices=BALL + ["agent"]); s.add_argument("--date"); s.add_argument("--thread")
    s.add_argument("--keep-ball", action="store_true", help="do not flip ball on this touch"); s.set_defaults(fn=cmd_log)

    s = sub.add_parser("stage"); s.add_argument("id"); s.add_argument("new_stage"); s.add_argument("reason", nargs="?")
    s.set_defaults(fn=cmd_stage)

    s = sub.add_parser("stale"); s.add_argument("--days", type=int, default=5); s.set_defaults(fn=cmd_stale)
    s = sub.add_parser("brief-data"); s.add_argument("--date"); s.set_defaults(fn=cmd_brief_data)
    s = sub.add_parser("render"); s.set_defaults(fn=cmd_render)
    s = sub.add_parser("validate"); s.set_defaults(fn=cmd_validate)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
