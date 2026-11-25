import datetime
import html
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

TZ_AZ = datetime.timezone(datetime.timedelta(hours=4))

# RSS / Atom mənbələri
RSS_SOURCES = [
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("SecurityWeek", "https://feeds.feedburner.com/securityweek"),
    ("Dark Reading", "https://www.darkreading.com/rss.xml"),
    ("CISA Advisories", "https://www.cisa.gov/cybersecurity-advisories/all.xml"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("Securelist (Kaspersky)", "https://securelist.com/feed/"),
    ("Secjuice", "https://www.secjuice.com/feed/"),
    ("Cyber Detective", "https://cybdetective.com/feed/"),
    ("Hatless1der", "https://hatless1der.com/feed/"),
    ("OSINT Me", "https://www.osintme.com/feed/"),
    ("Nixintel", "https://nixintel.info/feed/"),
    ("ESPY OSINT Blog", "https://espysys.com/blog/feed/"),
    ("OSINT Team", "https://www.osintteam.com/feed/"),
    ("Intel471 Blog", "https://www.intel471.com/blog/feed"),
    ("DailyDarkWeb", "https://dailydarkweb.net/feed/"),
]

# CTI, Leak, Darkweb, Malware Analysis & News səhifələri (dedup olunmuş)
RAW_WEB_SOURCES = [
    ("LeakFA Leaks", "https://leakfa.com/leaks"),
    ("BF.st DB Index", "https://bf.st/Announcement-Database-Index"),
    ("Kalir Pulse AZAL Brief", "https://pulse.kalir.io/en/brief/base-de-datos-de-azerbaijan-airlines-eca8fae5"),
    ("Kalir Pulse", "https://pulse.kalir.io/en/"),
    ("X LeakFarsi", "https://x.com/leakfarsi"),
    ("SecretLine", "https://secretline.top/"),
    ("Onion - OP7YIEK (Tor only)", "http://op7yiekgumt7po6mjgii4uewrwjydx5vhpa6y5gv7glftmw5srbwnaid.onion/"),
    ("DarkForums", "https://darkforums.as/"),
    ("Patched.to Leaks", "https://patched.to/Forum-other-leaks"),
    ("TweetFeed", "https://tweetfeed.live/"),
    ("Ransomware.live", "https://www.ransomware.live/"),
    ("Triage Sandbox", "https://tria.ge/260305-d6x8rsc15x"),
    ("JaffaCakes Analysis", "https://jaffacakes118.dev/analysis/b8d179cca6fe61ae175cc8c2f4377d1c249c24a73dc616358267f02d23d61776"),
    ("CERT.pl MWDB", "https://mwdb.cert.pl/file/dd7fca91c67710c4872e1c8fa62acbaedd94cd8bc673c4e3c9d5aa60e9902518"),
    ("DailyDarkWeb", "https://dailydarkweb.net/"),
    ("Securelist", "https://securelist.com/"),
    ("Life.ru", "https://life.ru/p/1849559"),
    ("VM.ru Infra", "https://vm.ru/news/1308971-prorossijskie-hakery-vzlomali-sistemy-kriticheskoj-infrastruktury-izrailya"),
    ("Telegram CyberGuerre", "https://t.me/cyberguerre/3953"),
    ("Ridus", "https://www.ridus.ru/z-pentest-alliance-vzlomali-sistemy-nasosov-na-obektah-izrailya-804595.html"),
    ("News Mail.ru", "https://news.mail.ru/society/70075193/"),
    ("MK.ru", "https://www.mk.ru/politics/2026/03/07/gruppa-khakerov-s-prorossiyskimi-vzglyadami-vzlomala-chast-kriticheskikh-obektov-izrailya.html"),
    ("News.ru", "https://news.ru/society/prorossijskie-hakery-vzlomali-sistemy-upravleniya-nasosami-v-izraile"),
    ("Gazeta.ru Tech", "https://www.gazeta.ru/tech/news/2026/03/07/28009429.shtml"),
    ("SMI2 #1", "https://smi2.ru/article/181077136/story"),
    ("SMI2 #2", "https://smi2.ru/article/181088846/story"),
    ("Rambler News", "https://news.rambler.ua/army/56147635-prorossiyskie-hakery-vzlomali-sistemy-kriticheskoy-infrastruktury-izrailya/"),
    ("Tsargrad", "https://tsargrad.tv/novost/entest-vzlomany-sistemy-nasosov-kriticheskoj-infrastruktury-izrailja_1587505"),
    ("VZ.ru", "https://vz.ru/news/2026/3/7/1400342.html"),
    ("SAK-Info", "https://sak-info.com/vlast/item/188817-z-pentest-alliance-vzlomali-sistemy-nasosov-na-obektah-izrailya"),
    ("Rodina.news", "https://rodina.news/hakery-zpentest-alliance-vzlomali-sistemy-kriticheskoi-26030718235844.htm"),
    ("MySeldon", "https://myseldon.com/en/news/index/342789446"),
    ("AlarmyK24", "https://alarmyk24.ru/news/3882425/prorossijskie-hakery-vzlomali-sistemy-kriticheskoj-infrastruktury-izrailya.html"),
    ("Cyber Intelligence House", "http://www.cyberintelligencehouse.com"),
    ("Sector035 (LinkedIn)", "https://lnkd.in/dVZ8iVA3"),
    ("Authentic8 Blog (LinkedIn)", "https://lnkd.in/dGc6wiVb"),
    ("Rae Baker Blog (LinkedIn)", "https://lnkd.in/d57YnaAj"),
    ("VEEXH Medium", "https://medium.com/@VEEXH"),
    ("OH SHINT Blog (LinkedIn)", "https://lnkd.in/d9UvBrT5"),
    ("OSINT Combine (LinkedIn)", "https://lnkd.in/ducHTp2X"),
    ("Bellingcat (LinkedIn)", "https://lnkd.in/dMTN2dNh"),
    ("Skopenow Blog (LinkedIn)", "https://lnkd.in/dfE3dc3q"),
    ("ShadowDragon Blog (LinkedIn)", "https://lnkd.in/dajF3QcN"),
    ("Maltego Blog (LinkedIn)", "https://lnkd.in/dzV4bmn8"),
    ("Social Links Blog (LinkedIn)", "https://lnkd.in/dkhvmhRX"),
    ("Blackdot Solutions (LinkedIn)", "https://lnkd.in/d8MYqXZB"),
    ("Offensive OSINT (LinkedIn)", "https://lnkd.in/dF3Fkbyc"),
    ("OSINT Industries (LinkedIn)", "https://lnkd.in/eCrSKUmK"),
    ("Reza Abasi LinkedIn", "https://www.linkedin.com/in/reza-abasi/"),
    ("Blackbones.net", "https://blackbones.net/"),
    ("DarknetList", "https://darknetlist.info/"),
    ("Dead-Frog", "https://www.dead-frog.com/"),
    ("Onion - Tenebris (Tor only)", "http://tenebrispoyfrcup4k24lciwrh4gc5735hmld4dweq7his7zh423opqd.onion/"),
    ("Onion - Dread #1 (Tor only)", "https://dreadytofatroptsdj6io7l3xptbet6onoyno2yv7jicoxknyazubrad.onion/"),
    ("Onion - Dread #2 (Tor only)", "https://dreadytognbh7m5nlmqsogzzlxjy75iuxkulewbhxcorupbqahact2yd.onion/"),
    ("FlakkaOnline", "https://flakkaonline.com/"),
    ("Blackbones.cc", "https://blackbones.cc/"),
]

CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

IP_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b")
URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)
HASH_RE = re.compile(r"\b(?:[a-fA-F0-9]{64}|[a-fA-F0-9]{40}|[a-fA-F0-9]{32})\b")
CVE_RE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)
DOMAIN_RE = re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+(?:ru|su|cn|tk|xyz|top|cc|pw|io|com|net|org|info|live|dev)\b", re.IGNORECASE)

DARKWEB_KEYWORDS = (
    "leak", "breach", "ransomware", "darkweb", "dark web", "stealer",
    "extortion", "vishing", "database", "dump", "forum", "onion", "payload", "malware"
)


def now_az_str():
    return datetime.datetime.now(TZ_AZ).strftime("%Y-%m-%d %H:%M (+04)")


def deduplicate_sources():
    seen_urls = set()
    unique_web = []
    for name, url in RAW_WEB_SOURCES:
        norm = url.strip().rstrip("/").lower()
        if norm in seen_urls:
            continue
        seen_urls.add(norm)
        unique_web.append((name, url.strip()))
    return unique_web


def http_get_text(url, headers=None, timeout=12):
    req = urllib.request.Request(
        url,
        headers=headers or {
            "User-Agent": "Mozilla/5.0 (compatible; SOC-CTI-Radar/3.0; +https://github.com)"
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def http_get_json(url, headers=None, timeout=12):
    return json.loads(http_get_text(url, headers=headers, timeout=timeout))


def http_post_form(url, data_dict, headers=None, timeout=12):
    encoded = urllib.parse.urlencode(data_dict).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=encoded,
        headers=headers or {"User-Agent": "SOC-CTI-Radar/3.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="ignore"))


def clean_html(text):
    text = html.unescape(text or "")
    text = re.sub(r"<script.*?>.*?</script>|<style.*?>.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def classify_category(source_name, title, summary, url):
    blob = f"{source_name} {title} {summary} {url}".lower()
    if any(k in blob for k in DARKWEB_KEYWORDS) or any(
        d in url.lower() for d in ("leakfa", "darkforums", "patched.to", "ransomware.live", "dailydarkweb", "darknetlist", "blackbones", "secretline", "bf.st", "tria.ge", "mwdb.cert.pl")
    ):
        return "darkweb_cti"
    return "global_cyber"


def fetch_rss_news():
    items = []
    for name, url in RSS_SOURCES:
        try:
            xml_data = http_get_text(url)
            root = ET.fromstring(xml_data)
            for elem in root.findall(".//item")[:5]:
                title = clean_html(elem.findtext("title") or "")
                link = (elem.findtext("link") or "").strip() or url
                desc = clean_html(elem.findtext("description") or "")[:260]
                pub_date = (elem.findtext("pubDate") or "")[:16]
                if title:
                    items.append({
                        "source": name,
                        "category": classify_category(name, title, desc, link),
                        "title": title,
                        "summary": desc,
                        "url": link,
                        "date": pub_date,
                    })
        except Exception:
            continue
    return items


def fetch_web_sources_items(web_sources):
    items = []
    for name, url in web_sources:
        if ".onion" in url.lower():
            items.append({
                "source": name,
                "category": "darkweb_cti",
                "title": f"{name} — Tor/Onion mənbə qeydi",
                "summary": "Onion ünvanı Tor şəbəkəsi tələb edir; birbaşa HTTP runner-də qeydə alınıb.",
                "url": url,
                "date": now_az_str()[:10],
            })
            continue

        try:
            raw = http_get_text(url, timeout=10)
            title_m = re.search(r"<title[^>]*>(.*?)</title>", raw, flags=re.S | re.I)
            page_title = clean_html(title_m.group(1)) if title_m else name
            text_body = clean_html(raw)
            snippet = text_body[:240] if text_body else f"{name} mənbəsindən məlumat toplandı."
            items.append({
                "source": name,
                "category": classify_category(name, page_title, snippet, url),
                "title": page_title[:140] or name,
                "summary": snippet,
                "url": url,
                "date": now_az_str()[:10],
            })
        except Exception as e:
            items.append({
                "source": name,
                "category": classify_category(name, name, "", url),
                "title": f"{name} (canlı sorğu məhdud/bloklu)",
                "summary": f"Mənbə qeydə alındı ({str(e)[:80]}).",
                "url": url,
                "date": now_az_str()[:10],
            })
    return items


def deduplicate_news(items):
    seen = set()
    out = []
    for it in items:
        key = f"{(it.get('url') or '').strip().lower()}|{(it.get('title') or '').strip().lower()[:90]}"
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def fetch_cisa_kev():
    try:
        data = http_get_json(CISA_KEV_URL)
        vulns = data.get("vulnerabilities") or []
        vulns_sorted = sorted(vulns, key=lambda x: x.get("dateAdded", ""), reverse=True)
        out = []
        for v in vulns_sorted[:15]:
            out.append({
                "cveID": v.get("cveID", ""),
                "vendor": v.get("vendorProject", ""),
                "product": v.get("product", ""),
                "name": v.get("vulnerabilityName", ""),
                "dateAdded": v.get("dateAdded", ""),
                "ransomware": v.get("knownRansomwareCampaignUse", ""),
                "action": v.get("requiredAction", ""),
            })
        return out
    except Exception:
        return []


def extract_and_dedup_iocs(news_items, cves):
    seen = set()
    iocs = []
    excluded_domains = {
        "bleepingcomputer.com", "thehackernews.com", "securityweek.com",
        "darkreading.com", "cisa.gov", "krebsonsecurity.com", "securelist.com",
        "secjuice.com", "cybdetective.com", "hatless1der.com", "osintme.com",
        "nixintel.info", "espysys.com", "osintteam.com", "intel471.com",
        "dailydarkweb.net", "github.com", "linkedin.com", "lnkd.in",
        "medium.com", "x.com", "t.me", "ransomware.live", "tweetfeed.live",
        "leakfa.com", "darkforums.as", "patched.to", "darknetlist.info",
        "blackbones.net", "blackbones.cc", "secretline.top", "bf.st",
        "pulse.kalir.io", "tria.ge", "mwdb.cert.pl", "flakkaonline.com",
    }

    def add_ioc(ioc_type, raw_val, origin):
        val = (raw_val or "").strip().strip(".,;:\"'()[]{}<>")
        if not val:
            return
        norm = val.upper() if ioc_type == "cve" else val.lower() if ioc_type in ("domain", "url", "hash") else val
        if ioc_type == "domain":
            if any(norm == d or norm.endswith("." + d) for d in excluded_domains):
                return
        key = f"{ioc_type}:{norm}"
        if key in seen:
            return
        seen.add(key)
        iocs.append({
            "type": ioc_type,
            "value": norm,
            "origin": origin,
            "level": "LOW",
            "score": 10,
            "reasons": [],
            "checks": {},
        })

    for n in news_items:
        blob = f"{n.get('title', '')} {n.get('summary', '')}"
        origin = f"{n.get('source', 'CTI')}: {n.get('title', '')[:65]}"
        for u in URL_RE.findall(blob):
            add_ioc("url", u, origin)
        for ip in IP_RE.findall(blob):
            if not ip.startswith(("127.", "10.", "192.168.", "0.", "172.16.")):
                add_ioc("ip", ip, origin)
        for h in HASH_RE.findall(blob):
            add_ioc("hash", h, origin)
        for cve in CVE_RE.findall(blob):
            add_ioc("cve", cve, origin)
        for d in DOMAIN_RE.findall(blob):
            add_ioc("domain", d, origin)

    for c in cves:
        if c.get("cveID"):
            add_ioc("cve", c["cveID"], f"CISA KEV: {c.get('vendor', '')} {c.get('product', '')}")

    return iocs[:40]


def check_urlhaus(ioc):
    auth = os.environ.get("URLHAUS_AUTH_KEY", "").strip()
    headers = {"User-Agent": "SOC-CTI-Radar/3.0"}
    if auth:
        headers["Auth-Key"] = auth
    try:
        if ioc["type"] == "url":
            res = http_post_form("https://urlhaus-api.abuse.ch/v1/url/", {"url": ioc["value"]}, headers=headers)
            if res.get("query_status") == "ok":
                return {"hit": True, "threat": res.get("threat") or "listed_url", "score_add": 45}
        elif ioc["type"] == "domain":
            host = ioc["value"].split("/")[0]
            res = http_post_form("https://urlhaus-api.abuse.ch/v1/host/", {"host": host}, headers=headers)
            if res.get("query_status") == "ok" and (res.get("urls") or []):
                return {"hit": True, "threat": f"urls:{len(res.get('urls', []))}", "score_add": 40}
        elif ioc["type"] == "hash":
            algo = "sha256_hash" if len(ioc["value"]) == 64 else "md5_hash"
            res = http_post_form("https://urlhaus-api.abuse.ch/v1/payload/", {algo: ioc["value"]}, headers=headers)
            if res.get("query_status") == "ok":
                return {"hit": True, "threat": res.get("signature") or "malware_payload", "score_add": 50}
    except Exception as e:
        return {"hit": False, "error": str(e)[:80], "score_add": 0}
    return {"hit": False, "score_add": 0}


def check_virustotal(ioc):
    key = os.environ.get("VT_API_KEY", "").strip()
    if not key:
        return {"skipped": True, "score_add": 0}
    headers = {"x-apikey": key, "User-Agent": "SOC-CTI-Radar/3.0"}
    try:
        if ioc["type"] == "ip":
            ep = f"https://www.virustotal.com/api/v3/ip_addresses/{urllib.parse.quote(ioc['value'])}"
        elif ioc["type"] == "domain":
            ep = f"https://www.virustotal.com/api/v3/domains/{urllib.parse.quote(ioc['value'])}"
        elif ioc["type"] == "hash":
            ep = f"https://www.virustotal.com/api/v3/files/{urllib.parse.quote(ioc['value'])}"
        else:
            return {"skipped": True, "score_add": 0}

        data = http_get_json(ep, headers=headers)
        stats = (((data.get("data") or {}).get("attributes") or {}).get("last_analysis_stats")) or {}
        mal = int(stats.get("malicious", 0))
        susp = int(stats.get("suspicious", 0))
        return {"malicious": mal, "suspicious": susp, "score_add": min(60, mal * 10 + susp * 4)}
    except Exception as e:
        return {"error": str(e)[:80], "score_add": 0}


def check_abuseipdb(ioc):
    if ioc["type"] != "ip":
        return {"skipped": True, "score_add": 0}
    key = os.environ.get("ABUSEIPDB_API_KEY", "").strip()
    if not key:
        return {"skipped": True, "score_add": 0}
    try:
        q = urllib.parse.urlencode({"ipAddress": ioc["value"], "maxAgeInDays": "30"})
        data = http_get_json(
            f"https://api.abuseipdb.com/api/v2/check?{q}",
            headers={"Key": key, "Accept": "application/json", "User-Agent": "SOC-CTI-Radar/3.0"},
        )
        d = data.get("data") or {}
        conf = int(d.get("abuseConfidenceScore", 0))
        return {"confidence": conf, "reports": d.get("totalReports", 0), "score_add": int(conf * 0.5)}
    except Exception as e:
        return {"error": str(e)[:80], "score_add": 0}


def check_otx(ioc):
    key = os.environ.get("OTX_API_KEY", "").strip()
    headers = {"User-Agent": "SOC-CTI-Radar/3.0"}
    if key:
        headers["X-OTX-API-KEY"] = key
    try:
        if ioc["type"] == "ip":
            ep = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{urllib.parse.quote(ioc['value'])}/general"
        elif ioc["type"] == "domain":
            ep = f"https://otx.alienvault.com/api/v1/indicators/domain/{urllib.parse.quote(ioc['value'])}/general"
        elif ioc["type"] == "hash":
            ep = f"https://otx.alienvault.com/api/v1/indicators/file/{urllib.parse.quote(ioc['value'])}/general"
        else:
            return {"skipped": True, "score_add": 0}

        data = http_get_json(ep, headers=headers)
        pulses = int(((data.get("pulse_info") or {}).get("count")) or 0)
        return {"pulses": pulses, "score_add": min(35, pulses * 5)}
    except Exception as e:
        return {"error": str(e)[:80], "score_add": 0}


def check_shodan(ioc):
    if ioc["type"] != "ip":
        return {"skipped": True, "score_add": 0}
    key = os.environ.get("SHODAN_API_KEY", "").strip()
    if not key:
        return {"skipped": True, "score_add": 0}
    try:
        data = http_get_json(f"https://api.shodan.io/shodan/host/{urllib.parse.quote(ioc['value'])}?key={urllib.parse.quote(key)}")
        vulns = list((data.get("vulns") or {}).keys())
        ports = data.get("ports") or []
        return {"ports": ports[:10], "vulns": vulns[:8], "org": data.get("org"), "score_add": min(30, len(vulns) * 8 + (5 if len(ports) > 5 else 0))}
    except Exception as e:
        return {"error": str(e)[:80], "score_add": 0}


def assign_level(score, ioc):
    if ioc["type"] == "cve":
        return "HIGH", max(score, 65)
    if score >= 70:
        return "CRITICAL", score
    if score >= 40:
        return "HIGH", score
    if score >= 20:
        return "MEDIUM", score
    return "LOW", score


def enrich_iocs(iocs):
    enriched = []
    for ioc in iocs:
        score = 10
        reasons = []
        uh = check_urlhaus(ioc)
        vt = check_virustotal(ioc)
        ab = check_abuseipdb(ioc)
        otx = check_otx(ioc)
        sh = check_shodan(ioc)

        for label, res in [("URLhaus", uh), ("VirusTotal", vt), ("AbuseIPDB", ab), ("OTX", otx), ("Shodan", sh)]:
            add = int(res.get("score_add", 0))
            if add > 0:
                score += add
                reasons.append(f"{label} (+{add})")

        level, final_score = assign_level(score, ioc)
        ioc["level"] = level
        ioc["score"] = final_score
        ioc["reasons"] = reasons if reasons else ["İlkin/standart yoxlama"]
        ioc["checks"] = {
            "urlhaus": uh,
            "virustotal": vt,
            "abuseipdb": ab,
            "otx": otx,
            "shodan": sh,
        }
        enriched.append(ioc)

    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    enriched.sort(key=lambda x: (order.get(x["level"], 9), -x["score"]))
    return enriched


def send_deep_cti_report(updated_at, source_count, news, cves, iocs):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    webapp_url = os.environ.get("WEBAPP_URL", "").strip()
    if not token or not chat_id:
        return

    darkweb_news = [n for n in news if n.get("category") == "darkweb_cti"][:4]
    global_news = [n for n in news if n.get("category") != "darkweb_cti"][:4]
    high_iocs = [x for x in iocs if x["level"] in ("CRITICAL", "HIGH")][:6]

    lines = [
        "🛰️ <b>DEEP CTI REPORT BOT — OPERATİV HESABAT</b>",
        f"🕒 Vaxt: <code>{updated_at}</code>",
        f"📡 Mənbələr: <b>{source_count}</b> | 📰 Xəbər: <b>{len(news)}</b> | 🔍 Dedup IoC: <b>{len(iocs)}</b>",
        "",
        "⚠️ <b>CISA KEV (Kritik İstismar Olunan Zəifliklər):</b>",
    ]
    for c in cves[:4]:
        lines.append(f"• <b>{c['cveID']}</b> — {c['vendor']} {c['product']} ({c['dateAdded']})")

    lines.append("")
    lines.append("🕵️ <b>Darkweb, Leak & Ransomware Radar:</b>")
    for n in darkweb_news:
        lines.append(f"• [{n['source']}] {n['title']}")

    lines.append("")
    lines.append("🌍 <b>Dünya Kiber Təhlükəsizlik Xəbərləri:</b>")
    for n in global_news:
        lines.append(f"• [{n['source']}] {n['title']}")

    if high_iocs:
        lines.append("")
        lines.append("🚨 <b>Yoxlanılmış Yüksək Səviyyəli IoC-lər:</b>")
        for it in high_iocs:
            lines.append(f"• [<b>{it['level']}</b> | {it['score']}] <code>{it['value']}</code> ({it['type']})")

    payload = {
        "chat_id": chat_id,
        "text": "\n".join(lines)[:4000],
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if webapp_url:
        payload["reply_markup"] = json.dumps({
            "inline_keyboard": [[{"text": "📲 SOC & CTI Operativ App-i Aç", "web_app": {"url": webapp_url}}]]
        })

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception:
        pass


def main():
    updated_at = now_az_str()
    unique_web = deduplicate_sources()
    rss_items = fetch_rss_news()
    web_items = fetch_web_sources_items(unique_web)
    news = deduplicate_news(rss_items + web_items)
    cves = fetch_cisa_kev()
    raw_iocs = extract_and_dedup_iocs(news, cves)
    iocs = enrich_iocs(raw_iocs)

    sources = (
        [{"name": n, "url": u, "type": "RSS"} for n, u in RSS_SOURCES]
        + [{"name": n, "url": u, "type": "CTI/Web"} for n, u in unique_web]
        + [
            {"name": "CISA KEV", "url": CISA_KEV_URL, "type": "KEV"},
            {"name": "Shodan API", "url": "https://www.shodan.io", "type": "CTI Check"},
            {"name": "URLhaus API", "url": "https://urlhaus.abuse.ch", "type": "CTI Check"},
            {"name": "VirusTotal API", "url": "https://www.virustotal.com", "type": "CTI Check"},
            {"name": "AbuseIPDB API", "url": "https://www.abuseipdb.com", "type": "CTI Check"},
            {"name": "AlienVault OTX", "url": "https://otx.alienvault.com", "type": "CTI Check"},
        ]
    )

    out_obj = {
        "updated_at": updated_at,
        "sources": sources,
        "news": news,
        "cves": cves,
        "iocs": iocs,
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=2)

    send_deep_cti_report(updated_at, len(sources), news, cves, iocs)


if __name__ == "__main__":
    main()
