import datetime
import html
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from email.utils import formataddr

import feedparser

FEEDS = [
    ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml"),
    ("CNN", "http://rss.cnn.com/rss/edition.rss"),
    (
        "Reuters Top News (Google News)",
        "https://news.google.com/rss/search?q=site:reuters.com&hl=en-US&gl=US&ceid=US:en",
    ),
    ("New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"),
    ("CNA Politics", "https://feeds.feedburner.com/rsscna/politics"),
    ("CNA International", "https://feeds.feedburner.com/rsscna/intworld"),
    ("CNA Finance", "https://feeds.feedburner.com/rsscna/finance"),
    ("UDN (United Daily News)", "https://udn.com/news/rssfeed/6638"),
    ("Liberty Times", "https://news.ltn.com.tw/rss/all.xml"),
    ("EBC / ETtoday", "https://feeds.feedburner.com/ettoday/realtime"),
    (
        "TVBS (Google News)",
        "https://news.google.com/rss/search?q=site:news.tvbs.com.tw&hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
    ),
]

MAX_ITEMS_PER_FEED = 20
DEFAULT_TO_EMAIL = "aaaaaaaaaaaaaaa@gmail.com"


def safe_text(value):
    if value is None:
        return ""

    text = str(value)
    encoding = sys.stdout.encoding or "utf-8"
    try:
        text.encode(encoding)
        return text
    except UnicodeEncodeError:
        return text.encode(encoding, errors="replace").decode(encoding, errors="replace")


def safe_print(value=""):
    print(safe_text(value))


def fetch_all_feeds():
    sections = []

    for source_name, url in FEEDS:
        section = {
            "source_name": source_name,
            "title": source_name,
            "items": [],
            "status": "ok",
            "message": "",
        }

        try:
            feed = feedparser.parse(url)
        except UnicodeDecodeError as err:
            section["status"] = "error"
            section["message"] = f"Unicode decode error: {err}"
            sections.append(section)
            continue
        except Exception as err:
            section["status"] = "error"
            section["message"] = f"Feed parse failed: {err}"
            sections.append(section)
            continue

        if not feed:
            section["status"] = "error"
            section["message"] = "Empty feed object"
            sections.append(section)
            continue

        feed_meta = getattr(feed, "feed", {}) or {}
        entries = getattr(feed, "entries", None) or []

        section["title"] = feed_meta.get("title", source_name)

        if not entries:
            section["status"] = "empty"
            section["message"] = "No entries available"
            sections.append(section)
            continue

        for entry in entries[:MAX_ITEMS_PER_FEED]:
            entry_title = entry.get("title", "(No title)")
            entry_link = entry.get("link", "")
            section["items"].append({
                "title": entry_title,
                "link": entry_link,
            })

        sections.append(section)

    return sections


def build_plain_content(report_date, sections):
    lines = [f"News Digest - {report_date}", ""]

    for section in sections:
        lines.append(f"[{section['title']}]")

        if section["items"]:
            for item in section["items"]:
                lines.append(f"- {item['title']}")
                if item["link"]:
                    lines.append(f"  {item['link']}")
        else:
            lines.append(f"- {section['message']}")

        lines.append("")

    return "\n".join(lines)


def build_html_content(report_date, sections):
    cards = []

    for section in sections:
        items_html = ""
        if section["items"]:
            item_rows = []
            for item in section["items"]:
                title = html.escape(item["title"])
                link = html.escape(item["link"])
                if item["link"]:
                    item_rows.append(
                        f"<li><a href=\"{link}\" target=\"_blank\">{title}</a></li>"
                    )
                else:
                    item_rows.append(f"<li>{title}</li>")
            items_html = "<ul>" + "".join(item_rows) + "</ul>"
        else:
            msg = html.escape(section["message"])
            items_html = f"<p class=\"hint\">{msg}</p>"

        cards.append(
            "".join(
                [
                    "<section class=\"card\">",
                    f"<h2>{html.escape(section['title'])}</h2>",
                    items_html,
                    "</section>",
                ]
            )
        )

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>News Digest</title>
  <style>
    body {{
      margin: 0;
      padding: 24px;
      font-family: "Segoe UI", Tahoma, Arial, sans-serif;
      background: #f2f5f9;
      color: #1f2937;
    }}
    .wrap {{
      max-width: 900px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 14px;
      padding: 24px;
      box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    }}
    h1 {{
      margin: 0 0 6px;
      color: #0f172a;
      font-size: 28px;
    }}
    .date {{
      margin: 0 0 20px;
      color: #64748b;
      font-size: 14px;
    }}
    .card {{
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 14px 16px;
      margin-bottom: 12px;
      background: #fbfdff;
    }}
    h2 {{
      margin: 0 0 10px;
      font-size: 18px;
      color: #0f172a;
    }}
    ul {{
      margin: 0;
      padding-left: 20px;
    }}
    li {{
      margin-bottom: 6px;
      line-height: 1.45;
    }}
    a {{
      color: #0b5ed7;
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    .hint {{
      margin: 0;
      color: #6b7280;
      font-style: italic;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>News Digest</h1>
    <p class="date">{html.escape(str(report_date))}</p>
    {''.join(cards)}
  </div>
</body>
</html>
""".strip()


def send_email(subject, plain_content, html_content, to_email):
    sender = os.getenv("NEWS_EMAIL_SENDER")
    password = os.getenv("NEWS_EMAIL_APP_PASSWORD")
    smtp_host = os.getenv("NEWS_SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("NEWS_SMTP_PORT", "465"))

    if not sender or not password:
        raise RuntimeError(
            "Missing env vars: NEWS_EMAIL_SENDER / NEWS_EMAIL_APP_PASSWORD"
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr(("RSS新聞發送", sender))
    msg["To"] = to_email
    msg.set_content(plain_content)
    msg.add_alternative(html_content, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)


def main():
    report_date = datetime.date.today()
    subject = f"News Digest - {report_date}"
    to_email = os.getenv("NEWS_TO_EMAIL", DEFAULT_TO_EMAIL)

    sections = fetch_all_feeds()
    plain_content = build_plain_content(report_date, sections)
    html_content = build_html_content(report_date, sections)

    safe_print(plain_content)

    try:
        send_email(subject, plain_content, html_content, to_email)
        safe_print(f"\\nEmail sent to {to_email}")
    except Exception as err:
        safe_print(f"\\nEmail send failed: {err}")


if __name__ == "__main__":
    main()





