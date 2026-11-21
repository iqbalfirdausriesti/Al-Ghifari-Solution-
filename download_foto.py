#!/usr/bin/env python3
"""
Download foto produk PRESISI dari daftar-produk.xlsx.

Kenapa hasil lama ngawur (logo, artis, meme)? Karena pencarian gambar langsung
dipakai tanpa verifikasi. Skrip ini menambahkan 4 lapis filter:
  1. Judul/URL gambar HARUS memuat semua token model (mis. "galaxy" + "s25").
  2. Varian salah ditolak (S25 Ultra, iPhone 15 Pro Max, dst.).
  3. Domain stok/watermark/sosmed ditolak (alamy, pinterest, dll.).
  4. CLIP memverifikasi isi gambar benar-benar HP/laptop/earbuds/dll.
     (bukan logo, orang, poster, meme). Plus dedupe & ukuran minimal.
Kalau tidak ada yang lolos, foto DIKOSONGKAN (bukan diisi asal) dan dicatat di
foto-laporan.csv supaya bisa kamu upload manual.

ENV: ULANG_SEMUA=true|false  (hapus & unduh ulang)   NOMOR="15,16,35" (hanya baris tsb)
"""
import csv, hashlib, io, os, re, sys, time
from urllib.parse import urlparse
import openpyxl, requests
from PIL import Image

XLSX = "daftar-produk.xlsx"
LAPORAN = "foto-laporan.csv"
ULANG = os.getenv("ULANG_SEMUA", "true").lower() == "true"
NOMOR = {int(x) for x in re.findall(r"\d+", os.getenv("NOMOR", ""))}
MIN_SISI, MAX_SISI, JUMLAH = 500, 1200, 3
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124 Safari/537.36"}

BLOK_DOMAIN = ("alamy", "pinterest", "shutterstock", "istockphoto", "gettyimages", "dreamstime",
               "123rf", "depositphotos", "facebook", "instagram", "tiktok", "youtube", "twimg",
               "twitter", "x.com", "reddit", "ebay", "aliexpress", "wallpaper", "vecteezy",
               "freepik", "pngtree", "pngwing", "flaticon", "redbubble", "etsy")
BLOK_KATA = ("logo", "wallpaper", "meme", "vector", "icon", "sticker", "poster", "wallpapers",
             "case ", "casing", "cover", "tempered", "screen protector", "skin", "mockup",
             "concept", "render leak", "drawing", "illustration", "cartoon", "tattoo", "actress",
             "actor", "model photo", "unboxing thumbnail", "vs ")
PREFERRED = ("gsmarena", "apple.com", "samsung.com", "mi.com", "xiaomi", "oppo.com", "vivo.com",
             "realme", "store.google", "asus.com", "lenovo.com", "acer.com", "hp.com", "dell.com",
             "msi.com", "axioo", "anker", "baseus", "logitech", "infinix", "tecno", "poco",
             "notebookcheck", "kompas", "carousell", "tokopedia", "bukalapak", "blibli", "wikimedia")
KONFLIK = {"pro", "max", "plus", "ultra", "fe", "mini", "lite", "edge", "flip", "fold", "neo",
           "gt", "turbo", "air", "slim"}
STOP = {"second", "kabel", "data", "5g", "gb", "tb", "ram", "inch", "bln"}
# Query tambahan (Inggris) untuk produk berbahasa Indonesia / sulit
ALIAS = {
    "Kabel Data USB-C 100W 2m": "Baseus USB-C cable 100W 2m",
    "Power Bank 20.000 mAh 65W": "Anker power bank 20000mAh 65W",
    "Charger GaN 65W 3 Port": "Anker GaN charger 65W 3 port",
    "M331 Silent Mouse": "Logitech M331 Silent Plus mouse",
}

# ---------- util teks ----------
def norm(s):
    s = s.lower()
    s = re.sub(r"(?<=\d)\.(?=\d{3}\b)", "", s)
    s = s.replace("+", " plus ")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s)).strip()

def pisah(s):
    s = re.sub(r"([a-z])(\d)", r"\1 \2", s)
    return re.sub(r"(\d)([a-z])", r"\1 \2", s)

def token_wajib(nama, merek):
    s = nama.lower().replace('"', " inch ")
    s = re.sub(r"\b\d+\s*/\s*\d+\b", " ", s)           # 8/256
    s = re.sub(r"\b\d+\s*(gb|tb)\b", " ", s)            # 256gb
    toks = [t for t in norm(s).split() if t not in STOP]
    if re.fullmatch(r"\d+", toks[-1] if toks else "") and "macbook" in toks and len(toks) > 3:
        pass
    return toks

def butuh_merek(toks):
    return not ({"iphone", "macbook", "airpods"} & set(toks))

def cocok_teks(teks, toks, merek, rasio=1.0):
    a = norm(teks)
    b = pisah(a)
    def ada(t):
        pat = r"(?<![a-z0-9])%s(?![a-z0-9])"
        return bool(re.search(pat % re.escape(t), a)) or bool(re.search(pat % re.escape(pisah(t)), b))
    if butuh_merek(toks) and norm(merek) not in a:
        return False
    skor = sum(ada(t) for t in toks)
    if skor < max(1, round(rasio * len(toks))):
        return False
    ada_kata = set(a.split())
    if (KONFLIK & ada_kata) - set(toks):
        return False
    return True

def domain_ok(url):
    h = urlparse(url).netloc.lower()
    return not any(b in h for b in BLOK_DOMAIN)

def kata_buruk(teks):
    t = " " + teks.lower() + " "
    return any(k in t for k in BLOK_KATA)

# ---------- CLIP ----------
_clip = None
def clip():
    global _clip
    if _clip is None:
        import torch
        from transformers import CLIPModel, CLIPProcessor
        m = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval()
        p = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        _clip = (torch, m, p)
    return _clip

NEG = ["a logo or brand emblem", "a photo of a person", "a poster with text", "a meme or cartoon",
       "a screenshot of a website", "a drawing or illustration", "a landscape photo", "a painting",
       "a group of people", "a document or book cover"]
def jenis(cat, nama):
    n = nama.lower()
    if cat == "Smartphone": return ["a photo of a smartphone", "a product photo of a mobile phone"]
    if cat == "Laptop": return ["a photo of a laptop computer", "a product photo of a notebook computer"]
    if "airpods" in n or "buds" in n: return ["a photo of wireless earbuds", "a photo of an earbuds charging case"]
    if "watch" in n or "band" in n: return ["a photo of a smartwatch", "a photo of a fitness band"]
    if "mouse" in n: return ["a photo of a computer mouse"]
    if "power bank" in n: return ["a photo of a power bank"]
    if "charger" in n: return ["a photo of a USB wall charger", "a photo of a charging adapter"]
    if "kabel" in n or "cable" in n: return ["a photo of a USB cable", "a photo of a charging cable"]
    return ["a product photo"]

def clip_ok(img, pos):
    torch, m, p = clip()
    labels = pos + NEG
    inp = p(text=labels, images=img, return_tensors="pt", padding=True)
    with torch.no_grad():
        pr = m(**inp).logits_per_image.softmax(dim=1)[0]
    s_pos = float(pr[: len(pos)].sum())
    return s_pos >= 0.60, s_pos

# ---------- gambar ----------
def ahash(img):
    g = img.convert("L").resize((8, 8))
    px = list(g.getdata()); avg = sum(px) / 64
    return sum(1 << i for i, v in enumerate(px) if v > avg)

def ambil(url):
    try:
        r = requests.get(url, headers=UA, timeout=20, stream=True)
        if r.status_code != 200 or "image" not in r.headers.get("content-type", "image"):
            return None
        data = r.raw.read(8_000_001, decode_content=True)
        if len(data) > 8_000_000: return None
        img = Image.open(io.BytesIO(data)); img.load()
        return img.convert("RGB")
    except Exception:
        return None

def cari(query):
    from ddgs import DDGS
    for t in range(3):
        try:
            return DDGS().images(query, max_results=40, safesearch="moderate") or []
        except Exception as e:
            print(f"   ! retry {t+1}: {str(e)[:70]}"); time.sleep(4 * (t + 1))
    return []

def proses(nama, kat, merek):
    toks = token_wajib(nama, merek)
    rasio = 0.6 if kat == "Aksesoris" else 1.0
    pos = jenis(kat, nama)
    dasar = ALIAS.get(nama, f"{merek} {nama}" if norm(merek) not in norm(nama) else nama)
    queries = [f"{dasar} product photo", f"{dasar} front back", f"{dasar} official", f"{dasar} review"]
    kandidat, seen = [], set()
    for q in queries:
        for r in cari(q):
            u = r.get("image")
            if not u or u in seen: continue
            seen.add(u)
            teks = " ".join([r.get("title", ""), r.get("url", ""), u])
            if not domain_ok(u) or not domain_ok(r.get("url", "")): continue
            if kata_buruk(r.get("title", "") + " " + u): continue
            if not cocok_teks(teks, toks, merek, rasio): continue
            w, h = r.get("width") or 0, r.get("height") or 0
            if w and h and (min(w, h) < MIN_SISI or not 0.5 <= w / h <= 2.0): continue
            pref = any(d in (r.get("url", "") + u).lower() for d in PREFERRED)
            kandidat.append((pref, w * h, u, r.get("url", "")))
        time.sleep(1.5)
        if len(kandidat) >= 25: break
    kandidat.sort(key=lambda x: (not x[0], -x[1]))
    hasil, hashes = [], []
    for _, _, u, src in kandidat[:50]:
        if len(hasil) == JUMLAH: break
        img = ambil(u)
        if img is None or min(img.size) < MIN_SISI: continue
        ar = img.width / img.height
        if not 0.5 <= ar <= 2.0: continue
        h = ahash(img)
        if any(bin(h ^ x).count("1") < 8 for x in hashes): continue
        ok, sk = clip_ok(img, pos)
        if not ok: continue
        hashes.append(h)
        img.thumbnail((MAX_SISI, MAX_SISI))
        hasil.append((img, u, src, sk))
    return hasil

def main():
    wb = openpyxl.load_workbook(XLSX)
    ws = wb.active
    hdr = [c.value for c in ws[1]]
    cF = [hdr.index(f"Foto {i}") for i in (1, 2, 3)]
    cOK = hdr.index("Foto Sudah Ada?")
    laporan = []
    for row in ws.iter_rows(min_row=2):
        no, nama, kat, merek = (row[0].value, row[1].value, row[2].value, row[3].value)
        if not isinstance(no, int) or not nama: continue
        if NOMOR and no not in NOMOR: continue
        files = [row[i].value for i in cF]
        ada = [f for f in files if f and os.path.exists(f)]
        if not ULANG and not NOMOR and len(ada) == JUMLAH:
            row[cOK].value = "Ya"; continue
        for f in files:
            if f and os.path.exists(f): os.remove(f)
        print(f"[{no}] {nama}")
        hasil = proses(nama, kat, merek)
        for (img, u, src, sk), f in zip(hasil, files):
            img.save(f, "JPEG", quality=88, optimize=True)
            laporan.append([no, nama, f, f"{sk:.2f}", u, src])
            print(f"   OK {f} (clip {sk:.2f})")
        for f in files[len(hasil):]:
            laporan.append([no, nama, f, "KOSONG", "", ""])
        row[cOK].value = "Ya" if len(hasil) == JUMLAH else f"Perlu cek ({len(hasil)}/{JUMLAH})"
        print(f"   => {len(hasil)}/{JUMLAH}")
    wb.save(XLSX)
    baru = not os.path.exists(LAPORAN) or not NOMOR
    with open(LAPORAN, "a" if NOMOR and os.path.exists(LAPORAN) else "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if baru: w.writerow(["No", "Produk", "File", "Skor CLIP", "URL gambar", "Halaman sumber"])
        w.writerows(laporan)

if __name__ == "__main__":
    main()
