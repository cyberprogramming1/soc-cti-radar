import datetime
import html
import json
import os
import re
import socket
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
    ("Onion - OP7YIEK (Tor)", "http://op7yiekgumt7po6mjgii4uewrwjydx5vhpa6y5gv7glftmw5srbwnaid.onion/"),
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
    ("Onion - Tenebris (Tor)", "http://tenebrispoyfrcup4k24lciwrh4gc5735hmld4dweq7his7zh423opqd.onion/"),
    ("Onion - Dread #1 (Tor)", "https://dreadytofatroptsdj6io7l3xptbet6onoyno2yv7jicoxknyazubrad.onion/"),
    ("Onion - Dread #2 (Tor)", "https://dreadytognbh7m5nlmqsogzzlxjy75iuxkulewbhxcorupbqahact2yd.onion/"),
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
        "focus": "Government, defense, energy, mail & edge/VPN infrastructure",
        "default_techniques": ["T1566.001", "T1190", "T1071.001", "T1110"],
        "mitigation": "Patch edge/mail/VPN appliances, enforce phishing-resistant MFA, monitor anomalous auth/ASN.",
        "scenario": "token_replay",
    },
    {
        "id": "apt29",
        "name": "APT29 (Midnight Blizzard / Nobelium)",
        "category": "espionage",
        "keywords": ["apt29", "midnight blizzard", "nobelium", "cozy bear"],
        "focus": "Cloud/SaaS tenants, diplomatic/government orgs, OAuth & token systems",
        "default_techniques": ["T1528", "T1550.001", "T1098", "T1567"],
        "mitigation": "Conditional Access, OAuth consent governance, refresh token & session revocation.",
        "scenario": "api_leak",
    },
    {
        "id": "volt_typhoon",
        "name": "Volt Typhoon",
        "category": "infra",
        "keywords": ["volt typhoon", "vanguard panda", "bronze silhouette"],
        "focus": "Critical infrastructure, telecom, energy & perimeter network gear",
        "default_techniques": ["T1190", "T1078", "T1021", "T1071"],
        "mitigation": "Hunt LOTL activity on edge/VPN/firewall devices and lateral movement.",
        "scenario": "c2_lateral",
    },
    {
        "id": "sandworm",
        "name": "Sandworm Team (APT44)",
        "category": "infra",
        "keywords": ["sandworm", "apt44", "seadoggie", "telebots"],
        "focus": "Energy, ICS/SCADA, critical infrastructure & destructive/wiper ops",
        "default_techniques": ["T1566", "T1486", "T1561", "T1021.002"],
        "mitigation": "IT/OT segmentation, immutable offline backups, admin share & mass change alerts.",
        "scenario": "c2_lateral",
    },
    {
        "id": "lazarus",
        "name": "Lazarus Group (Hidden Cobra / TraderTraitor)",
        "category": "finance",
        "keywords": ["lazarus", "hidden cobra", "tradertraitor", "bluenoroff"],
        "focus": "Banking, crypto/DeFi, software supply chain & trojanized apps",
        "default_techniques": ["T1204.002", "T1059.001", "T1105", "T1041"],
        "mitigation": "Control unsigned/new binaries, restrict untrusted downloads in dev/crypto environments.",
        "scenario": "infostealer",
    },
    {
        "id": "scattered_spider",
        "name": "Scattered Spider (UNC3944 / Octo Tempest)",
        "category": "identity",
        "keywords": ["scattered spider", "unc3944", "octo tempest", "0ktapus"],
        "focus": "Helpdesk/IT social engineering, vishing, SSO/Okta/Entra ID & cloud accounts",
        "default_techniques": ["T1566.004", "T1539", "T1078.004", "T1550.004"],
        "mitigation": "Strict verification on MFA resets, session revocation & stealer/cookie hunting.",
        "scenario": "token_replay",
    },
    {
        "id": "kimsuky",
        "name": "Kimsuky (Velvet Chollima)",
        "category": "espionage",
        "keywords": ["kimsuky", "velvet chollima", "black banshee", "emerald whitetail"],
        "focus": "Think tanks, academia, diplomatic & foreign policy/defense targets",
        "default_techniques": ["T1566.001", "T1555.003", "T1059.001", "T1567"],
        "mitigation": "Spear-phishing filtering & browser credential/cookie theft detection.",
        "scenario": "infostealer",
    },
    {
        "id": "apt41",
        "name": "APT41 (Winnti / Brass Typhoon)",
        "category": "finance",
        "keywords": ["apt41", "winnti", "brass typhoon", "wicked panda"],
        "focus": "Supply chain, healthcare, telecom, gaming & cyber-espionage/financial ops",
        "default_techniques": ["T1190", "T1195", "T1059", "T1071.001"],
        "mitigation": "Rapid patching of public web apps, service account hardening & egress monitoring.",
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

COUNTRY_PATTERNS = {
    "United States": r"\b(?:united states|usa|u\.s\.|america|american)\b",
    "Israel": r"\b(?:israel|israeli)\b",
    "Ukraine": r"\b(?:ukraine|ukrainian)\b",
    "Russia": r"\b(?:russia|russian)\b",
    "United Kingdom": r"\b(?:united kingdom|uk|britain|british)\b",
    "Germany": r"\b(?:germany|german)\b",
    "France": r"\b(?:france|french)\b",
    "Poland": r"\b(?:poland|polish)\b",
    "Canada": r"\b(?:canada|canadian)\b",
    "India": r"\b(?:india|indian)\b",
    "Japan": r"\b(?:japan|japanese)\b",
    "South Korea": r"\b(?:south korea|korean)\b",
    "Brazil": r"\b(?:brazil|brazilian)\b",
    "Australia": r"\b(?:australia|australian)\b",
    "Azerbaijan": r"\b(?:azerbaijan|baku|azal)\b",
    "Turkey": r"\b(?:turkey|turkish|türkiye)\b",
    "Iran": r"\b(?:iran|iranian)\b",
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


def tor_socks_available(host="127.0.0.1", port=9050, timeout=1.5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def fetch_via_tor_socks5(url, host="127.0.0.1", port=9050, timeout=18):
    parsed = urllib.parse.urlparse(url)
    target_host = parsed.hostname
    target_port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path_and_q = parsed.path or "/"
    if parsed.query:
        path_and_q += "?" + parsed.query

    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        # SOCKS5 handshake (no auth)
        sock.sendall(b"\x05\x01\x00")
        resp = sock.recv(2)
        if len(resp) < 2 or resp[0] != 0x05 or resp[1] != 0x00:
            raise RuntimeError("SOCKS5 auth handshake failed")

        # SOCKS5 connect with domain name (0x03)
        host_bytes = target_host.encode("utf-8")
        req = b"\x05\x01\x00\x03" + bytes([len(host_bytes)]) + host_bytes + target_port.to_bytes(2, "big")
        sock.sendall(req)
        rep = sock.recv(10)
        if len(rep) < 2 or rep[1] != 0x00:
            raise RuntimeError("SOCKS5 connect to onion failed")

        http_req = (
            f"GET {path_and_q} HTTP/1.1\r\n"
            f"Host: {target_host}\r\n"
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0\r\n"
            "Connection: close\r\n\r\n"
        ).encode("utf-8")
        sock.sendall(http_req)

        chunks = []
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)
        raw = b"".join(chunks).decode("utf-8", errors="ignore")
        if "\r\n\r\n" in raw:
            raw = raw.split("\r\n\r\n", 1)[1]
        return raw


def http_get_text(url, headers=None, timeout=10):
    if ".onion" in url.lower():
        if tor_socks_available():
            return fetch_via_tor_socks5(url)
        raise RuntimeError("Tor SOCKS5 (127.0.0.1:9050) not active")

    req = urllib.request.Request(
        url,
        headers=headers or {
            "User-Agent": "Mozilla/5.0 (compatible; SOC-CTI-Radar/4.0; +https://github.com)"
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
        headers=headers or {"User-Agent": "SOC-CTI-Radar/4.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="ignore"))


def clean_html(text):
    text = html.unescape(text or "")
    text = re.sub(r"<script.*?>.*?</script>|<style.*?>.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_impact_summary(title, summary, category):
    blob = f"{title} {summary}".lower()
    if any(w in blob for w in ("ransomware", "wiper", "extortion", "lockbit", "blackcat")):
        return "High operational & business impact: potential encryption/downtime or data extortion — check backups, EDR isolation & lateral paths."
    if any(w in blob for w in ("zero-day", "0-day", "rce", "critical", "exploit", "cve-")):
        return "High exposure risk: active exploitation/vulnerability signal — verify affected assets, apply patches & hunt suspicious child processes."
    if any(w in blob for w in ("breach", "leak", "database", "dump", "credential", "stealer", "cookie", "token")):
        return "Identity & data exposure impact: leaked credentials/tokens/data — audit exposed accounts, reset secrets & revoke active sessions."
    if category == "darkweb_cti":
        return "Threat actor / underground intel signal: monitor for targeted extortion, leak mentions or related infrastructure."
    return "General cyber threat intel: review relevance to perimeter, cloud/identity controls and active detection rules."


def extract_countries(text):
    t = (text or "").lower()
    found = []
    for country, pat in COUNTRY_PATTERNS.items():
        if re.search(pat, t):
            found.append(country)
    return found


def classify_category(source_name, title, summary, url):
    blob = f"{source_name} {title} {summary} {url}".lower()
    if ".onion" in url.lower() or any(k in blob for k in DARKWEB_KEYWORDS) or any(
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
                    cat = classify_category(name, title, desc, link)
                    items.append({
                        "source": name,
                        "category": cat,
                        "title": title,
                        "summary": desc,
                        "impact": build_impact_summary(title, desc, cat),
                        "countries": extract_countries(f"{title} {desc}"),
                        "url": link,
                        "date": pub_date,
                    })
        except Exception:
            continue
    return items


def fetch_web_sources_items(web_sources):
    items = []
    for name, url in web_sources:
        try:
            raw = http_get_text(url, timeout=8 if ".onion" not in url.lower() else 18)
            title_m = re.search(r"<title[^>]*>(.*?)</title>", raw, flags=re.S | re.I)
            page_title = (clean_html(title_m.group(1)) if title_m else name)[:130] or name
            text_body = clean_html(raw)
            snippet = text_body[:220] if text_body else f"Fetched data from {name}."
            cat = classify_category(name, page_title, snippet, url)
            items.append({
                "source": name,
                "category": cat,
                "title": page_title,
                "summary": snippet,
                "impact": build_impact_summary(page_title, snippet, cat),
                "countries": extract_countries(f"{page_title} {snippet}"),
                "url": url,
                "date": now_az_str()[:10],
            })
        except Exception as e:
            err_msg = str(e)[:80]
            cat = classify_category(name, name, "", url)
            note = (
                f"Tor SOCKS5 not active/reachable ({err_msg})."
                if ".onion" in url.lower()
                else f"Source reachability note ({err_msg})."
            )
            items.append({
                "source": name,
                "category": cat,
                "title": f"{name} — {note}",
                "summary": note,
                "impact": build_impact_summary(name, note, cat),
                "countries": extract_countries(name),
                "url": url,
                "date": now_az_str()[:10],
            })
    return items


def deduplicate_news(items):
    seen = set()
    out = []
    for it in items:
        norm_title = re.sub(r"\W+", " ", (it.get("title") or "").strip().lower()).strip()[:90]
        norm_url = (it.get("url") or "").strip().rstrip("/").lower()
        key = f"{norm_url}|{norm_title}"
        if key in seen or not norm_title:
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
                "dateAdded": v.get("dateAdded", ""),
                "ransomware": v.get("knownRansomwareCampaignUse", ""),
                "action": action,
                "impact": build_impact_summary(name, action, "global_cyber"),
            })
        return out
    except Exception:
        return []


def extract_live_ransomware(news_items, cves):
    # Canlı ransomware.live API və xəbərlərdən ən son aktiv qrup və ölkələri çıxarır
    entries = []
    seen = set()

    try:
        recent_victims = http_get_json("https://api.ransomware.live/v2/recentvictims", timeout=10)
        if isinstance(recent_victims, list):
            for v in recent_victims[:20]:
                group = (v.get("group_name") or v.get("group") or "Unknown Group").strip()
                victim = (v.get("post_title") or v.get("victim") or "Victim").strip()
                country = (v.get("country") or "Global").strip() or "Global"
                discovered = (v.get("discovered") or "")[:16]
                key = f"{group.lower()}|{victim.lower()}|{country.lower()}"
                if key in seen:
                    continue
                seen.add(key)
                entries.append({
                    "group": group,
                    "victim": victim,
                    "country": country,
                    "date": discovered,
                    "source": "Ransomware.live API",
                })
    except Exception:
        pass

    for n in news_items:
        blob = f"{n.get('title', '')} {n.get('summary', '')}"
        if "ransomware" in blob.lower() or "extortion" in blob.lower() or "wiper" in blob.lower():
            countries = extract_countries(blob) or ["Global"]
            for ctry in countries[:2]:
                key = f"{n.get('source', '').lower()}|{n.get('title', '')[:60].lower()}|{ctry.lower()}"
                if key in seen:
                    continue
                seen.add(key)
                entries.append({
                    "group": n.get("source") or "Threat Intel",
                    "victim": n.get("title")[:110],
                    "country": ctry,
                    "date": n.get("date") or now_az_str()[:10],
                    "source": n.get("source") or "CTI Feed",
                })

    for c in cves:
        if "known" in str(c.get("ransomware") or "").lower():
            key = f"kev|{c.get('cveID')}|global"
            if key not in seen:
                seen.add(key)
                entries.append({
                    "group": f"{c.get('vendor') or 'Vendor'} ({c.get('cveID')})",
                    "victim": c.get("product") or c.get("name") or c.get("cveID"),
                    "country": "Global",
                    "date": c.get("dateAdded") or now_az_str()[:10],
                    "source": "CISA KEV",
                })

    return entries[:25]


def detect_active_apts(news, cves, mitre_techniques):
    corpus_entries = []
    for n in news:
        corpus_entries.append({
            "text": f"{n.get('source', '')} {n.get('title', '')} {n.get('summary', '')}".lower(),
            "title": n.get("title") or "",
            "source": n.get("source") or "",
            "url": n.get("url") or "",
        })
    for c in cves:
        corpus_entries.append({
            "text": f"{c.get('cveID', '')} {c.get('vendor', '')} {c.get('product', '')} {c.get('name', '')} {c.get('action', '')}".lower(),
            "title": f"{c.get('cveID', '')}: {c.get('name') or ''}",
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
                    "title": entry["title"][:130],
                    "url": entry["url"],
                })
                for tid in TECH_RE.findall(txt.upper()):
                    if tid in mitre_techniques:
                        found_techs.add(tid)

        if not matched_mentions:
            continue

        mention_count = len(matched_mentions)
        activity_score = min(99, 75 + mention_count * 8)
        level = "CRITICAL" if mention_count >= 2 else "HIGH"

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
            "status_label": f"Matched in sources ({mention_count})",
            "focus": grp["focus"],
            "mitigation": grp["mitigation"],
            "scenario": grp["scenario"],
            "techniques": tech_details,
            "mentions": matched_mentions[:5],
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
            "source_results": [],
            "verdict": "",
            "checks": {},
        })

    custom_ioc = os.environ.get("CUSTOM_IOC", "").strip()
    if custom_ioc:
        if URL_RE.match(custom_ioc):
            add_ioc("url", custom_ioc, "Manual Workflow Input")
        elif IP_RE.match(custom_ioc):
            add_ioc("ip", custom_ioc, "Manual Workflow Input")
        elif HASH_RE.match(custom_ioc):
            add_ioc("hash", custom_ioc, "Manual Workflow Input")
        elif CVE_RE.match(custom_ioc):
            add_ioc("cve", custom_ioc, "Manual Workflow Input")
        else:
            add_ioc("domain", custom_ioc, "Manual Workflow Input")

    for n in news_items:
        blob = f"{n.get('title', '')} {n.get('summary', '')}"
        origin = f"[{n.get('source', 'CTI')}] {n.get('title', '')[:70]}"
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
            add_ioc("cve", c["cveID"], f"[CISA KEV] {c.get('vendor', '')} {c.get('product', '')}")

    return iocs[:50]


def check_urlhaus(ioc):
    auth = os.environ.get("URLHAUS_AUTH_KEY", "").strip()
    headers = {"User-Agent": "SOC-CTI-Radar/4.0"}
    if auth:
        headers["Auth-Key"] = auth
    try:
        if ioc["type"] == "url":
            res = http_post_form("https://urlhaus-api.abuse.ch/v1/url/", {"url": ioc["value"]}, headers=headers)
            if res.get("query_status") == "ok":
                return {"hit": True, "score_add": 45, "result": f"URLhaus: Malicious URL ({res.get('threat') or 'listed'})"}
        elif ioc["type"] == "domain":
            host = ioc["value"].split("/")[0]
            res = http_post_form("https://urlhaus-api.abuse.ch/v1/host/", {"host": host}, headers=headers)
            if res.get("query_status") == "ok" and (res.get("urls") or []):
                cnt = len(res.get("urls", []))
                return {"hit": True, "score_add": 40, "result": f"URLhaus: {cnt} malicious URLs on host"}
        elif ioc["type"] == "hash":
            algo = "sha256_hash" if len(ioc["value"]) == 64 else "md5_hash"
            res = http_post_form("https://urlhaus-api.abuse.ch/v1/payload/", {algo: ioc["value"]}, headers=headers)
            if res.get("query_status") == "ok":
                return {"hit": True, "score_add": 50, "result": f"URLhaus: Payload match ({res.get('signature') or 'malware'})"}
    except Exception:
        return {"score_add": 0, "result": "URLhaus: no hit / error"}
    return {"score_add": 0, "result": "URLhaus: clean / not listed"}


def check_virustotal(ioc):
    key = os.environ.get("VT_API_KEY", "").strip()
    if not key:
        return {"score_add": 0, "result": "VirusTotal: API key not configured"}
    headers = {"x-apikey": key, "User-Agent": "SOC-CTI-Radar/4.0"}
    try:
        if ioc["type"] == "ip":
            ep = f"https://www.virustotal.com/api/v3/ip_addresses/{urllib.parse.quote(ioc['value'])}"
        elif ioc["type"] == "domain":
            ep = f"https://www.virustotal.com/api/v3/domains/{urllib.parse.quote(ioc['value'])}"
        elif ioc["type"] == "hash":
            ep = f"https://www.virustotal.com/api/v3/files/{urllib.parse.quote(ioc['value'])}"
        else:
            return {"score_add": 0, "result": "VirusTotal: N/A for CVE"}

        data = http_get_json(ep, headers=headers)
        stats = (((data.get("data") or {}).get("attributes") or {}).get("last_analysis_stats")) or {}
        mal = int(stats.get("malicious", 0))
        susp = int(stats.get("suspicious", 0))
        add = min(60, mal * 10 + susp * 4)
        return {"malicious": mal, "suspicious": susp, "score_add": add, "result": f"VirusTotal: {mal} malicious, {susp} suspicious (+{add})"}
    except Exception:
        return {"score_add": 0, "result": "VirusTotal: query failed / not found"}


def check_abuseipdb(ioc):
    if ioc["type"] != "ip":
        return {"score_add": 0, "result": "AbuseIPDB: IP only"}
    key = os.environ.get("ABUSEIPDB_API_KEY", "").strip()
    if not key:
        return {"score_add": 0, "result": "AbuseIPDB: API key not configured"}
    try:
        q = urllib.parse.urlencode({"ipAddress": ioc["value"], "maxAgeInDays": "30"})
        data = http_get_json(
            f"https://api.abuseipdb.com/api/v2/check?{q}",
            headers={"Key": key, "Accept": "application/json", "User-Agent": "SOC-CTI-Radar/4.0"},
        )
        d = data.get("data") or {}
        conf = int(d.get("abuseConfidenceScore", 0))
        rep = int(d.get("totalReports", 0))
        add = int(conf * 0.5)
        return {"confidence": conf, "reports": rep, "score_add": add, "result": f"AbuseIPDB: {conf}% confidence, {rep} reports (+{add})"}
    except Exception:
        return {"score_add": 0, "result": "AbuseIPDB: query failed"}


def check_otx(ioc):
    key = os.environ.get("OTX_API_KEY", "").strip()
    headers = {"User-Agent": "SOC-CTI-Radar/4.0"}
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
            return {"score_add": 0, "result": "OTX: N/A for CVE"}

        data = http_get_json(ep, headers=headers)
        pulses = int(((data.get("pulse_info") or {}).get("count")) or 0)
        add = min(35, pulses * 5)
        return {"pulses": pulses, "score_add": add, "result": f"OTX: {pulses} threat pulses (+{add})"}
    except Exception:
        return {"score_add": 0, "result": "OTX: query failed"}


def check_shodan(ioc):
    if ioc["type"] != "ip":
        return {"score_add": 0, "result": "Shodan: IP only"}
    key = os.environ.get("SHODAN_API_KEY", "").strip()
    if not key:
        return {"score_add": 0, "result": "Shodan: API key not configured"}
    try:
        data = http_get_json(f"https://api.shodan.io/shodan/host/{urllib.parse.quote(ioc['value'])}?key={urllib.parse.quote(key)}")
        vulns = list((data.get("vulns") or {}).keys())
        ports = data.get("ports") or []
        add = min(30, len(vulns) * 8 + (5 if len(ports) > 5 else 0))
        return {"ports": ports[:10], "vulns": vulns[:8], "org": data.get("org"), "score_add": add, "result": f"Shodan: {len(ports)} open ports, {len(vulns)} vulns (+{add})"}
    except Exception:
        return {"score_add": 0, "result": "Shodan: no host data"}


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
        source_results = []

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
            if res.get("result"):
                source_results.append(res["result"])

        if ioc["type"] == "cve":
            source_results.append("CISA KEV: Known exploited vulnerability (+55)")
            score += 55
            reasons.append("CISA KEV (+55)")

        level, final_score = assign_level(score, ioc)
        if level == "CRITICAL":
            verdict = "CRITICAL — Confirmed malicious/high-risk activity across CTI sources. Block & investigate immediately."
        elif level == "HIGH":
            verdict = "HIGH — Elevated threat/exploitation signal. Hunt across logs, sessions & endpoints."
        elif level == "MEDIUM":
            verdict = "MEDIUM — Moderate/suspicious exposure. Correlate with perimeter, DNS & auth telemetry."
        else:
            verdict = "LOW — No malicious hits in queried CTI tools. Keep under observation."

        ioc["level"] = level
        ioc["score"] = final_score
        ioc["reasons"] = reasons if reasons else ["Base score only"]
        ioc["source_results"] = source_results
        ioc["verdict"] = verdict
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


def send_deep_cti_report(updated_at, source_count, news, cves, iocs, active_apts, live_ransomware):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    webapp_url = os.environ.get("WEBAPP_URL", "").strip()
    if not token or not chat_id:
        return

    darkweb_news = [n for n in news if n.get("category") == "darkweb_cti"][:3]
    global_news = [n for n in news if n.get("category") != "darkweb_cti"][:3]
    high_iocs = [x for x in iocs if x["level"] in ("CRITICAL", "HIGH")][:4]

    lines = [
        "🛰️ <b>DEEP CTI REPORT BOT — LIVE OPERATIONAL REPORT</b>",
        f"🕒 Time: <code>{updated_at}</code>",
        f"📡 Sources: <b>{source_count}</b> | 📰 News: <b>{len(news)}</b> | 🔍 IoC: <b>{len(iocs)}</b> | 🕵️ APT: <b>{len(active_apts)}</b> | 💀 RW: <b>{len(live_ransomware)}</b>",
    ]

    if live_ransomware:
        lines.append("")
        lines.append("💀 <b>Live Ransomware Activity (Latest):</b>")
        for r in live_ransomware[:3]:
            lines.append(f"• [<b>{r['country']}</b>] <b>{r['group']}</b> — {r['victim']}")

    if active_apts:
        lines.append("")
        lines.append("🕵️ <b>Detected APT Groups:</b>")
        for a in active_apts[:4]:
            t_codes = ", ".join(t["id"] for t in (a.get("techniques") or [])[:4])
            lines.append(f"• <b>{a['name']}</b> [{t_codes}] — Score {a['activity_score']}")

    lines.append("")
    lines.append("🕵️ <b>Darkweb & Leak:</b>")
    for n in darkweb_news:
        lines.append(f"• [{n['source']}] {n['title']}")

    lines.append("")
    lines.append("🌍 <b>Global Cyber News:</b>")
    for n in global_news:
        lines.append(f"• [{n['source']}] {n['title']}")

    if high_iocs:
        lines.append("")
        lines.append("🚨 <b>Top IoCs (Total Score):</b>")
        for it in high_iocs:
            lines.append(f"• [<b>{it['level']}</b> | Score: <b>{it['score']}</b>] <code>{it['value']}</code>")

    payload = {
        "chat_id": chat_id,
        "text": "\n".join(lines)[:4000],
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if webapp_url:
        payload["reply_markup"] = json.dumps({
            "inline_keyboard": [[{"text": "📲 Open SOC & CTI App", "web_app": {"url": webapp_url}}]]
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
    live_ransomware = extract_live_ransomware(news, cves)
    raw_iocs = extract_and_dedup_iocs(news, cves)
    iocs = enrich_iocs(raw_iocs)

    sources = (
        [{"name": n, "url": u, "type": "RSS"} for n, u in RSS_SOURCES]
        + [{"name": n, "url": u, "type": "Tor/Onion" if ".onion" in u.lower() else "CTI/Web"} for n, u in unique_web]
        + [
            {"name": "CISA KEV", "url": CISA_KEV_URL, "type": "KEV"},
            {"name": "Ransomware.live API", "url": "https://api.ransomware.live/v2/recentvictims", "type": "Ransomware"},
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
        "live_ransomware": live_ransomware,
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=2)

    send_deep_cti_report(updated_at, len(sources), news, cves, iocs, active_apts, live_ransomware)


if __name__ == "__main__":
    main()
