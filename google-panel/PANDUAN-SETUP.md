# Panduan Setup Google Panel — Al Ghifari Solution

Dengan **Google Panel** ini, Anda bisa mengelola seluruh isi website **langsung dari Google Sheets** tanpa perlu mengedit kode HTML lagi:
- Mengganti **Banner Utama ("TRENDING SEKARANG")** agar teks, tombol, dan produk/3D di sisi kanan selalu cocok.
- Mengganti **Video Trending Sekarang** (manual lewat file `.mp4` / link YouTube biasa & Shorts, **atau otomatis tiap hari lintas merk resmi**).
- Mengatur produk mana saja yang masuk **Flash Sale Hari Ini** dan urutannya.
- Menambah/mengedit produk & kategori baru (`HP`, `Laptop`, `Aksesoris`, `Tablet`, `Wearable`, dll.).
- Menyesuaikan harga massal per merk atau per kategori sekaligus (misal: turun 5% khusus semua Samsung, atau naik Rp100.000 khusus Apple).

---

## 1. Pasang Script ke Google Sheets (Sekali Saja)
1. Buka Google Drive dan buat **Google Spreadsheet (Google Sheets)** baru, beri nama misalnya `Panel Toko Al Ghifari Solution`.
2. Klik menu **Ekstensi (Extensions)** -> **Apps Script**.
3. Hapus seluruh teks bawaan di file `Code.gs`, lalu **salin dan tempel seluruh isi** file [Code.gs](Code.gs).
4. Tekan **Simpan (`Ctrl + S`)**.
5. Kembali ke tab Google Sheets lalu **Muat ulang halaman (`F5`)**. Tunggu ~5 detik hingga muncul menu baru bernama **`⚡ Al Ghifari Panel`** di bar atas.
6. Klik **`⚡ Al Ghifari Panel`** -> **`🚀 Setup Awal (Buat Sheet & Import Katalog)`**.
   - Saat pertama kali berjalan, Google akan meminta izin akses -> pilih akun Google Anda -> klik **Lanjutan (Advanced)** -> **Buka ... (tidak aman)** -> **Izinkan (Allow)**.
   - Script otomatis membuat 6 sheet rapi sekaligus mengimpor seluruh 164 produk, 3 banner hero, dan 3 video dari website Anda!

---

## 2. Hubungkan Google Panel ke Website
1. Di editor **Apps Script**, klik tombol biru **Deploy** (kanan atas) -> **New deployment**.
2. Pada ikon gear **Select type**, pilih **Web app**.
3. Isi pengaturan berikut:
   - **Description**: `Al Ghifari Panel API v1`
   - **Execute as**: `Me (email Anda)`
   - **Who has access**: **`Anyone`** *(wajib Anyone agar website pengunjung dapat membaca data katalog)*
4. Klik **Deploy**, lalu salin **Web app URL** (berakhiran `/exec`).
5. Buka [index.html](../index.html), cari baris:
   ```javascript
   var PANEL_API_URL="";
   ```
   Tempel URL tersebut di dalam tanda kutip, lalu commit & push ke GitHub!

> [!TIP]
> Anda juga bisa menguji URL Panel tanpa mengubah kode lebih dulu dengan membuka link website Anda sambil menambahkan `?panel=URL_WEB_APP_ANDA` di belakang alamat browser!

---

## 3. Cara Pakai Sehari-hari di Google Sheets

### A. Mengganti Flash Sale Hari Ini
- Buka sheet **`Produk`**.
- Centang kolom **`flash_sale`** pada produk yang ingin ditampilkan di barisan Flash Sale.
- Isi kolom **`urutan_flash`** (`1`, `2`, `3`, ...) untuk mengatur urutan tampilnya, dan ubah `terjual_persen` jika ingin menyesuaikan bar terjual.
- **Website otomatis memperbarui Flash Sale** dari centang tersebut!

### B. Penyesuaian Harga Massal per Merk / Kategori
- Klik **`⚡ Al Ghifari Panel`** -> **`💰 Sesuaikan Harga per Merk / Kategori`**.
- Pilih **Merk** (atau `Semua Merk`) dan **Kategori** (`HP`, `Laptop`, `Aksesoris`, atau `Semua Kategori`).
- Pilih mode **Persentase (%)** atau **Nominal Rupiah (Rp)**, lalu isi nilai (misal `-5` untuk diskon turun 5%, atau `200000` untuk naik Rp200.000).
- Pilih pembulatan (mis. `Akhiran 9.000` agar harga rapi seperti `Rp18.999.000`).
- Klik **👁 Preview Dampak** untuk cek contoh sebelum/sesudah, lalu klik **✅ Terapkan Sekarang**. Semua perubahan otomatis tercatat di sheet **`Log_Harga`**.

### C. Menjaga Banner & Gambar Selalu Sesuai yang Dibahas
- Buka sheet **`Banner_Hero`**.
- Pilih nama produk pada kolom **`produk_terkait`** lewat dropdown (terhubung langsung ke daftar nama di sheet `Produk`).
- Website otomatis menampilkan model 3D `.glb` atau foto produk asli dari `produk_terkait` tepat di sebelah teks banner Anda sehingga gambar selalu serasi dengan judul promosinya.
- Jika ingin memakai foto/banner khusus di luar katalog, isi kolom **`gambar_custom`** dengan URL gambar.

### D. Mengganti / Auto-Update Video Trending Sekarang
- **Manual**: Di sheet **`Video_Trending`**, Anda bisa menempel link video `.mp4` atau link **YouTube biasa / YouTube Shorts**. Untuk video YouTube, biarkan kolom `poster_url` kosong jika ingin memakai thumbnail asli YouTube secara otomatis.
  - Centang **`kunci_manual`** bila video tersebut tidak boleh tergantikan saat auto-update berjalan.
- **Otomatis Lintas Merk**:
  - Atur daftar channel resmi brand di sheet **`Sumber_Trending`** (bisa tambah merk baru dengan `Channel ID` `UC...` atau `@handle` YouTube, serta isi `kata_kunci_filter` mis. `Pro,Ultra,AI` jika hanya ingin topik tertentu).
  - Klik **`⚡ Al Ghifari Panel`** -> **`🔄 Update Video Trending Otomatis`** untuk menarik video resmi terbaru dari seluruh merk, atau klik **`⏰ Aktifkan Auto-Update Video Harian (08:00)`** agar terupdate otomatis setiap pagi!
