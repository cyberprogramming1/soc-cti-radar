import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

BAKU_TZ = timezone(timedelta(hours=4))
NOW_BAKU = datetime.now(BAKU_TZ).strftime("%Y-%m-%d %H:%M (+04)")

# Genişləndirilmiş CTI & Xəbər Mənbələri (RSS)
RSS_FEEDS = [
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("SecurityWeek", "https://feeds.feedburner.com/securityweek"),
    ("Dark Reading", "https://www.darkreading.com/rss.xml"),
    ("Threatpost", "https://threatpost.com/feed/"),
    ("CERT.az", "https://cert.az/az/rss"),
    ("CISA Advisories", "https://www.cisa.gov/cybersecurity-advisories/all.xml"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("AlienVault OTX Pulse", "https://otx.alienvault.com/otxapi/pulses/subscribed?format=xml"),
]

CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


def fetch_url(url: str, timeout: int = 15) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; SOC-CTI-Radar/2.0; +https://github.com)"
        }
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def clean_html(text: str) -> str:
    no_tags = re.sub(r"<[^>]+>", " ", text or "")
    collapsed = re.sub(r"\s+", " ", no_tags).strip()
    if len(collapsed) > 220:
        return collapsed[:217] + "..."
    return collapsed


def get_rss_news(limit_per_feed: int = 3) -> list:
    items = []
    for source_name, feed_url in RSS_FEEDS:
        try:
            raw = fetch_url(feed_url)
            root = ET.fromstring(raw)
            entries = root.findall(".//item")
            if not entries:
                entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")

            count = 0
            for entry in entries:
                title = (
                    entry.findtext("title")
                    or entry.findtext("{http://www.w3.org/2005/Atom}title")
                    or ""
                ).strip()

                link = (entry.findtext("link") or "").strip()
                if not link:
                    atom_link = entry.find("{http://www.w3.org/2005/Atom}link")
                    if atom_link is not None:
                        link = (atom_link.attrib.get("href") or "").strip()

                pub_date = (
                    entry.findtext("pubDate")
                    or entry.findtext("updated")
                    or entry.findtext("{http://www.w3.org/2005/Atom}updated")
                    or NOW_BAKU
                ).strip()

                desc = (
                    entry.findtext("description")
                    or entry.findtext("summary")
                    or entry.findtext("{http://www.w3.org/2005/Atom}summary")
                    or ""
                )

                if title and link:
                    items.append({
                        "source": source_name,
                        "feed_url": feed_url,
                        "title": clean_html(title),
                        "summary": clean_html(desc),
                        "date": pub_date,
                        "url": link
                    })
                    count += 1
                if count >= limit_per_feed:
                    break
        except Exception as e:
            items.append({
                "source": source_name,
                "feed_url": feed_url,
                "title": f"[{source_name}] mənbəsi əlçatan olmadı",
                "summary": str(e),
                "date": NOW_BAKU,
                "url": feed_url
            })
    return items


def get_latest_cisa_cves(limit: int = 8) -> list:
    try:
        raw = fetch_url(CISA_KEV_URL)
        data = json.loads(raw.decode("utf-8"))
        vulns = data.get("vulnerabilities", [])
        latest = sorted(vulns, key=lambda x: x.get("dateAdded", ""), reverse=True)[:limit]
        result = []
        for v in latest:
            result.append({
                "source": "CISA KEV",
                "cveID": v.get("cveID", "N/A"),
                "vendor": v.get("vendorProject", "Unknown"),
                "product": v.get("product", "Unknown"),
                "name": v.get("vulnerabilityName", ""),
                "dateAdded": v.get("dateAdded", ""),
                "dueDate": v.get("dueDate", ""),
                "action": v.get("requiredAction", ""),
                "ransomware": v.get("knownRansomwareCampaignUse", "Unknown")
            })
        return result
    except Exception as e:
        return [{
            "source": "CISA KEV",
            "cveID": "ERROR",
            "vendor": "CISA",
            "product": "Feed",
            "name": str(e)
        }]


def send_telegram_notification(news: list, cves: list):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    webapp_url = os.environ.get("WEBAPP_URL", "").strip()

    if not token or not chat_id:
        print("Telegram secret-ləri tapılmadı, mesaj göndərilmədi.")
        return

    active_sources = sorted({n["source"] for n in news if "əlçatan olmadı" not in n["title"]})
    lines = [
        "🛡️ *SOC & CTI Radar Yeniləməsi*",
        f"🕒 Vaxt: `{NOW_BAKU}`",
        f"📡 Aktiv Mənbələr ({len(active_sources)}): {', '.join(active_sources[:6])}",
        "",
        "*⚠️ Ən Son CISA KEV Zəiflikləri:*"
    ]
    for c in cves[:4]:
        lines.append(f"• `{c['cveID']}` — {c['vendor']} {c['product']} ({c['dateAdded']})")

    lines.append("")
    lines.append("*📰 Ən Son Kiber Xəbərlər:*")
    for n in news[:5]:
        lines.append(f"• [{n['source']}] {n['title']}")

    text = "\n".join(lines)

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    if webapp_url:
        payload["reply_markup"] = {
            "inline_keyboard": [[
                {
                    "text": "📲 SOC & CTI Operativ App-i Aç",
                    "web_app": {"url": webapp_url}
                }
            ]]
        }

    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("Telegram cavabı:", resp.status)


def main():
    news = get_rss_news(limit_per_feed=3)
    cves = get_latest_cisa_cves(limit=8)
    sources_list = [{"name": s, "url": u} for s, u in RSS_FEEDS] + [
        {"name": "CISA KEV Catalog", "url": CISA_KEV_URL}
    ]

    output = {
        "updated_at": NOW_BAKU,
        "sources": sources_list,
        "news": news,
        "cves": cves
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    send_telegram_notification(news, cves)


if __name__ == "__main__":
    main()
