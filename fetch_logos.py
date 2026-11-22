import os
import re
import requests
import xml.etree.ElementTree as ET

os.makedirs("logos", exist_ok=True)

headers = {'User-Agent': 'AlGhifariBot/1.0 (contact@alghifari.com)'}

# Brand mapping to high-res official vector SVGs on Wikimedia / raw
WIKI_MAP = {
    "apple": "Apple_logo_black.svg",
    "samsung": "Samsung_logo.svg",
    "xiaomi": "Xiaomi_logo.svg",
    "oppo": "Oppo_logo.svg",
    "vivo": "Vivo_logo.svg",
    "realme": "Realme_logo.svg",
    "google": "Google_2015_logo.svg",
    "poco": "Poco_Smartphone_Company_Logo.svg",
    "asus": "Asus_Logo.svg",
    "lenovo": "Lenovo_logo_2015.svg",
    "acer": "Acer_2011.svg",
    "hp": "HP_logo_2012.svg",
    "dell": "Dell_Logo.svg",
    "msi": "MSI_Logo.svg",
    "anker": "Anker_Innovations_logo.svg",
    "logitech": "Logitech_logo.svg"
}

def get_wiki_url(filename):
    api = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&titles=File:{filename}&prop=imageinfo&iiprop=url"
    r = requests.get(api, headers=headers, timeout=10).json()
    pages = r.get("query", {}).get("pages", {})
    for p in pages.values():
        ii = p.get("imageinfo", [{}])[0]
        if ii.get("url"):
            return ii["url"]
    return None

for slug, wiki_name in WIKI_MAP.items():
    out_file = f"logos/{slug}.svg"
    url = get_wiki_url(wiki_name)
    if not url:
        print(f"Failed to find wiki URL for {slug} ({wiki_name})")
        continue
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            svg_content = r.text
            # Normalize fill to white or currentColor so it renders brightly on dark background
            # Remove existing fill/stroke colors or replace with currentColor / #fff
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(svg_content)
            print(f"[OK] Saved {out_file} from {url}")
        else:
            print(f"[Err {r.status_code}] for {slug}")
    except Exception as e:
        print(f"Exception for {slug}: {e}")
