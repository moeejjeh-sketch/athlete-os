"""
Send an HTML email to yourself via Gmail SMTP (App Password auth).
Read-only w.r.t. everything except sending this one email — no inbox access.

Usage: python send_email.py "<subject>" <path_to_html_body_file> [--to <address>]
Body is read from a file (not a CLI arg) to avoid shell-escaping issues with HTML.
"""
import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

def read_env():
    values = {}
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, _, v = s.partition("=")
            values[k.strip()] = v.strip()
    return values

def main():
    if len(sys.argv) < 3:
        print("Usage: python send_email.py \"<subject>\" <path_to_html_body_file> [--to <address>]")
        sys.exit(1)

    subject = sys.argv[1]
    body_path = sys.argv[2]
    to_addr = None
    if "--to" in sys.argv:
        to_addr = sys.argv[sys.argv.index("--to") + 1]

    env = read_env()
    gmail_addr = env["GMAIL_ADDRESS"]
    app_password = env["GMAIL_APP_PASSWORD"]
    to_addr = to_addr or gmail_addr

    with open(body_path, "r", encoding="utf-8") as f:
        html_body = f.read()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(gmail_addr, app_password)
        server.sendmail(gmail_addr, to_addr, msg.as_string())

    print(f"SENT to {to_addr}")

if __name__ == "__main__":
    main()
