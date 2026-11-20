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
