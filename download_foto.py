import os
import re
import time
from io import BytesIO
import openpyxl
import requests
from PIL import Image

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

EXCEL_FILE = "daftar-produk.xlsx"
SHEET_NAME = "Daftar Produk"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def download_as_jpg(url, save_path):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            bg.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
            img = bg
        else:
            img = img.convert("RGB")

        # Skip tiny thumbnails/icons
        if img.width < 220 or img.height < 220:
            return False

        # Resize if overly huge to keep GitHub repo lightweight
        max_dim = 1000
        if max(img.width, img.height) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

        img.save(save_path, "JPEG", quality=88, optimize=True)
        return True
    except Exception:
        return False


def search_images(query, max_results=15):
    for attempt in range(3):
        try:
            with DDGS() as ddgs:
                return list(ddgs.images(query, max_results=max_results))
        except Exception as e:
            print(f"  Percobaan {attempt + 1} gagal ({e}), menunggu...")
            time.sleep(3 * (attempt + 1))
    return []


def main():
    wb = openpyxl.load_workbook(EXCEL_FILE)
    ws = wb[SHEET_NAME]

    for row in range(2, ws.max_row + 1):
        no = ws.cell(row, 1).value
        if not isinstance(no, (int, float)):
            continue

        nama = str(ws.cell(row, 2).value or "").strip()
        merek = str(ws.cell(row, 4).value or "").strip()
        target_files = [
            ws.cell(row, 9).value,   # Foto 1
            ws.cell(row, 10).value,  # Foto 2
            ws.cell(row, 11).value,  # Foto 3
        ]

        missing_files = [f for f in target_files if f and not os.path.exists(f)]
        if not missing_files:
            ws.cell(row, 12).value = "Ya"
            print(f"[{int(no):02d}/39] {nama} -> Lengkap")
            continue

        clean_nama = re.sub(r"\(second\)", "", nama, flags=re.IGNORECASE).strip()
        base_q = clean_nama if merek.lower() in clean_nama.lower() else f"{merek} {clean_nama}"
        query = f"{base_q} product photo"

        print(f"[{int(no):02d}/39] Mencari foto: {query}...")
        results = search_images(query, max_results=15)

        url_idx = 0
        for filename in missing_files:
            saved = False
            while url_idx < len(results) and not saved:
                img_url = results[url_idx].get("image")
                url_idx += 1
                if img_url and download_as_jpg(img_url, filename):
                    print(f"  [OK] {filename}")
                    saved = True
            if not saved:
                print(f"  [GAGAL] {filename}")

        if all(f and os.path.exists(f) for f in target_files):
            ws.cell(row, 12).value = "Ya"

        wb.save(EXCEL_FILE)
        time.sleep(1.5)

    print("\nSelesai! Foto produk berhasil diunduh dan daftar-produk.xlsx telah diperbarui.")


if __name__ == "__main__":
    main()
