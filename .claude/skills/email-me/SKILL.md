---
name: email-me
description: Send a short HTML email to your own inbox via Gmail SMTP (App Password auth). Used by daily-brief and available for any other skill that needs to land something in your inbox. Run with /email-me, or invoked by other skills.
---

# Email Me

A thin, reusable sending capability — not a skill you run for its own sake
usually, but the thing other skills (like `daily-brief`) hand off to when
they need to land in your inbox instead of just chat.

## How it works

`send_email.py` in this folder sends via Gmail SMTP using an App Password
(stored in `.env` as `GMAIL_ADDRESS` / `GMAIL_APP_PASSWORD` — never in
chat, never committed). It only sends; it never reads your inbox.

Usage: write the HTML body to a temp file, then:
```
python .claude/skills/email-me/send_email.py "<subject>" <path_to_html_file>
```
Defaults to sending to your own address (`GMAIL_ADDRESS`). Pass `--to
<address>` to send elsewhere.

## When another skill uses this

Keep the HTML simple and self-contained (inline styles, no external
assets) — it needs to render cleanly in a phone email client, not look like
a full web page. A short header, the content, done.
