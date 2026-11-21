#!/usr/bin/env python3
"""
Download foto produk PRESISI dari daftar-produk.xlsx  (v3)

Alur per produk:
  A. Kalau ada baris di url-manual.csv  -> pakai URL itu dulu (paling pasti benar).
  B. Sisanya dicari dari 3 sumber: DuckDuckGo, Bing, Wikimedia Commons.
  C. Tiap kandidat harus lolos SEMUA filter:
       1. judul/URL memuat semua token model (mis. "galaxy" + "s25")
       2. bukan varian lain (Ultra/Pro/Max/FE/Plus... yang tidak ada di nama produk)
       3. bukan domain stok/sosmed/watermark, bukan kata logo/meme/poster/dll
       4. ukuran >= 500px, rasio wajar, bukan duplikat foto lain
       5. CLIP: isi gambar benar-benar HP/laptop/earbuds/dll (bukan orang/logo/teks)
  D. Tidak lolos = dikosongkan & dicatat. TIDAK PERNAH diisi asal.

ENV:  ULANG_SEMUA=true|false   NOMOR="15,16,35"
File opsional url-manual.csv  (header: no,url1,url2,url3)
"""
import csv, html, io, json, os, re, time
from collections import Counter
from urllib.parse import urlparse, quote_plus
import openpyxl, requests
from PIL import Image

XLSX, LAPORAN, MANUAL = "daftar-produk.xlsx", "foto-laporan.csv", "url-manual.csv"
ULANG = os.getenv("ULANG_SEMUA", "true").strip().lower() == "true"
NOMOR = {int(x) for x in re.findall(r"\d+", os.getenv("NOMOR", ""))}
MIN_SISI, MAX_SISI, JUMLAH, CLIP_MIN = 500, 1200, 3, 0.50
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
UA_WIKI = {"User-Agent": "AlGhifariFotoBot/1.0 (github actions; product catalog)"}

BLOK_DOMAIN = ("alamy", "pinterest", "shutterstock", "istockphoto", "gettyimages", "dreamstime",
               "123rf", "depositphotos", "facebook", "fbcdn", "instagram", "tiktok", "youtube",
               "ytimg", "twimg", "twitter", "x.com", "reddit", "ebay", "aliexpress", "vecteezy",
               "freepik", "pngtree", "pngwing", "flaticon", "redbubble", "etsy", "wallpaper",
               "someecards", "tumblr", "weibo", "vk.com", "alicdn")
BLOK_KATA = ("logo", "wallpaper", "meme", "vector", "icon", "sticker", "poster", "casing",
             "cover", "tempered", "screen protector", "skin", "mockup", "concept", "leak",
             "drawing", "illustration", "cartoon", "tattoo", "actress", "actor", "wedding",
             "thumbnail", "banner", "infographic", "wallpapers", "ringtone", "case for")
PREFERRED = ("wikimedia", "gsmarena", "apple.com", "samsung.com", "mi.com", "xiaomi", "oppo.com",
             "vivo.com", "realme", "store.google", "asus.com", "lenovo.com", "acer.com", "hp.com",
             "dell.com", "msi.com", "axioo", "anker", "baseus", "logitech", "infinix", "tecno",
             "poco", "notebookcheck", "tokopedia", "bukalapak", "blibli", "kompas", "carousell")
KONFLIK = {"pro", "max", "plus", "ultra", "fe", "mini", "lite", "edge", "flip", "fold", "neo",
           "gt", "turbo", "air", "slim", "se"}
STOP = {"second", "kabel", "data", "5g", "gb", "tb", "ram", "inch", "bln"}
ALIAS = {
    "Kabel Data USB-C 100W 2m": "Baseus USB-C cable 100W 2m",
    "Power Bank 20.000 mAh 65W": "Anker power bank 20000mAh 65W",
    "Charger GaN 65W 3 Port": "Anker GaN charger 65W 3 port",
    "M331 Silent Mouse": "Logitech M331 Silent Plus mouse",
    "Smart Band 9": "Xiaomi Smart Band 9",
    "Watch SE 2": "Apple Watch SE 2",
    "Galaxy Buds3": "Samsung Galaxy Buds3",
}

# ---------------- teks ----------------
def norm(s):
    s = str(s).lower()
    s = re.sub(r"(?<=\d)\.(?=\d{3}\b)", "", s)
    s = s.replace("+", " plus ")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s)).strip()

def pisah(s):
    s = re.sub(r"([a-z])(\d)", r"\1 \2", s)
    return re.sub(r"(\d)([a-z])", r"\1 \2", s)

def token_wajib(nama):
    s = nama.lower().replace('"', " inch ")
    s = re.sub(r"\b\d+\s*/\s*\d+\b", " ", s)
    s = re.sub(r"\b\d+\s*(gb|tb)\b", " ", s)
    return [t for t in norm(s).split() if t not in STOP]

def cocok_teks(teks, toks, merek, rasio):
    a = norm(teks); b = pisah(a)
    pat = r"(?<![a-z0-9])%s(?![a-z0-9])"
    ada = lambda t: bool(re.search(pat % re.escape(t), a)) or bool(re.search(pat % re.escape(pisah(t)), b))
    if not ({"iphone", "macbook", "airpods"} & set(toks)) and norm(merek) not in a:
        return False
    if sum(ada(t) for t in toks) < max(1, round(rasio * len(toks))):
        return False
    return not ((KONFLIK & set(a.split())) - set(toks))

def domain_ok(url):
    h = urlparse(str(url)).netloc.lower()
    return not any(b in h for b in BLOK_DOMAIN)

def kata_buruk(t):
    t = " " + t.lower() + " "
    return any(k in t for k in BLOK_KATA)

# ---------------- CLIP ----------------
_clip = None
def clip():
    global _clip
    if _clip is None:
        import torch
        from transformers import CLIPModel, CLIPProcessor
        _clip = (torch, CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval(),
                 CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32"))
    return _clip

NEG = ["a logo or brand emblem", "a photo of a person", "a poster with text", "a meme or cartoon",
       "a screenshot of a website", "a drawing or illustration", "a landscape photo", "a painting",
       "a group of people", "a document or book cover"]

def jenis(cat, nama):
    n = nama.lower()
    if cat == "Smartphone": return ["a photo of a smartphone", "a product photo of a mobile phone"]
    if cat == "Laptop": return ["a photo of a laptop computer", "a product photo of a notebook computer"]
    if "airpods" in n or "buds" in n: return ["a photo of wireless earbuds", "a photo of earbuds in a charging case"]
    if "watch" in n or "band" in n: return ["a photo of a smartwatch", "a photo of a fitness band"]
    if "mouse" in n: return ["a photo of a computer mouse"]
    if "power bank" in n: return ["a photo of a power bank"]
    if "charger" in n: return ["a photo of a USB wall charger", "a photo of a charging adapter"]
    if "kabel" in n or "cable" in n: return ["a photo of a USB cable", "a photo of a charging cable"]
    return ["a product photo"]

def clip_ok(img, pos):
    try:
        torch, m, p = clip()
        inp = p(text=pos + NEG, images=img, return_tensors="pt", padding=True)
        with torch.no_grad():
            pr = m(**inp).logits_per_image.softmax(dim=1)[0]
        s = float(pr[: len(pos)].sum())
        return s >= CLIP_MIN, s
    except Exception as e:
        print("   ! CLIP gagal, gambar ditolak:", str(e)[:80])
        return False, 0.0

# ---------------- gambar ----------------
def ahash(img):
    px = list(img.convert("L").resize((8, 8)).getdata()); avg = sum(px) / 64
    return sum(1 << i for i, v in enumerate(px) if v > avg)

def ambil(url, referer=""):
    for ref in ([referer, ""] if referer else [""]):
        try:
            hd = dict(UA_WIKI if "wikimedia" in url else UA)
            if ref: hd["Referer"] = ref
            r = requests.get(url, headers=hd, timeout=20, stream=True)
            if r.status_code != 200: continue
            data = r.raw.read(8_000_001, decode_content=True)
            if len(data) > 8_000_000: return None
            img = Image.open(io.BytesIO(data)); img.load()
            return img.convert("RGB")
        except Exception:
            continue
    return None

# ---------------- sumber pencarian ----------------
def sumber_ddg(q):
    try:
        from ddgs import DDGS
    except Exception:
        return []
    for t in range(3):
        try:
            rs = DDGS().images(q, max_results=40, safesearch="moderate") or []
            return [dict(image=r.get("image"), title=r.get("title", ""), src=r.get("url", ""),
                         w=r.get("width"), h=r.get("height"), via="ddg") for r in rs]
        except Exception as e:
            print(f"   ! ddg retry {t+1}: {str(e)[:60]}"); time.sleep(4 * (t + 1))
    return []

def sumber_bing(q):
    try:
        u = f"https://www.bing.com/images/async?q={quote_plus(q)}&first=0&count=35&adlt=off&qft=+filterui:imagesize-large"
        txt = requests.get(u, headers=UA, timeout=25).text
        out = []
        for m in re.findall(r'\bm="(\{[^"]+\})"', txt):
            try: d = json.loads(html.unescape(m))
            except Exception: continue
            if d.get("murl"):
                out.append(dict(image=d["murl"], title=re.sub(r"<.*?>", "", d.get("t", "")),
                                src=d.get("purl", ""), w=None, h=None, via="bing"))
        return out
    except Exception as e:
        print("   ! bing gagal:", str(e)[:60]); return []

def sumber_wiki(q):
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", headers=UA_WIKI, timeout=25, params=dict(
            action="query", format="json", generator="search", gsrnamespace=6, gsrsearch=q,
            gsrlimit=20, prop="imageinfo", iiprop="url|size|mime", iiurlwidth=1200))
        out = []
        for p in (r.json().get("query", {}).get("pages", {}) or {}).values():
            ii = (p.get("imageinfo") or [{}])[0]
            if not str(ii.get("mime", "")).startswith("image/jpeg") and not str(ii.get("mime", "")).startswith("image/png"):
                continue
            out.append(dict(image=ii.get("thumburl") or ii.get("url"), title=p.get("title", ""),
                            src=ii.get("descriptionurl", "wikimedia"), w=ii.get("width"), h=ii.get("height"), via="wiki"))
        return out
    except Exception as e:
        print("   ! wiki gagal:", str(e)[:60]); return []

# ---------------- proses satu produk ----------------
def baca_manual():
    d = {}
    if os.path.exists(MANUAL):
        with open(MANUAL, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                r = {k.strip().lower(): (v or "").strip() for k, v in r.items() if k}
                try: d[int(r.get("no", ""))] = [r[k] for k in ("url1", "url2", "url3") if r.get(k)]
                except ValueError: pass
    return d

def terima(img, hashes, pos, cek_clip=True):
    if min(img.size) < MIN_SISI or not 0.5 <= img.width / img.height <= 2.0: return None, "ukuran"
    h = ahash(img)
    if any(bin(h ^ x).count("1") < 8 for x in hashes): return None, "duplikat"
    sk = 1.0
    if cek_clip:
        ok, sk = clip_ok(img, pos)
        if not ok: return None, "clip"
    hashes.append(h)
    im = img.copy(); im.thumbnail((MAX_SISI, MAX_SISI))
    return (im, sk), None

def proses(nama, kat, merek, manual_urls):
    toks = token_wajib(nama)
    rasio = 0.6 if kat == "Aksesoris" else 1.0
    pos = jenis(kat, nama)
    st, hasil, hashes = Counter(), [], []

    # A. URL manual (dipercaya, tanpa filter teks/CLIP)
    for u in manual_urls:
        if len(hasil) == JUMLAH: break
        img = ambil(u)
        r, why = terima(img, hashes, pos, cek_clip=False) if img else (None, "unduh")
        if r: hasil.append((r[0], u, "manual", 1.0))
        else: st["manual_x_" + why] += 1
    if len(hasil) == JUMLAH:
        print("   stat:", dict(st)); return hasil

    # B. cari otomatis
    dasar = ALIAS.get(nama) or (" ".join(toks) if norm(merek) in norm(nama) or {"iphone", "macbook", "airpods"} & set(toks) else f"{merek} {' '.join(toks)}")
    plan = [(sumber_ddg, dasar + " product photo"), (sumber_bing, dasar + " product photo"),
            (sumber_wiki, dasar), (sumber_ddg, dasar + " front back"), (sumber_bing, dasar + " official"),
            (sumber_ddg, dasar + " official")]
    kandidat, seen = [], set()
    for fn, q in plan:
        rs = fn(q); st[f"cari_{rs[0]['via'] if rs else fn.__name__[7:]}"] += len(rs)
        for r in rs:
            u = r.get("image")
            if not u or u in seen: continue
            seen.add(u)
            judul, src = str(r.get("title", "")), str(r.get("src", ""))
            if not domain_ok(u) or not domain_ok(src): st["x_domain"] += 1; continue
            if kata_buruk(judul + " " + u): st["x_kata"] += 1; continue
            if not cocok_teks(" ".join([judul, src, u]), toks, merek, rasio): st["x_teks"] += 1; continue
            try: w, h = int(r.get("w") or 0), int(r.get("h") or 0)
            except (TypeError, ValueError): w = h = 0
            if w and h and (min(w, h) < MIN_SISI or not 0.5 <= w / h <= 2.0): st["x_ukuran"] += 1; continue
            pref = any(d in (src + u).lower() for d in PREFERRED)
            kandidat.append((pref, w * h, u, src, r["via"]))
        time.sleep(1.2)
    kandidat.sort(key=lambda x: (not x[0], -x[1]))
    st["lolos_teks"] = len(kandidat)
    for _, _, u, src, via in kandidat[:60]:
        if len(hasil) == JUMLAH: break
        img = ambil(u, src if src.startswith("http") else "")
        if img is None: st["x_unduh"] += 1; continue
        r, why = terima(img, hashes, pos)
        if not r: st["x_" + why] += 1; continue
        hasil.append((r[0], u, f"{via}:{src}", r[1]))
    print("   stat:", dict(st), "| token:", toks)
    return hasil

def tulis_laporan(rows):
    with open(LAPORAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["No", "Produk", "File", "Skor CLIP", "URL gambar", "Sumber", "Status"])
        w.writerows(rows)

def main():
    wb = openpyxl.load_workbook(XLSX); ws = wb.active
    hdr = [c.value for c in ws[1]]
    cF = [hdr.index(f"Foto {i}") for i in (1, 2, 3)]; cOK = hdr.index("Foto Sudah Ada?")
    manual = baca_manual()
    lama = {}
    if NOMOR and os.path.exists(LAPORAN):
        with open(LAPORAN, encoding="utf-8") as f:
            for r in list(csv.reader(f))[1:]:
                if r and r[0].isdigit() and int(r[0]) not in NOMOR: lama.setdefault(int(r[0]), []).append(r)
    rows = [r for v in lama.values() for r in v]
    for row in ws.iter_rows(min_row=2):
        no, nama, kat, merek = (row[0].value, row[1].value, row[2].value, row[3].value)
        if not isinstance(no, int) or not nama: continue
        if NOMOR and no not in NOMOR: continue
        files = [row[i].value for i in cF]
        if not ULANG and not NOMOR and all(f and os.path.exists(f) for f in files):
            row[cOK].value = "Ya"; continue
        print(f"[{no}] {nama}", flush=True)
        try:
            hasil = proses(nama, kat, merek, manual.get(no, []))
        except Exception as e:
            print("   ! ERROR produk dilewati:", repr(e)[:150]); hasil = []
        if hasil:  # ganti foto lama hanya jika ada foto baru terverifikasi
            for f in files:
                if f and os.path.exists(f): os.remove(f)
            for (img, u, src, sk), f in zip(hasil, files):
                img.save(f, "JPEG", quality=88, optimize=True)
                rows.append([no, nama, f, f"{sk:.2f}", u, src, "OK"])
                print(f"   OK {f} (clip {sk:.2f})")
        for f in files[len(hasil):]:
            rows.append([no, nama, f, "", "", "", "KOSONG" if hasil else "KOSONG-foto lama dipertahankan, belum terverifikasi"])
        row[cOK].value = "Ya" if len(hasil) == JUMLAH else f"Perlu cek ({len(hasil)}/{JUMLAH})"
        print(f"   => {len(hasil)}/{JUMLAH}", flush=True)
        wb.save(XLSX); tulis_laporan(rows)   # simpan bertahap
    wb.save(XLSX); tulis_laporan(rows)

if __name__ == "__main__":
    main()
