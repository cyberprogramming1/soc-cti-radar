import datetime
import html
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

TZ_AZ = datetime.timezone(datetime.timedelta(hours=4))

RSS_SOURCES = [
    ("The Hacker News RSS", "https://feeds.feedburner.com/TheHackersNews"),
    ("The Hacker News Atom", "https://thehackernews.com/feeds/posts/default"),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
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

RAW_WEB_SOURCES = [
    ("MITRE ATT&CK", "https://attack.mitre.org/"),
    ("The Hacker News", "https://thehackernews.com/"),
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
MITRE_ENTERPRISE_STIX_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"

APT_CATALOG = [
    {
        "id": "apt28",
        "name": "APT28 (Fancy Bear / Forest Blizzard)",
        "category": "espionage",
        "keywords": ["apt28", "fancy bear", "forest blizzard", "strontium"],
        "focus": "Dövlət, müdafiə, enerji, mail və sərhəd/VPN sistemləri",
        "default_techniques": ["T1566.001", "T1190", "T1071.001", "T1110"],
        "mitigation": "Edge/mail/VPN yamaları, phishing-resistant MFA, anomal auth/ASN monitorinqi.",
        "scenario": "token_replay",
    },
    {
        "id": "apt29",
        "name": "APT29 (Midnight Blizzard / Nobelium)",
        "category": "espionage",
        "keywords": ["apt29", "midnight blizzard", "nobelium", "cozy bear"],
        "focus": "Cloud/SaaS tenant-lar, diplomatik/dövlət qurumları, OAuth və token sistemləri",
        "default_techniques": ["T1528", "T1550.001", "T1098", "T1567"],
        "mitigation": "Conditional Access, OAuth app consent nəzarəti, refresh token və sessiya reviziyası.",
        "scenario": "api_leak",
    },
    {
        "id": "volt_typhoon",
        "name": "Volt Typhoon",
        "category": "infra",
        "keywords": ["volt typhoon", "vanguard panda", "bronze silhouette"],
        "focus": "Kritik infrastruktur, telekommunikasiya, enerji və sərhəd şəbəkə cihazları",
        "default_techniques": ["T1190", "T1078", "T1021", "T1071"],
        "mitigation": "Edge/VPN/Firewall cihazlarında LOTL və daxili lateral hərəkət ovlanması.",
        "scenario": "c2_lateral",
    },
    {
        "id": "sandworm",
        "name": "Sandworm Team (APT44)",
        "category": "infra",
        "keywords": ["sandworm", "apt44", "seadoggie", "telebots"],
        "focus": "Enerji, ICS/SCADA, kritik infrastruktur və destruktiv/wiper hücumları",
        "default_techniques": ["T1566", "T1486", "T1561", "T1021.002"],
        "mitigation": "OT/IT seqmentasiyası, offline backup, admin share və kütləvi dəyişiklik alertləri.",
        "scenario": "c2_lateral",
    },
    {
        "id": "lazarus",
        "name": "Lazarus Group (Hidden Cobra / TraderTraitor)",
        "category": "finance",
        "keywords": ["lazarus", "hidden cobra", "tradertraitor", "bluenoroff"],
        "focus": "Bankçılıq, kripto/DeFi, IT təchizat zənciri, trojanlaşdırılmış tətbiqlər",
        "default_techniques": ["T1204.002", "T1059.001", "T1105", "T1041"],
        "mitigation": "İmzasız/yeni binary-lərin nəzarəti, developer/kripto mühitlərində kənar yükləmə bloklaması.",
        "scenario": "infostealer",
    },
    {
        "id": "scattered_spider",
        "name": "Scattered Spider (UNC3944 / Octo Tempest)",
        "category": "identity",
        "keywords": ["scattered spider", "unc3944", "octo tempest", "0ktapus", "vishing"],
        "focus": "Helpdesk/IT sosial mühəndislik, vishing, SSO/Okta/Entra ID və bulud hesabları",
        "default_techniques": ["T1566.004", "T1539", "T1078.004", "T1550.004"],
        "mitigation": "MFA reset prosedurlarında əlavə yoxlama, sessiya ləğvi və stealer/cookie ovlanması.",
        "scenario": "token_replay",
    },
    {
        "id": "kimsuky",
        "name": "Kimsuky (Velvet Chollima)",
        "category": "espionage",
        "keywords": ["kimsuky", "velvet chollima", "black banshee", "emerald whitetail"],
        "focus": "Analitik mərkəzlər, akademiya, diplomatik və xarici siyasət/müdafiə sektoru",
        "default_techniques": ["T1566.001", "T1555.003", "T1059.001", "T1567"],
        "mitigation": "Spear-phishing və brauzer credential/cookie oğurluğuna qarşı EDR/mail qaydaları.",
        "scenario": "infostealer",
    },
    {
        "id": "apt41",
        "name": "APT41 (Winnti / Brass Typhoon)",
        "category": "finance",
        "keywords": ["apt41", "winnti", "brass typhoon", "wicked panda"],
        "focus": "Təchizat zənciri, səhiyyə, telekom, oyun və maliyyə/kiber-casusluq",
        "default_techniques": ["T1190", "T1195", "T1059", "T1071.001"],
        "mitigation": "Web/app zəifliklərinin sürətli yamalanması, xidmət hesabları və çıxış trafikinin izlənməsi.",
        "scenario": "rce_web",
    },
]

FALLBACK_MITRE_TECHNIQUES = {
    "T1021": {"id": "T1021", "name": "Remote Services", "tactic": "Lateral Movement"},
    "T1021.002": {"id": "T1021.002", "name": "SMB/Windows Admin Shares", "tactic": "Lateral Movement"},
    "T1041": {"id": "T1041", "name": "Exfiltration Over C2 Channel", "tactic": "Exfiltration"},
    "T1059": {"id": "T1059", "name": "Command and Scripting Interpreter", "tactic": "Execution"},
    "T1059.001": {"id": "T1059.001", "name": "PowerShell", "tactic": "Execution"},
    "T1071": {"id": "T1071", "name": "Application Layer Protocol", "tactic": "Command and Control"},
    "T1071.001": {"id": "T1071.001", "name": "Web Protocols", "tactic": "Command and Control"},
    "T1078": {"id": "T1078", "name": "Valid Accounts", "tactic": "Defense Evasion / Persistence"},
    "T1078.004": {"id": "T1078.004", "name": "Cloud Accounts", "tactic": "Persistence"},
    "T1098": {"id": "T1098", "name": "Account Manipulation", "tactic": "Persistence"},
    "T1105": {"id": "T1105", "name": "Ingress Tool Transfer", "tactic": "Command and Control"},
    "T1110": {"id": "T1110", "name": "Brute Force", "tactic": "Credential Access"},
    "T1190": {"id": "T1190", "name": "Exploit Public-Facing Application", "tactic": "Initial Access"},
    "T1195": {"id": "T1195", "name": "Supply Chain Compromise", "tactic": "Initial Access"},
    "T1204.002": {"id": "T1204.002", "name": "Malicious File", "tactic": "Execution"},
    "T1486": {"id": "T1486", "name": "Data Encrypted for Impact", "tactic": "Impact"},
    "T1528": {"id": "T1528", "name": "Steal Application Access Token", "tactic": "Credential Access"},
    "T1539": {"id": "T1539", "name": "Steal Web Session Cookie", "tactic": "Credential Access"},
    "T1550.001": {"id": "T1550.001", "name": "Application Access Token", "tactic": "Defense Evasion"},
    "T1550.004": {"id": "T1550.004", "name": "Web Session Cookie", "tactic": "Defense Evasion"},
    "T1555.003": {"id": "T1555.003", "name": "Credentials from Web Browsers", "tactic": "Credential Access"},
    "T1561": {"id": "T1561", "name": "Disk Wipe", "tactic": "Impact"},
    "T1566": {"id": "T1566", "name": "Phishing", "tactic": "Initial Access"},
    "T1566.001": {"id": "T1566.001", "name": "Spearphishing Attachment", "tactic": "Initial Access"},
    "T1566.004": {"id": "T1566.004", "name": "Spearphishing Voice", "tactic": "Initial Access"},
    "T1567": {"id": "T1567", "name": "Exfiltration Over Web Service", "tactic": "Exfiltration"},
}

IP_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b")
URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)
HASH_RE = re.compile(r"\b(?:[a-fA-F0-9]{64}|[a-fA-F0-9]{40}|[a-fA-F0-9]{32})\b")
CVE_RE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)
TECH_RE = re.compile(r"\bT\d{4}(?:\.\d{3})?\b")
DOMAIN_RE = re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+(?:ru|su|cn|tk|xyz|top|cc|pw|io|com|net|org|info|live|dev)\b", re.IGNORECASE)

DARKWEB_KEYWORDS = (
    "leak", "breach", "ransomware", "darkweb", "dark web", "stealer",
    "extortion", "vishing", "database", "dump", "forum", "onion", "payload",
    "malware", "zero-day", "0-day", "credential", "threat actor", "wiper", "botnet"
)

_TRANSLATION_CACHE = {}


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


def http_get_text(url, headers=None, timeout=10):
    req = urllib.request.Request(
        url,
        headers=headers or {
            "User-Agent": "Mozilla/5.0 (compatible; SOC-CTI-Radar/3.5; +https://github.com)"
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def http_get_json(url, headers=None, timeout=12):
    return json.loads(http_get_text(url, headers=headers, timeout=timeout))


def http_post_form(url, data_dict, headers=None, timeout=10):
    encoded = urllib.parse.urlencode(data_dict).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=encoded,
        headers=headers or {"User-Agent": "SOC-CTI-Radar/3.5"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="ignore"))


def clean_html(text):
    text = html.unescape(text or "")
    text = re.sub(r"<script.*?>.*?</script>|<style.*?>.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def translate_to_az(text):
    src = (text or "").strip()
    if not src:
        return ""
    if src in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[src]

    chunk = src[:450]

    try:
        q = urllib.parse.urlencode({
            "client": "gtx",
            "sl": "auto",
            "tl": "az",
            "dt": "t",
            "q": chunk,
        })
        parsed = http_get_json(f"https://translate.googleapis.com/translate_a/single?{q}", timeout=7)
        translated = "".join(seg[0] for seg in (parsed[0] or []) if seg and seg[0]).strip()
        if translated:
            _TRANSLATION_CACHE[src] = translated
            return translated
    except Exception:
        pass

    try:
        q2 = urllib.parse.urlencode({"q": chunk[:400], "langpair": "en|az"})
        mm = http_get_json(f"https://api.mymemory.translated.net/get?{q2}", timeout=8)
        mm_text = html.unescape(((mm.get("responseData") or {}).get("translatedText") or "")).strip()
        if mm_text and "MYMEMORY WARNING" not in mm_text.upper():
            _TRANSLATION_CACHE[src] = mm_text
            return mm_text
    except Exception:
        pass

    _TRANSLATION_CACHE[src] = src
    return src


def classify_category(source_name, title, summary, url):
    blob = f"{source_name} {title} {summary} {url}".lower()
    if any(k in blob for k in DARKWEB_KEYWORDS) or any(
        d in url.lower() for d in (
            "leakfa", "darkforums", "patched.to", "ransomware.live",
            "dailydarkweb", "darknetlist", "blackbones", "secretline",
            "bf.st", "tria.ge", "mwdb.cert.pl", "kalir.io", "leakfarsi", "dread", "tenebris"
        )
    ):
        return "darkweb_cti"
    return "global_cyber"


def load_mitre_techniques():
    techniques = dict(FALLBACK_MITRE_TECHNIQUES)
    try:
        stix = http_get_json(MITRE_ENTERPRISE_STIX_URL, timeout=14)
        for obj in stix.get("objects") or []:
            if obj.get("type") != "attack-pattern" or obj.get("revoked") or obj.get("x_mitre_deprecated"):
                continue
            ext_id = None
            for ref in obj.get("external_references") or []:
                if ref.get("source_name") == "mitre-attack" and ref.get("external_id"):
                    ext_id = ref["external_id"].strip()
                    break
            if not ext_id or not re.match(r"^T\d{4}(?:\.\d{3})?$", ext_id):
                continue
            phases = [
                (p.get("phase_name") or "").replace("-", " ").title()
                for p in (obj.get("kill_chain_phases") or [])
                if p.get("phase_name")
            ]
            techniques[ext_id] = {
                "id": ext_id,
                "name": obj.get("name") or ext_id,
                "tactic": ", ".join(phases) if phases else "Enterprise ATT&CK",
                "url": f"https://attack.mitre.org/techniques/{ext_id.replace('.', '/')}/",
            }
    except Exception:
        pass

    for tid, info in techniques.items():
        if "url" not in info:
            info["url"] = f"https://attack.mitre.org/techniques/{tid.replace('.', '/')}/"
    return techniques


def fetch_rss_news():
    items = []
    for name, url in RSS_SOURCES:
        try:
            xml_data = http_get_text(url, timeout=9)
            root = ET.fromstring(xml_data)
            entries = root.findall(".//item")
            if not entries:
                entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
            for elem in entries[:4]:
                title_el = elem.find("title")
                if title_el is None:
                    title_el = elem.find("{http://www.w3.org/2005/Atom}title")
                title = clean_html(title_el.text if title_el is not None else "")

                link = (elem.findtext("link") or "").strip()
                if not link:
                    link_el = elem.find("{http://www.w3.org/2005/Atom}link")
                    if link_el is not None:
                        link = (link_el.attrib.get("href") or "").strip()
                link = link or url

                desc = clean_html(
                    elem.findtext("description")
                    or elem.findtext("{http://www.w3.org/2005/Atom}summary")
                    or ""
                )[:240]
                pub_date = (
                    elem.findtext("pubDate")
                    or elem.findtext("{http://www.w3.org/2005/Atom}updated")
                    or ""
                )[:16]
                if title:
                    items.append({
                        "source": name,
                        "category": classify_category(name, title, desc, link),
                        "title": title,
                        "title_az": translate_to_az(title),
                        "summary": desc,
                        "summary_az": translate_to_az(desc),
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
            t = f"{name} — Tor/Onion mənbə qeydi"
            s = "Onion ünvanı Tor şəbəkəsi tələb edir; birbaşa HTTP runner-də qeydə alınıb."
            items.append({
                "source": name,
                "category": "darkweb_cti",
                "title": t,
                "title_az": t,
                "summary": s,
                "summary_az": s,
                "url": url,
                "date": now_az_str()[:10],
            })
            continue

        try:
            raw = http_get_text(url, timeout=7)
            title_m = re.search(r"<title[^>]*>(.*?)</title>", raw, flags=re.S | re.I)
            page_title = (clean_html(title_m.group(1)) if title_m else name)[:130] or name
            text_body = clean_html(raw)
            snippet = text_body[:220] if text_body else f"{name} mənbəsindən məlumat toplandı."
            cat = classify_category(name, page_title, snippet, url)
            items.append({
                "source": name,
                "category": cat,
                "title": page_title,
                "title_az": translate_to_az(page_title),
                "summary": snippet,
                "summary_az": snippet,
                "url": url,
                "date": now_az_str()[:10],
            })
        except Exception as e:
            t = f"{name} (mənbə qeydi)"
            s = f"Mənbə qeydə alındı ({str(e)[:70]})."
            items.append({
                "source": name,
                "category": classify_category(name, name, "", url),
                "title": t,
                "title_az": t,
                "summary": s,
                "summary_az": s,
                "url": url,
                "date": now_az_str()[:10],
            })
    return items


def deduplicate_news(items):
    seen = set()
    out = []
    for it in items:
        key = f"{(it.get('url') or '').strip().lower()}|{(it.get('title') or '').strip().lower()[:85]}"
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def fetch_cisa_kev():
    try:
        data = http_get_json(CISA_KEV_URL, timeout=12)
        vulns = data.get("vulnerabilities") or []
        vulns_sorted = sorted(vulns, key=lambda x: x.get("dateAdded", ""), reverse=True)
        out = []
        for v in vulns_sorted[:15]:
            name = v.get("vulnerabilityName", "")
            action = v.get("requiredAction", "")
            out.append({
                "cveID": v.get("cveID", ""),
                "vendor": v.get("vendorProject", ""),
                "product": v.get("product", ""),
                "name": name,
                "name_az": translate_to_az(name),
                "dateAdded": v.get("dateAdded", ""),
                "ransomware": v.get("knownRansomwareCampaignUse", ""),
                "action": action,
                "action_az": translate_to_az(action),
            })
        return out
    except Exception:
        return []


def detect_active_apts(news, cves, mitre_techniques):
    corpus_entries = []
    for n in news:
        corpus_entries.append({
            "text": f"{n.get('source', '')} {n.get('title', '')} {n.get('summary', '')}".lower(),
            "title": n.get("title_az") or n.get("title") or "",
            "source": n.get("source") or "",
            "url": n.get("url") or "",
        })
    for c in cves:
        corpus_entries.append({
            "text": f"{c.get('cveID', '')} {c.get('vendor', '')} {c.get('product', '')} {c.get('name', '')} {c.get('action', '')}".lower(),
            "title": f"{c.get('cveID', '')}: {c.get('name_az') or c.get('name') or ''}",
            "source": "CISA KEV",
            "url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        })

    active_list = []
    for grp in APT_CATALOG:
        matched_mentions = []
        found_techs = set(grp["default_techniques"])

        for entry in corpus_entries:
            txt = entry["text"]
            if any(kw in txt for kw in grp["keywords"]):
                matched_mentions.append({
                    "source": entry["source"],
                    "title": entry["title"][:120],
                    "url": entry["url"],
                })
                for tid in TECH_RE.findall(txt.upper()):
                    if tid in mitre_techniques:
                        found_techs.add(tid)

        context_hits = 0
        for entry in corpus_entries:
            txt = entry["text"]
            if grp["category"] == "identity" and any(w in txt for w in ("vishing", "session", "mfa", "token", "okta", "entra")):
                context_hits += 1
            elif grp["category"] == "infra" and any(w in txt for w in ("infrastructure", "router", "firewall", "vpn", "scada", "critical")):
                context_hits += 1
            elif grp["category"] == "finance" and any(w in txt for w in ("ransomware", "extortion", "stealer", "bank", "crypto")):
                context_hits += 1
            elif grp["category"] == "espionage" and any(w in txt for w in ("zero-day", "0-day", "cve-", "breach", "espionage")):
                context_hits += 1

        mention_count = len(matched_mentions)
        is_explicitly_seen = mention_count > 0
        activity_score = min(99, 58 + mention_count * 12 + min(22, context_hits * 2))
        level = "CRITICAL" if is_explicitly_seen else "HIGH"

        tech_details = []
        for tid in sorted(found_techs):
            tinfo = mitre_techniques.get(tid) or {
                "id": tid,
                "name": tid,
                "tactic": "Enterprise ATT&CK",
                "url": f"https://attack.mitre.org/techniques/{tid.replace('.', '/')}/",
            }
            tech_details.append({
                "id": tid,
                "name": tinfo.get("name", tid),
                "tactic": tinfo.get("tactic", "Enterprise ATT&CK"),
                "url": tinfo.get("url", f"https://attack.mitre.org/techniques/{tid.replace('.', '/')}/"),
            })

        active_list.append({
            "id": grp["id"],
            "name": grp["name"],
            "category": grp["category"],
            "level": level,
            "activity_score": activity_score,
            "status_label": f"Mənbələrdə aşkarlandı ({mention_count})" if is_explicitly_seen else "Aktiv sektor radarı",
            "focus": grp["focus"],
            "mitigation": grp["mitigation"],
            "scenario": grp["scenario"],
            "techniques": tech_details,
            "mentions": matched_mentions[:4],
        })

    active_list.sort(key=lambda x: (-x["activity_score"], x["name"]))
    return active_list


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
        "pulse.kalir.io", "tria.ge", "mwdb.cert.pl", "flakkaonline.com", "attack.mitre.org",
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
            "verdict": "İlkin qeyd",
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
    headers = {"User-Agent": "SOC-CTI-Radar/3.5"}
    if auth:
        headers["Auth-Key"] = auth
    try:
        if ioc["type"] == "url":
            res = http_post_form("https://urlhaus-api.abuse.ch/v1/url/", {"url": ioc["value"]}, headers=headers)
            if res.get("query_status") == "ok":
                return {"hit": True, "threat": res.get("threat") or "listed_url", "score_add": 45, "summary": f"URLhaus: aktiv təhdid ({res.get('threat') or 'URL'})"}
        elif ioc["type"] == "domain":
            host = ioc["value"].split("/")[0]
            res = http_post_form("https://urlhaus-api.abuse.ch/v1/host/", {"host": host}, headers=headers)
            if res.get("query_status") == "ok" and (res.get("urls") or []):
                cnt = len(res.get("urls", []))
                return {"hit": True, "threat": f"urls:{cnt}", "score_add": 40, "summary": f"URLhaus: {cnt} zərərli URL qeydi"}
        elif ioc["type"] == "hash":
            algo = "sha256_hash" if len(ioc["value"]) == 64 else "md5_hash"
            res = http_post_form("https://urlhaus-api.abuse.ch/v1/payload/", {algo: ioc["value"]}, headers=headers)
            if res.get("query_status") == "ok":
                sig = res.get("signature") or "malware_payload"
                return {"hit": True, "threat": sig, "score_add": 50, "summary": f"URLhaus: zərərli fayl ({sig})"}
    except Exception as e:
        return {"hit": False, "error": str(e)[:80], "score_add": 0, "summary": "URLhaus: sorğu xətası"}
    return {"hit": False, "score_add": 0, "summary": "URLhaus: təmiz"}


def check_virustotal(ioc):
    key = os.environ.get("VT_API_KEY", "").strip()
    if not key:
        return {"skipped": True, "score_add": 0, "summary": "VT: API açarı yoxdur"}
    headers = {"x-apikey": key, "User-Agent": "SOC-CTI-Radar/3.5"}
    try:
        if ioc["type"] == "ip":
            ep = f"https://www.virustotal.com/api/v3/ip_addresses/{urllib.parse.quote(ioc['value'])}"
        elif ioc["type"] == "domain":
            ep = f"https://www.virustotal.com/api/v3/domains/{urllib.parse.quote(ioc['value'])}"
        elif ioc["type"] == "hash":
            ep = f"https://www.virustotal.com/api/v3/files/{urllib.parse.quote(ioc['value'])}"
        else:
            return {"skipped": True, "score_add": 0, "summary": "VT: tətbiq olunmur"}

        data = http_get_json(ep, headers=headers)
        stats = (((data.get("data") or {}).get("attributes") or {}).get("last_analysis_stats")) or {}
        mal = int(stats.get("malicious", 0))
        susp = int(stats.get("suspicious", 0))
        return {"malicious": mal, "suspicious": susp, "score_add": min(60, mal * 10 + susp * 4), "summary": f"VT: {mal} malicious / {susp} suspicious"}
    except Exception as e:
        return {"error": str(e)[:80], "score_add": 0, "summary": "VT: sorğu xətası"}


def check_abuseipdb(ioc):
    if ioc["type"] != "ip":
        return {"skipped": True, "score_add": 0, "summary": "AbuseIPDB: yalnız IP"}
    key = os.environ.get("ABUSEIPDB_API_KEY", "").strip()
    if not key:
        return {"skipped": True, "score_add": 0, "summary": "AbuseIPDB: API açarı yoxdur"}
    try:
        q = urllib.parse.urlencode({"ipAddress": ioc["value"], "maxAgeInDays": "30"})
        data = http_get_json(
            f"https://api.abuseipdb.com/api/v2/check?{q}",
            headers={"Key": key, "Accept": "application/json", "User-Agent": "SOC-CTI-Radar/3.5"},
        )
        d = data.get("data") or {}
        conf = int(d.get("abuseConfidenceScore", 0))
        rep = int(d.get("totalReports", 0))
        return {"confidence": conf, "reports": rep, "score_add": int(conf * 0.5), "summary": f"AbuseIPDB: {conf}% etibar ({rep} hesabat)"}
    except Exception as e:
        return {"error": str(e)[:80], "score_add": 0, "summary": "AbuseIPDB: sorğu xətası"}


def check_otx(ioc):
    key = os.environ.get("OTX_API_KEY", "").strip()
    headers = {"User-Agent": "SOC-CTI-Radar/3.5"}
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
            return {"skipped": True, "score_add": 0, "summary": "OTX: tətbiq olunmur"}

        data = http_get_json(ep, headers=headers)
        pulses = int(((data.get("pulse_info") or {}).get("count")) or 0)
        return {"pulses": pulses, "score_add": min(35, pulses * 5), "summary": f"OTX: {pulses} pulse"}
    except Exception as e:
        return {"error": str(e)[:80], "score_add": 0, "summary": "OTX: sorğu xətası"}


def check_shodan(ioc):
    if ioc["type"] != "ip":
        return {"skipped": True, "score_add": 0, "summary": "Shodan: yalnız IP"}
    key = os.environ.get("SHODAN_API_KEY", "").strip()
    if not key:
        return {"skipped": True, "score_add": 0, "summary": "Shodan: API açarı yoxdur"}
    try:
        data = http_get_json(f"https://api.shodan.io/shodan/host/{urllib.parse.quote(ioc['value'])}?key={urllib.parse.quote(key)}")
        vulns = list((data.get("vulns") or {}).keys())
        ports = data.get("ports") or []
        return {
            "ports": ports[:10],
            "vulns": vulns[:8],
            "org": data.get("org"),
            "score_add": min(30, len(vulns) * 8 + (5 if len(ports) > 5 else 0)),
            "summary": f"Shodan: {len(ports)} port, {len(vulns)} CVE",
        }
    except Exception as e:
        return {"error": str(e)[:80], "score_add": 0, "summary": "Shodan: sorğu xətası"}


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
        tool_notes = []

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
            if not res.get("skipped") and res.get("summary"):
                tool_notes.append(res["summary"])

        level, final_score = assign_level(score, ioc)
        if ioc["type"] == "cve":
            verdict = "Aktiv istismar kataloqunda qeyd olunan zəiflik — dərhal yama/hunting tələb edir."
        elif level == "CRITICAL":
            verdict = "Kritik zərərli indikator — bloklama və dərhal SOC/SOAR müdaxiləsi tövsiyə olunur."
        elif level == "HIGH":
            verdict = "Yüksək riskli indikator — loglarda ovlama və sessiya/host yoxlaması aparın."
        elif level == "MEDIUM":
            verdict = "Orta riskli indikator — əlavə kontekst və perimetr/DNS izi yoxlanmalıdır."
        else:
            verdict = "Aşağı/ilkin risk — aktiv zərərli siqnal qeydə alınmayıb, müşahidədə saxlayın."

        ioc["level"] = level
        ioc["score"] = final_score
        ioc["reasons"] = reasons if reasons else ["Açıq/API yoxlamada əlavə risk balı yoxdur"]
        ioc["verdict"] = verdict
        ioc["tool_summary"] = " • ".join(tool_notes) if tool_notes else "Avtomatik alət yoxlaması tamamlandı"
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


def send_deep_cti_report(updated_at, source_count, news, cves, iocs, active_apts):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    webapp_url = os.environ.get("WEBAPP_URL", "").strip()
    if not token or not chat_id:
        return

    darkweb_news = [n for n in news if n.get("category") == "darkweb_cti"][:3]
    global_news = [n for n in news if n.get("category") != "darkweb_cti"][:3]
    high_iocs = [x for x in iocs if x["level"] in ("CRITICAL", "HIGH")][:4]
    top_apts = active_apts[:4]

    lines = [
        "🛰️ <b>DEEP CTI REPORT BOT — OPERATİV HESABAT (AZ)</b>",
        f"🕒 Vaxt: <code>{updated_at}</code>",
        f"📡 Mənbə: <b>{source_count}</b> | 📰 Xəbər: <b>{len(news)}</b> | 🔍 IoC: <b>{len(iocs)}</b> | 🕵️ APT: <b>{len(active_apts)}</b>",
        "",
        "🕵️ <b>Aktiv APT Radar (MITRE ATT&CK):</b>",
    ]
    for a in top_apts:
        t_codes = ", ".join(t["id"] for t in (a.get("techniques") or [])[:4])
        lines.append(f"• <b>{a['name']}</b> [{t_codes}] — {a['status_label']}")

    lines.append("")
    lines.append("⚠️ <b>CISA KEV:</b>")
    for c in cves[:3]:
        lines.append(f"• <b>{c['cveID']}</b> — {c['vendor']} {c['product']} ({c['dateAdded']})")

    lines.append("")
    lines.append("🕵️ <b>Darkweb & Leak:</b>")
    for n in darkweb_news:
        lines.append(f"• [{n['source']}] {n.get('title_az') or n.get('title')}")

    lines.append("")
    lines.append("🌍 <b>Dünya Kiber Xəbərləri:</b>")
    for n in global_news:
        lines.append(f"• [{n['source']}] {n.get('title_az') or n.get('title')}")

    if high_iocs:
        lines.append("")
        lines.append("🚨 <b>Yüksək Səviyyəli IoC-lər (Avtomatik Analiz):</b>")
        for it in high_iocs:
            lines.append(f"• [<b>{it['level']}</b> | {it['score']}] <code>{it['value']}</code> — {it.get('verdict', '')[:70]}")

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
    mitre_techniques = load_mitre_techniques()
    rss_items = fetch_rss_news()
    web_items = fetch_web_sources_items(unique_web)
    news = deduplicate_news(rss_items + web_items)
    cves = fetch_cisa_kev()
    active_apts = detect_active_apts(news, cves, mitre_techniques)
    raw_iocs = extract_and_dedup_iocs(news, cves)
    iocs = enrich_iocs(raw_iocs)

    sources = (
        [{"name": n, "url": u, "type": "RSS"} for n, u in RSS_SOURCES]
        + [{"name": n, "url": u, "type": "CTI/Web"} for n, u in unique_web]
        + [
            {"name": "CISA KEV", "url": CISA_KEV_URL, "type": "KEV"},
            {"name": "MITRE ATT&CK STIX", "url": "https://attack.mitre.org/", "type": "ATT&CK"},
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
        "active_apts": active_apts,
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=2)

    send_deep_cti_report(updated_at, len(sources), news, cves, iocs, active_apts)


if __name__ == "__main__":
    main()
