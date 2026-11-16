# Google Colab compatible
# 01_collect_official_sites.py
# J-LISの自治体公式サイトリンクを候補データとして収集する。
# 注意: J-LISの一覧ページは更新日が古い場合があるため、結果は確定URLではなく候補。

!pip -q install requests beautifulsoup4 pandas

import json, re, time
from datetime import date
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

INDEX_URL = "https://www.j-lis.go.jp/spd/map-search/cms_1069.html"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; 1741-municipality-research/0.1)"}
TODAY = date.today().isoformat()
session = requests.Session()
session.headers.update(HEADERS)

def get_soup(url):
    response = session.get(url, timeout=30)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return BeautifulSoup(response.text, "html.parser")

index = get_soup(INDEX_URL)

# J-LIS index page links to prefecture-level pages. Region links and prefecture links
# are both present; keep links whose visible text ends in 都/道/府/県 or equals 北海道.
prefecture_pages = {}
for a in index.select("a[href]"):
    label = a.get_text(" ", strip=True)
    href = urljoin(INDEX_URL, a["href"])
    if label == "北海道" or re.fullmatch(r".+[都道府県]", label):
        if urlparse(href).netloc.endswith("j-lis.go.jp"):
            prefecture_pages[label] = href

print("Prefecture pages:", len(prefecture_pages))
if len(prefecture_pages) < 47:
    print("WARNING: expected 47 prefecture pages; inspect prefecture_pages before continuing.")

records = []
for prefecture, page_url in prefecture_pages.items():
    try:
        soup = get_soup(page_url)
        for a in soup.select("a[href]"):
            name = a.get_text(" ", strip=True)
            href = urljoin(page_url, a["href"])
            host = urlparse(href).netloc.lower()
            # Skip empty labels, non-http links, and links back into J-LIS.
            if not name or not href.startswith("http") or host.endswith("j-lis.go.jp"):
                continue
            # Retain only links that look like public-sector websites.
            if not (host.endswith(".lg.jp") or ".lg.jp." in host or
                    host.endswith(".go.jp") or "city." in host or
                    "town." in host or "vill." in host or
                    "pref." in host):
                continue
            records.append({
                "candidate_id": f"jlis-{len(records)+1:05d}",
                "prefecture": prefecture,
                "municipality_name": name,
                "municipality_type": None,
                "official_site_url": href,
                "catchphrase": None,
                "source_id": "src-jlis-map",
                "source_url": page_url,
                "retrieved_at": TODAY,
                "verification_status": "unverified",
                "notes": "J-LIS link candidate; confirm current URL and municipality-code match."
            })
        time.sleep(0.4)
    except Exception as e:
        print("FAILED:", prefecture, page_url, repr(e))

# Remove exact duplicate rows while preserving order.
unique = {}
for row in records:
    key = (row["prefecture"], row["municipality_name"], row["official_site_url"])
    unique[key] = row
records = list(unique.values())

output_path = "/content/municipality_sites_candidates.jsonl"
with open(output_path, "w", encoding="utf-8") as f:
    for row in records:
        f.write(json.dumps(row, ensure_ascii=False) + "\\n")

print("Candidate rows:", len(records))
print("Saved:", output_path)

# Download the JSONL from Colab.
from google.colab import files
files.download(output_path)
