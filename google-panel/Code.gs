/**
 * ============================================================================
 * AL GHIFARI SOLUTION — GOOGLE PANEL (Google Sheets + Apps Script)
 * ============================================================================
 * Cara pasang:
 * 1. Buka Google Sheets baru -> menu Ekstensi (Extensions) -> Apps Script
 * 2. Hapus kode bawaan, tempel seluruh isi file Code.gs ini, lalu Simpan (Ctrl+S)
 * 3. Muat ulang (F5) Google Sheets -> klik menu "⚡ Al Ghifari Panel"
 * 4. Klik "🚀 Setup Awal (Buat Sheet & Import Katalog)"
 * 5. Deploy -> New deployment -> Web app (Execute as: Me, Who has access: Anyone)
 * 6. Salin URL Web App (/exec) ke variabel PANEL_API_URL di index.html
 * ============================================================================
 */

var SEED_URL = "https://iqbalfirdausriesti.github.io/Al-Ghifari-Solution-/data/catalog-seed.json";

var SHEET_NAMES = {
  PRODUK: "Produk",
  HERO: "Banner_Hero",
  VIDEO: "Video_Trending",
  SUMBER: "Sumber_Trending",
  SETTING: "Pengaturan",
  LOG: "Log_Harga"
};

var DEFAULT_SOURCES = [
  [true, "Apple",    "UCE_M8A5yxnLfW0KghEeajjw", 1, "", "Apple Official YouTube"],
  [true, "Samsung",  "UCWwgaK7x0_FR1goeSRazfsQ", 1, "", "Samsung Global Official"],
  [true, "Xiaomi",   "UCCspJ6mFfCwOV4qFjZWi2wg", 1, "", "Xiaomi Global Official"],
  [true, "OPPO",     "UCJRGO2xgZEoJW5gyEd_RJ2g", 1, "", "OPPO Official"],
  [true, "Google",   "UCIG1k8umaCIIrujZPzZPIMA", 1, "", "Made by Google (Pixel)"],
  [true, "POCO",     "UCLqyjOsn6zS-j5adSd7g-Qg", 1, "", "POCO Global Official"],
  [true, "vivo",     "UCln0gS4LpG4O6zpRaMKV6Sg", 1, "", "vivo Official"],
  [true, "ASUS",     "UCBK_MzhanH8HamrFbABbe8Q", 1, "", "ASUS Official"],
  [true, "Lenovo",   "UCJkBIeTewoQGgtviUe5LH_g", 1, "", "Lenovo Official"],
  [true, "Acer",     "UCrJJLF-MAHn4emWhJls9xaA", 1, "", "Acer Official"],
  [true, "HP",       "UCqcEzOKaA4nc0gISklN0Ryw", 1, "", "HP / OMEN Gaming"],
  [true, "Dell",     "UCQmE9qgzRd2eGqJ1Z2ACl5A", 1, "", "Dell / Alienware Official"],
  [true, "MSI",      "UCezxSW8kVueIU0pr_rukbYA", 1, "", "MSI Gaming Official"],
  [true, "Anker",    "UCv6bA2FHQhi4yzSnDo1TXAg", 1, "", "Anker Official"],
  [true, "Logitech", "UCeQl4-NIFmHUCE_GZ1RTtfA", 1, "", "Logitech Official"]
];

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("⚡ Al Ghifari Panel")
    .addItem("🚀 Setup Awal (Buat Sheet & Import Katalog)", "setupAwal")
    .addSeparator()
    .addItem("💰 Sesuaikan Harga per Merk / Kategori", "bukaDialogHarga")
    .addItem("🔄 Update Video Trending Otomatis", "updateVideoTrendingOtomatis")
    .addSeparator()
    .addItem("⏰ Aktifkan Auto-Update Video Harian (08:00)", "aktifkanTriggerHarian")
    .addItem("⏹ Matikan Auto-Update Video", "matikanTriggerHarian")
    .addSeparator()
    .addItem("🔥 Ringkasan Flash Sale & Statistik", "ringkasanPanel")
    .addItem("🔗 Cara Hubungkan ke Website", "tampilkanPanduanApi")
    .addToUi();
}

/**
 * Mengambil atau membuat sheet dan mengatur gaya header seragam.
 */
function ensureSheet_(ss, name, headers, colWidths) {
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
  }
  sh.clear();
  if (sh.getFilter()) sh.getFilter().remove();

  var headerRange = sh.getRange(1, 1, 1, headers.length);
  headerRange.setValues([headers]);
  headerRange
    .setBackground("#0a1020")
    .setFontColor("#ffffff")
    .setFontWeight("bold")
    .setVerticalAlignment("middle")
    .setHorizontalAlignment("center");
  sh.setRowHeight(1, 32);
  sh.setFrozenRows(1);

  if (colWidths && colWidths.length) {
    for (var i = 0; i < colWidths.length; i++) {
      if (colWidths[i]) sh.setColumnWidth(i + 1, colWidths[i]);
    }
  }
  return sh;
}

/**
 * Setup awal 6 sheet + import seluruh data awal dari GitHub Pages (catalog-seed.json).
 */
function setupAwal() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var ui = SpreadsheetApp.getUi();

  var existing = ss.getSheetByName(SHEET_NAMES.PRODUK);
  if (existing && existing.getLastRow() > 1) {
    var ans = ui.alert(
      "Konfirmasi Setup Ulang",
      "Sheet 'Produk' sudah berisi data (" + (existing.getLastRow() - 1) + " baris).\nMenjalankan Setup Awal akan menimpa sheet Produk, Banner_Hero, Video_Trending, Sumber_Trending, dan Pengaturan dengan data awal website.\n\nLanjutkan?",
      ui.ButtonSet.YES_NO
    );
    if (ans !== ui.Button.YES) return;
  }

  var resp = UrlFetchApp.fetch(SEED_URL, { muteHttpExceptions: true });
  if (resp.getResponseCode() !== 200) {
    ui.alert("Gagal mengambil catalog-seed.json (HTTP " + resp.getResponseCode() + "). Pastikan GitHub Pages aktif.");
    return;
  }
  var seed = JSON.parse(resp.getContentText());

  // 1. Sheet Produk
  var pHeaders = [
    "aktif", "brand", "kategori", "nama",
    "harga_promo", "harga_normal", "diskon_%",
    "flash_sale", "urutan_flash", "terjual_persen",
    "tipe_ikon", "warna_1", "warna_2", "glb_3d",
    "foto_1", "foto_2", "foto_3"
  ];
  var pWidths = [60, 100, 110, 260, 130, 130, 85, 85, 95, 105, 95, 90, 90, 210, 260, 220, 220];
  var shP = ensureSheet_(ss, SHEET_NAMES.PRODUK, pHeaders, pWidths);
  var pRows = (seed.products || []).map(function (p, idx) {
    var rowNum = idx + 2;
    return [
      p.aktif !== false,
      p.brand || "",
      p.kategori || "HP",
      p.nama || "",
      Number(p.harga_promo || 0),
      Number(p.harga_normal || 0),
      "=IF(F" + rowNum + ">0,ROUND((1-E" + rowNum + "/F" + rowNum + ")*100,0),0)",
      !!p.flash_sale,
      p.urutan_flash !== "" && p.urutan_flash !== undefined ? Number(p.urutan_flash) : "",
      p.terjual_persen !== undefined ? Number(p.terjual_persen) : 50,
      p.tipe_ikon || "phone",
      p.warna_1 || "#1c2d4f",
      p.warna_2 || "#4b78ff",
      p.glb_3d || "",
      p.foto_1 || "",
      p.foto_2 || "",
      p.foto_3 || ""
    ];
  });
  if (pRows.length) {
    shP.getRange(2, 1, pRows.length, pHeaders.length).setValues(pRows);
    shP.getRange(2, 1, pRows.length, 1).insertCheckboxes();
    shP.getRange(2, 8, pRows.length, 1).insertCheckboxes();
    shP.getRange(2, 5, pRows.length, 2).setNumberFormat('"Rp"#,##0');
    shP.getRange(2, 7, pRows.length, 1).setNumberFormat('0"%"');
    shP.getRange(2, 10, pRows.length, 1).setNumberFormat('0"%"');
  }
  var maxValRows = Math.max(300, pRows.length + 50);
  var katRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["HP", "Laptop", "Aksesoris", "Tablet", "Wearable", "Audio", "Lainnya"], true)
    .setAllowInvalid(true)
    .build();
  var iconRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["phone", "laptop", "watch", "mouse", "plug", "buds", "bank"], true)
    .setAllowInvalid(true)
    .build();
  shP.getRange(2, 3, maxValRows, 1).setDataValidation(katRule);
  shP.getRange(2, 11, maxValRows, 1).setDataValidation(iconRule);
  shP.getRange(1, 1, Math.max(2, pRows.length + 1), pHeaders.length).createFilter();

  // 2. Sheet Banner_Hero (produk_terkait tervalidasi ke Produk!D2:D)
  var hHeaders = [
    "aktif", "urutan", "label", "judul", "deskripsi",
    "tombol_teks", "tombol_link", "produk_terkait", "gambar_custom", "glb_custom"
  ];
  var hWidths = [60, 70, 170, 260, 320, 150, 150, 240, 220, 200];
  var shH = ensureSheet_(ss, SHEET_NAMES.HERO, hHeaders, hWidths);
  var hRows = (seed.hero || []).map(function (h) {
    return [
      h.aktif !== false,
      Number(h.urutan || 1),
      h.label || "TRENDING SEKARANG",
      h.judul || "",
      h.deskripsi || "",
      h.tombol_teks || "Belanja Sekarang",
      h.tombol_link || "#flash",
      h.produk_terkait || "",
      h.gambar_custom || "",
      h.glb_custom || ""
    ];
  });
  if (hRows.length) {
    shH.getRange(2, 1, hRows.length, hHeaders.length).setValues(hRows);
    shH.getRange(2, 1, hRows.length, 1).insertCheckboxes();
  }
  var prodRefRule = SpreadsheetApp.newDataValidation()
    .requireValueInRange(shP.getRange("D2:D500"), true)
    .setAllowInvalid(true)
    .build();
  shH.getRange(2, 8, 50, 1).setDataValidation(prodRefRule);

  // 3. Sheet Video_Trending
  var vHeaders = [
    "aktif", "urutan", "brand", "judul", "deskripsi",
    "nama_produk_wa", "tipe", "video_url", "poster_url", "kunci_manual", "terakhir_update"
  ];
  var vWidths = [60, 70, 100, 240, 320, 200, 95, 280, 260, 105, 160];
  var shV = ensureSheet_(ss, SHEET_NAMES.VIDEO, vHeaders, vWidths);
  var nowStr = Utilities.formatDate(new Date(), ss.getSpreadsheetTimeZone(), "yyyy-MM-dd HH:mm");
  var vRows = (seed.videos || []).map(function (v) {
    return [
      v.aktif !== false,
      Number(v.urutan || 1),
      v.brand || "",
      v.judul || "",
      v.deskripsi || "",
      v.nama_produk_wa || v.judul || "",
      v.tipe || "mp4",
      v.video_url || "",
      v.poster_url || "",
      v.kunci_manual !== false,
      nowStr
    ];
  });
  if (vRows.length) {
    shV.getRange(2, 1, vRows.length, vHeaders.length).setValues(vRows);
    shV.getRange(2, 1, vRows.length, 1).insertCheckboxes();
    shV.getRange(2, 10, vRows.length, 1).insertCheckboxes();
  }
  var tipeVideoRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["mp4", "youtube"], true)
    .setAllowInvalid(false)
    .build();
  shV.getRange(2, 7, 100, 1).setDataValidation(tipeVideoRule);

  // 4. Sheet Sumber_Trending (Channel YouTube resmi lintas merk)
  var sHeaders = ["aktif", "brand", "channel_id", "max_video", "kata_kunci_filter", "catatan"];
  var sWidths = [60, 110, 240, 95, 190, 220];
  var shS = ensureSheet_(ss, SHEET_NAMES.SUMBER, sHeaders, sWidths);
  shS.getRange(2, 1, DEFAULT_SOURCES.length, sHeaders.length).setValues(DEFAULT_SOURCES);
  shS.getRange(2, 1, DEFAULT_SOURCES.length, 1).insertCheckboxes();

  // 5. Sheet Pengaturan
  var stHeaders = ["kunci", "nilai", "keterangan"];
  var stWidths = [180, 220, 420];
  var shSt = ensureSheet_(ss, SHEET_NAMES.SETTING, stHeaders, stWidths);
  var stRows = [
    ["wa", (seed.settings && seed.settings.wa) || "6281574682460", "Nomor WhatsApp resmi toko (awalan 62 tanpa +)"],
    ["flash_hours", (seed.settings && seed.settings.flashHours) || 6, "Durasi countdown Flash Sale (jam)"],
    ["auto_video_limit", 8, "Jumlah maksimal video otomatis di tab Video Trending"],
    ["catatan_toko", "Semua unit baru & bergaransi resmi Indonesia.", "Catatan opsional toko"]
  ];
  shSt.getRange(2, 1, stRows.length, stHeaders.length).setValues(stRows);

  // 6. Sheet Log_Harga
  var lHeaders = ["waktu", "merk", "kategori", "target", "mode", "nilai", "pembulatan", "jumlah_produk"];
  var lWidths = [160, 120, 120, 160, 100, 110, 130, 120];
  if (!ss.getSheetByName(SHEET_NAMES.LOG)) {
    ensureSheet_(ss, SHEET_NAMES.LOG, lHeaders, lWidths);
  }

  // Hapus Sheet1 bawaan jika kosong dan bukan satu-satunya sheet
  var sheet1 = ss.getSheetByName("Sheet1");
  if (sheet1 && sheet1.getLastRow() === 0 && ss.getSheets().length > 1) {
    ss.deleteSheet(sheet1);
  }
  ss.setActiveSheet(shP);

  ui.alert(
    "Setup Berhasil!",
    "Berhasil membuat 6 sheet Google Panel:\n" +
    "• Produk (" + pRows.length + " produk terimport)\n" +
    "• Banner_Hero (" + hRows.length + " slide)\n" +
    "• Video_Trending (" + vRows.length + " video)\n" +
    "• Sumber_Trending (" + DEFAULT_SOURCES.length + " channel brand)\n" +
    "• Pengaturan & Log_Harga\n\n" +
    "Langkah berikutnya: Deploy sebagai Web App agar website terhubung ke panel ini.",
    ui.ButtonSet.OK
  );
}

/**
 * Helper membaca sheet menjadi array objek berdasarkan header baris 1.
 */
function sheetToObjects_(sh) {
  if (!sh || sh.getLastRow() < 2) return [];
  var data = sh.getDataRange().getValues();
  var headers = data[0].map(function (h) { return String(h).trim(); });
  var rows = [];
  for (var r = 1; r < data.length; r++) {
    var row = data[r];
    var hasAny = false;
    var obj = {};
    for (var c = 0; c < headers.length; c++) {
      if (headers[c]) {
        obj[headers[c]] = row[c];
        if (row[c] !== "" && row[c] !== null && row[c] !== false) hasAny = true;
      }
    }
    if (hasAny) rows.push(obj);
  }
  return rows;
}

function toBool_(v, defVal) {
  if (v === true || v === "TRUE" || v === "true" || v === 1 || v === "1" || v === "YA") return true;
  if (v === false || v === "FALSE" || v === "false" || v === 0 || v === "0" || v === "TIDAK") return false;
  return !!defVal;
}

function extractYouTubeId_(url) {
  if (!url) return "";
  var s = String(url).trim();
  if (/^[a-zA-Z0-9_-]{11}$/.test(s)) return s;
  var m =
    s.match(/[?&]v=([a-zA-Z0-9_-]{11})/) ||
    s.match(/youtu\.be\/([a-zA-Z0-9_-]{11})/) ||
    s.match(/youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})/) ||
    s.match(/youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/);
  return m ? m[1] : "";
}

/**
 * Web App Endpoint GET -> Dibaca oleh website (index.html).
 * Gunakan fetch(PANEL_API_URL) polos di browser agar bebas preflight CORS.
 */
function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  // Pengaturan
  var stRows = sheetToObjects_(ss.getSheetByName(SHEET_NAMES.SETTING));
  var settings = { wa: "6281574682460", flashHours: 6 };
  stRows.forEach(function (r) {
    var k = String(r.kunci || "").trim();
    if (k === "wa" && r.nilai) settings.wa = String(r.nilai).trim();
    if (k === "flash_hours" && r.nilai) settings.flashHours = Number(r.nilai) || 6;
    if (k === "auto_video_limit" && r.nilai) settings.autoVideoLimit = Number(r.nilai) || 8;
  });

  // Produk
  var pRows = sheetToObjects_(ss.getSheetByName(SHEET_NAMES.PRODUK));
  var products = [];
  pRows.forEach(function (r) {
    if (!toBool_(r.aktif, true)) return;
    if (!r.nama) return;
    var pr = Number(r.harga_promo) || 0;
    var o = Number(r.harga_normal) || pr;
    if (pr <= 0) return;
    if (o < pr) o = pr;
    var im = [];
    [r.foto_1, r.foto_2, r.foto_3].forEach(function (u) {
      var s = String(u || "").trim();
      if (s) im.push(s);
    });
    var item = {
      n: String(r.nama).trim(),
      c: String(r.kategori || "HP").trim(),
      pr: pr,
      o: o,
      t: String(r.tipe_ikon || "phone").trim(),
      col: [String(r.warna_1 || "#1c2d4f").trim(), String(r.warna_2 || "#4b78ff").trim()],
      b: String(r.brand || "").trim(),
      im: im
    };
    if (String(r.glb_3d || "").trim()) item.glb = String(r.glb_3d).trim();
    if (toBool_(r.flash_sale, false)) {
      item.fs = true;
      item.fsOrder = r.urutan_flash !== "" && r.urutan_flash !== null ? Number(r.urutan_flash) : 999;
    }
    if (r.terjual_persen !== "" && r.terjual_persen !== null && !isNaN(Number(r.terjual_persen))) {
      item.sold = Math.max(1, Math.min(99, Number(r.terjual_persen)));
    }
    products.push(item);
  });

  // Banner Hero
  var hRows = sheetToObjects_(ss.getSheetByName(SHEET_NAMES.HERO));
  var hero = hRows
    .filter(function (r) { return toBool_(r.aktif, true) && String(r.judul || "").trim(); })
    .sort(function (a, b) { return (Number(a.urutan) || 999) - (Number(b.urutan) || 999); })
    .map(function (r) {
      return {
        label: String(r.label || "TRENDING SEKARANG").trim(),
        judul: String(r.judul || "").trim(),
        deskripsi: String(r.deskripsi || "").trim(),
        tombol_teks: String(r.tombol_teks || "Belanja Sekarang").trim(),
        tombol_link: String(r.tombol_link || "#flash").trim(),
        produk_terkait: String(r.produk_terkait || "").trim(),
        gambar_custom: String(r.gambar_custom || "").trim(),
        glb_custom: String(r.glb_custom || "").trim()
      };
    });

  // Video Trending
  var vRows = sheetToObjects_(ss.getSheetByName(SHEET_NAMES.VIDEO));
  var videos = vRows
    .filter(function (r) { return toBool_(r.aktif, true) && String(r.judul || "").trim(); })
    .sort(function (a, b) { return (Number(a.urutan) || 999) - (Number(b.urutan) || 999); })
    .map(function (r) {
      var videoUrl = String(r.video_url || "").trim();
      var tipeRaw = String(r.tipe || "").trim().toLowerCase();
      var ytId = extractYouTubeId_(videoUrl);
      var tipe = tipeRaw === "youtube" || (ytId && tipeRaw !== "mp4") ? "youtube" : "mp4";
      var poster = String(r.poster_url || "").trim();
      if (!poster && ytId) poster = "https://i.ytimg.com/vi/" + ytId + "/hqdefault.jpg";
      return {
        brand: String(r.brand || "").trim().toUpperCase(),
        t: String(r.judul || "").trim(),
        p: String(r.deskripsi || "").trim(),
        q: String(r.nama_produk_wa || r.judul || "").trim(),
        tipe: tipe,
        url: videoUrl,
        ytId: ytId,
        poster: poster
      };
    });

  var payload = {
    ok: true,
    updatedAt: new Date().toISOString(),
    settings: settings,
    hero: hero,
    videos: videos,
    products: products
  };

  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

/* ============================================================================
 * TOOL 1: PENYESUAIAN HARGA MASSAL PER MERK & KATEGORI
 * ============================================================================ */

function bukaDialogHarga() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss.getSheetByName(SHEET_NAMES.PRODUK)) {
    SpreadsheetApp.getUi().alert("Sheet 'Produk' belum ada. Jalankan 'Setup Awal' terlebih dahulu.");
    return;
  }
  var html = HtmlService.createHtmlOutput(buildHargaDialogHtml_())
    .setWidth(470)
    .setHeight(530);
  SpreadsheetApp.getUi().showModalDialog(html, "💰 Penyesuaian Harga Massal per Merk / Kategori");
}

function dapatkanOpsiHarga() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var rows = sheetToObjects_(ss.getSheetByName(SHEET_NAMES.PRODUK));
  var brands = {};
  var cats = {};
  rows.forEach(function (r) {
    if (r.brand) brands[String(r.brand).trim()] = true;
    if (r.kategori) cats[String(r.kategori).trim()] = true;
  });
  return {
    brands: Object.keys(brands).sort(),
    categories: Object.keys(cats).sort(),
    totalProducts: rows.length
  };
}

function bulatkanHarga_(val, roundingMode) {
  if (val <= 0) return 0;
  var r = String(roundingMode || "1000");
  if (r === "9000") {
    var base = Math.round(val / 10000) * 10000;
    return Math.max(9000, base - 1000);
  }
  var step = Number(r) || 1000;
  return Math.max(step, Math.round(val / step) * step);
}

function terapkanPenyesuaianHarga(cfg) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAMES.PRODUK);
  if (!sh || sh.getLastRow() < 2) {
    return { ok: false, message: "Data produk kosong." };
  }

  var nilai = Number(cfg.nilai);
  if (isNaN(nilai) || nilai === 0) {
    return { ok: false, message: "Masukkan angka perubahan harga selain 0 (contoh: -5 untuk turun 5%, atau 250000 untuk naik Rp250.000)." };
  }

  var range = sh.getDataRange();
  var data = range.getValues();
  var headers = data[0].map(function (h) { return String(h).trim(); });
  var iBrand = headers.indexOf("brand");
  var iKat = headers.indexOf("kategori");
  var iNama = headers.indexOf("nama");
  var iPr = headers.indexOf("harga_promo");
  var iO = headers.indexOf("harga_normal");

  var affected = 0;
  var samples = [];
  var changedPrValues = [];
  var changedOValues = [];

  for (var r = 1; r < data.length; r++) {
    var b = String(data[r][iBrand] || "").trim();
    var c = String(data[r][iKat] || "").trim();
    var prOld = Number(data[r][iPr]) || 0;
    var oOld = Number(data[r][iO]) || 0;

    var matchBrand = cfg.brand === "ALL" || b === cfg.brand;
    var matchCat = cfg.kategori === "ALL" || c === cfg.kategori;

    var prNew = prOld;
    var oNew = oOld;

    if (matchBrand && matchCat && (prOld > 0 || oOld > 0)) {
      affected++;
      if (cfg.target === "both" || cfg.target === "promo") {
        var rawPr = cfg.mode === "percent" ? prOld * (1 + nilai / 100) : prOld + nilai;
        prNew = bulatkanHarga_(rawPr, cfg.pembulatan);
      }
      if (cfg.target === "both" || cfg.target === "normal") {
        var rawO = cfg.mode === "percent" ? oOld * (1 + nilai / 100) : oOld + nilai;
        oNew = bulatkanHarga_(rawO, cfg.pembulatan);
      }
      if (oNew < prNew) oNew = prNew;

      if (samples.length < 5) {
        samples.push({
          nama: String(data[r][iNama] || ""),
          prOld: prOld,
          prNew: prNew,
          oOld: oOld,
          oNew: oNew
        });
      }
    }
    changedPrValues.push([prNew]);
    changedOValues.push([oNew]);
  }

  if (affected === 0) {
    return { ok: false, message: "Tidak ada produk yang cocok dengan filter Merk & Kategori tersebut." };
  }

  if (!cfg.preview) {
    if (cfg.target === "both" || cfg.target === "promo") {
      sh.getRange(2, iPr + 1, changedPrValues.length, 1).setValues(changedPrValues);
    }
    if (cfg.target === "both" || cfg.target === "normal") {
      sh.getRange(2, iO + 1, changedOValues.length, 1).setValues(changedOValues);
    }

    var shLog = ss.getSheetByName(SHEET_NAMES.LOG);
    if (!shLog) {
      shLog = ensureSheet_(ss, SHEET_NAMES.LOG, ["waktu", "merk", "kategori", "target", "mode", "nilai", "pembulatan", "jumlah_produk"], [160, 120, 120, 160, 100, 110, 130, 120]);
    }
    var nowStr = Utilities.formatDate(new Date(), ss.getSpreadsheetTimeZone(), "yyyy-MM-dd HH:mm:ss");
    shLog.appendRow([nowStr, cfg.brand, cfg.kategori, cfg.target, cfg.mode, nilai, cfg.pembulatan, affected]);
  }

  return {
    ok: true,
    preview: !!cfg.preview,
    affected: affected,
    samples: samples
  };
}

function buildHargaDialogHtml_() {
  return [
    '<!DOCTYPE html><html><head><base target="_top"><style>',
    'body{font-family:Inter,Arial,sans-serif;background:#0a1020;color:#eef3ff;margin:0;padding:16px;font-size:13px}',
    'h3{margin:0 0 12px;color:#d8b46a;font-size:15px}',
    '.g{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px}',
    'label{display:block;font-size:11px;color:#9eb0d6;margin-bottom:4px;font-weight:600}',
    'select,input{width:100%;box-sizing:border-box;padding:8px 10px;border-radius:8px;border:1px solid #2b3f70;background:#111a30;color:#fff;font-size:13px}',
    '.hint{font-size:11px;color:#9eb0d6;margin:4px 0 12px}',
    '.btns{display:flex;gap:8px;margin-top:8px}',
    'button{flex:1;padding:10px;border-radius:9px;border:0;font-weight:700;cursor:pointer;font-size:13px}',
    '.b1{background:#1c2d56;color:#dbe8ff;border:1px solid #4b78ff66}',
    '.b2{background:linear-gradient(135deg,#4b78ff,#2a54d6);color:#fff}',
    'button:disabled{opacity:.5;cursor:wait}',
    '#out{margin-top:12px;background:#111a30;border:1px solid #263963;border-radius:10px;padding:10px;font-size:12px;max-height:175px;overflow:auto;display:none}',
    '.ok{color:#5ee8a0;font-weight:700}.err{color:#ff7b7b;font-weight:700}',
    'table{width:100%;border-collapse:collapse;margin-top:6px;font-size:11px}',
    'td,th{text-align:left;padding:4px 5px;border-bottom:1px solid #ffffff14}',
    '</style></head><body>',
    '<h3>Atur Harga Massal (Merk & Kategori)</h3>',
    '<div class="g"><div><label>Pilih Merk</label><select id="brand"><option value="ALL">Semua Merk</option></select></div>',
    '<div><label>Pilih Kategori</label><select id="kat"><option value="ALL">Semua Kategori</option></select></div></div>',
    '<div class="g"><div><label>Kolom Harga</label><select id="target"><option value="both">Harga Promo & Normal</option><option value="promo">Hanya Harga Promo</option><option value="normal">Hanya Harga Normal</option></select></div>',
    '<div><label>Mode Perubahan</label><select id="mode"><option value="percent">Persentase (%)</option><option value="nominal">Nominal Rupiah (Rp)</option></select></div></div>',
    '<div class="g"><div><label>Nilai (+ naik, − turun)</label><input id="nilai" type="number" placeholder="Contoh: -5 atau 250000"></div>',
    '<div><label>Pembulatan</label><select id="bulat"><option value="1000">Rp1.000 terdekat</option><option value="10000">Rp10.000 terdekat</option><option value="50000">Rp50.000 terdekat</option><option value="100000">Rp100.000 terdekat</option><option value="9000">Akhiran 9.000 (cth: ...99.000)</option></select></div></div>',
    '<div class="hint">Tips: Isi <b>-5</b> pada mode Persen untuk menurunkan harga 5%, atau <b>100000</b> pada mode Nominal untuk menaikkan Rp100.000.</div>',
    '<div class="btns"><button class="b1" id="btnPrev" onclick="run(true)">👁 Preview Dampak</button><button class="b2" id="btnApply" onclick="run(false)">✅ Terapkan Sekarang</button></div>',
    '<div id="out"></div>',
    '<script>',
    'function rp(n){return "Rp"+Number(n||0).toLocaleString("id-ID")}',
    'google.script.run.withSuccessHandler(function(d){',
    ' var sb=document.getElementById("brand"),sk=document.getElementById("kat");',
    ' (d.brands||[]).forEach(function(b){var o=document.createElement("option");o.value=b;o.textContent=b;sb.appendChild(o)});',
    ' (d.categories||[]).forEach(function(c){var o=document.createElement("option");o.value=c;o.textContent=c;sk.appendChild(o)});',
    '}).dapatkanOpsiHarga();',
    'function run(preview){',
    ' var cfg={brand:brand.value,kategori:kat.value,target:target.value,mode:mode.value,nilai:nilai.value,pembulatan:bulat.value,preview:preview};',
    ' if(!preview && !confirm("Terapkan perubahan harga pada produk terpilih?"))return;',
    ' btnPrev.disabled=btnApply.disabled=true;',
    ' out.style.display="block";out.innerHTML="Memproses...";',
    ' google.script.run.withSuccessHandler(function(res){',
    '  btnPrev.disabled=btnApply.disabled=false;',
    '  if(!res.ok){out.innerHTML="<span class=err>"+res.message+"</span>";return}',
    '  var h="<span class=ok>"+(res.preview?"Preview: ":"Selesai! ")+res.affected+" produk terdampak.</span>";',
    '  h+="<table><tr><th>Produk</th><th>Promo Lama → Baru</th></tr>";',
    '  res.samples.forEach(function(s){h+="<tr><td>"+s.nama+"</td><td>"+rp(s.prOld)+" → <b>"+rp(s.prNew)+"</b></td></tr>"});',
    '  out.innerHTML=h+"</table>";',
    ' }).withFailureHandler(function(e){btnPrev.disabled=btnApply.disabled=false;out.innerHTML="<span class=err>"+e.message+"</span>"}).terapkanPenyesuaianHarga(cfg);',
    '}',
    '</script></body></html>'
  ].join("");
}

/* ============================================================================
 * TOOL 2: AUTO-UPDATE VIDEO TRENDING LINTAS MERK (YOUTUBE RSS PUBLIK)
 * ============================================================================ */

function resolveChannelIdIfHandle_(raw) {
  var s = String(raw || "").trim();
  if (!s) return "";
  if (/^UC[a-zA-Z0-9_-]{20,}$/.test(s)) return s;
  var url = s.indexOf("http") === 0 ? s : "https://www.youtube.com/" + (s.indexOf("@") === 0 ? s : "@" + s);
  try {
    var r = UrlFetchApp.fetch(url, { muteHttpExceptions: true, followRedirects: true });
    if (r.getResponseCode() !== 200) return "";
    var html = r.getContentText();
    var m = html.match(/"channelId":"(UC[a-zA-Z0-9_-]{22})"/) || html.match(/channel_id=(UC[a-zA-Z0-9_-]{22})/);
    return m ? m[1] : "";
  } catch (e) {
    return "";
  }
}

function updateVideoTrendingOtomatis(silent) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var shSrc = ss.getSheetByName(SHEET_NAMES.SUMBER);
  var shVid = ss.getSheetByName(SHEET_NAMES.VIDEO);
  if (!shSrc || !shVid) {
    if (!silent) SpreadsheetApp.getUi().alert("Jalankan 'Setup Awal' terlebih dahulu.");
    return;
  }

  // Ambil batas max video dari sheet Pengaturan
  var maxLimit = 8;
  sheetToObjects_(ss.getSheetByName(SHEET_NAMES.SETTING)).forEach(function (r) {
    if (String(r.kunci).trim() === "auto_video_limit" && Number(r.nilai) > 0) {
      maxLimit = Number(r.nilai);
    }
  });

  // Pertahankan video yang ditandai kunci_manual = TRUE
  var existingVideos = sheetToObjects_(shVid);
  var lockedRows = [];
  existingVideos.forEach(function (v) {
    if (toBool_(v.kunci_manual, false) && String(v.judul || "").trim()) {
      lockedRows.push([
        toBool_(v.aktif, true),
        Number(v.urutan || 1),
        String(v.brand || "").trim().toUpperCase(),
        String(v.judul || "").trim(),
        String(v.deskripsi || "").trim(),
        String(v.nama_produk_wa || v.judul || "").trim(),
        String(v.tipe || "mp4").trim(),
        String(v.video_url || "").trim(),
        String(v.poster_url || "").trim(),
        true,
        v.terakhir_update || ""
      ]);
    }
  });

  var sources = sheetToObjects_(shSrc);
  var fetched = [];
  var atomNs = XmlService.getNamespace("http://www.w3.org/2005/Atom");
  var ytNs = XmlService.getNamespace("yt", "http://www.youtube.com/xml/schemas/2015");
  var nowStr = Utilities.formatDate(new Date(), ss.getSpreadsheetTimeZone(), "yyyy-MM-dd HH:mm");

  sources.forEach(function (src) {
    if (!toBool_(src.aktif, true)) return;
    var brand = String(src.brand || "").trim().toUpperCase();
    var cid = resolveChannelIdIfHandle_(src.channel_id);
    if (!cid) return;

    var perBrandMax = Math.max(1, Number(src.max_video) || 1);
    var kwRaw = String(src.kata_kunci_filter || "").trim();
    var kws = kwRaw ? kwRaw.toLowerCase().split(",").map(function (x) { return x.trim(); }).filter(Boolean) : [];

    try {
      var rssUrl = "https://www.youtube.com/feeds/videos.xml?channel_id=" + encodeURIComponent(cid);
      var res = UrlFetchApp.fetch(rssUrl, { muteHttpExceptions: true });
      if (res.getResponseCode() !== 200) return;

      var doc = XmlService.parse(res.getContentText());
      var entries = doc.getRootElement().getChildren("entry", atomNs);
      var taken = 0;

      for (var i = 0; i < entries.length && taken < perBrandMax; i++) {
        var entry = entries[i];
        var vidIdEl = entry.getChild("videoId", ytNs);
        var titleEl = entry.getChild("title", atomNs);
        var pubEl = entry.getChild("published", atomNs);
        if (!vidIdEl || !titleEl) continue;

        var vidId = vidIdEl.getText().trim();
        var title = titleEl.getText().trim();
        var pub = pubEl ? pubEl.getText().trim() : "";

        if (kws.length) {
          var tLow = title.toLowerCase();
          var matched = kws.some(function (k) { return tLow.indexOf(k) >= 0; });
          if (!matched) continue;
        }

        fetched.push({
          pubTs: pub ? new Date(pub).getTime() : 0,
          brand: brand,
          title: title,
          vidId: vidId,
          url: "https://www.youtube.com/watch?v=" + vidId,
          poster: "https://i.ytimg.com/vi/" + vidId + "/hqdefault.jpg"
        });
        taken++;
      }
    } catch (err) {
      Logger.log("Gagal fetch RSS " + brand + ": " + err);
    }
  });

  // Urutkan dari video terbaru
  fetched.sort(function (a, b) { return b.pubTs - a.pubTs; });
  var autoCount = Math.max(0, maxLimit);
  var sliced = fetched.slice(0, autoCount);

  var nextOrder = lockedRows.length + 1;
  var autoRows = sliced.map(function (v, idx) {
    return [
      true,
      nextOrder + idx,
      v.brand,
      v.title,
      "Rilis resmi & trending terbaru dari " + v.brand + ": " + v.title + ". Tanya ketersediaan unit & harga promo di Al Ghifari Solution.",
      v.brand + " - " + v.title,
      "youtube",
      v.url,
      v.poster,
      false,
      nowStr
    ];
  });

  var allRows = lockedRows.concat(autoRows);
  var headers = [
    "aktif", "urutan", "brand", "judul", "deskripsi",
    "nama_produk_wa", "tipe", "video_url", "poster_url", "kunci_manual", "terakhir_update"
  ];
  var vWidths = [60, 70, 100, 240, 320, 200, 95, 280, 260, 105, 160];
  shVid = ensureSheet_(ss, SHEET_NAMES.VIDEO, headers, vWidths);
  if (allRows.length) {
    shVid.getRange(2, 1, allRows.length, headers.length).setValues(allRows);
    shVid.getRange(2, 1, allRows.length, 1).insertCheckboxes();
    shVid.getRange(2, 10, allRows.length, 1).insertCheckboxes();
  }
  var tipeVideoRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["mp4", "youtube"], true)
    .setAllowInvalid(false)
    .build();
  shVid.getRange(2, 7, 100, 1).setDataValidation(tipeVideoRule);

  if (!silent) {
    SpreadsheetApp.getUi().alert(
      "Update Video Trending Selesai!",
      "Berhasil mengambil " + autoRows.length + " video terbaru lintas merk resmi.\n" +
      "Video manual yang dikunci tetap dipertahankan (" + lockedRows.length + " video).",
      SpreadsheetApp.getUi().ButtonSet.OK
    );
  }
}

function aktifkanTriggerHarian() {
  matikanTriggerHarian(true);
  ScriptApp.newTrigger("updateVideoTrendingOtomatis")
    .timeBased()
    .everyDays(1)
    .atHour(8)
    .create();
  SpreadsheetApp.getUi().alert("Auto-Update Aktif!", "Google Panel akan memperbarui Video Trending otomatis setiap hari sekitar pukul 08:00.");
}

function matikanTriggerHarian(silent) {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === "updateVideoTrendingOtomatis") {
      ScriptApp.deleteTrigger(t);
    }
  });
  if (!silent) {
    SpreadsheetApp.getUi().alert("Auto-Update Dimatikan.", "Jadwal harian video otomatis telah dihapus.");
  }
}

function ringkasanPanel() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var products = sheetToObjects_(ss.getSheetByName(SHEET_NAMES.PRODUK));
  var aktif = products.filter(function (p) { return toBool_(p.aktif, true); });
  var fs = aktif.filter(function (p) { return toBool_(p.flash_sale, false); });
  var hero = sheetToObjects_(ss.getSheetByName(SHEET_NAMES.HERO)).filter(function (h) { return toBool_(h.aktif, true); });
  var vids = sheetToObjects_(ss.getSheetByName(SHEET_NAMES.VIDEO)).filter(function (v) { return toBool_(v.aktif, true); });

  var byCat = {};
  aktif.forEach(function (p) {
    var k = String(p.kategori || "Lainnya");
    byCat[k] = (byCat[k] || 0) + 1;
  });
  var catLines = Object.keys(byCat).map(function (k) { return "  • " + k + ": " + byCat[k] + " produk"; }).join("\n");

  SpreadsheetApp.getUi().alert(
    "Ringkasan Al Ghifari Panel",
    "Total Produk Aktif: " + aktif.length + " dari " + products.length + " baris\n" +
    catLines + "\n\n" +
    "🔥 Flash Sale Aktif: " + fs.length + " produk\n" +
    "🖼 Banner Hero Aktif: " + hero.length + " slide\n" +
    "🎬 Video Trending Aktif: " + vids.length + " video",
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

function tampilkanPanduanApi() {
  var serviceUrl = "";
  try { serviceUrl = ScriptApp.getService().getUrl() || ""; } catch (e) {}
  var msg = serviceUrl
    ? "URL Web App terdeteksi:\n" + serviceUrl + "\n\nSalin URL di atas ke variabel PANEL_API_URL di dalam file index.html."
    : "Belum di-deploy sebagai Web App.\n\nLangkah cepat:\n1. Klik Deploy -> New deployment\n2. Pilih Type: Web app\n3. Execute as: Me | Who has access: Anyone\n4. Klik Deploy, salin URL Web App (/exec)\n5. Tempel URL tersebut ke variabel PANEL_API_URL di index.html.";
  SpreadsheetApp.getUi().alert("Hubungkan Google Panel ke Website", msg, SpreadsheetApp.getUi().ButtonSet.OK);
}
