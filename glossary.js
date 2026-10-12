// glossary.js - Kamus Istilah Saham untuk WPscanner v4.2
// Dipanggil oleh app.js untuk menampilkan tooltip edukasi

const GLOSSARY = {
    // === VALUASI ===
    pbv: {
        term: "PBV",
        full: "Price to Book Value",
        id: "Harga terhadap Nilai Buku",
        desc: "Perbandingan harga saham dengan nilai aset bersih (ekuitas) perusahaan. Mengukur seberapa 'mahal' atau 'murah' sebuah saham relatif terhadap kekayaan bersihnya.",
        how: "Rumus: Harga Saham ÷ Nilai Buku per Saham",
        guide: "PBV < 0.7x = Sangat Murah | 0.7-0.9x = Murah | 0.9-1.2x = Wajar | 1.2-1.5x = Agak Mahal | > 1.5x = Mahal"
    },
    
    per: {
        term: "PER",
        full: "Price to Earnings Ratio",
        id: "Harga terhadap Laba",
        desc: "Berapa tahun waktu yang dibutuhkan untuk mengembalikan modal investasi dari laba perusahaan. Mengukur kemahalan saham relatif terhadap profitabilitasnya.",
        how: "Rumus: Harga Saham ÷ Laba per Saham (EPS)",
        guide: "PER < 10x = Murah | 10-15x = Wajar | 15-20x = Agak Mahal | > 20x = Mahal"
    },

    // === DIVIDEN ===
    dividend_yield: {
        term: "Dividend Yield",
        full: "Imbal Hasil Dividen",
        id: "Persentase Dividen terhadap Harga",
        desc: "Persentase pengembalian investasi dari dividen tahunan relatif terhadap harga saham. Seperti 'uang sewa' yang Anda terima dari memegang saham.",
        how: "Rumus: (Dividen per Lembar ÷ Harga Saham) × 100%",
        guide: "Yield > 7% = Tinggi | 5-7% = Menengah | 3-5% = Rendah | < 3% = Sangat Rendah"
    },

    dps: {
        term: "DPS",
        full: "Dividend Per Share",
        id: "Dividen per Lembar Saham",
        desc: "Besaran nominal rupiah dividen yang dibagikan perusahaan untuk setiap 1 lembar saham yang Anda miliki.",
        how: "Rumus: Total Dividen Dibagikan ÷ Jumlah Saham Beredar",
        guide: "Semakin konsisten DPS naik tiap tahun, semakin sehat kebijakan dividen perusahaan."
    },

    payout_ratio: {
        term: "Payout Ratio",
        full: "Rasio Pembagian Laba",
        id: "Persentase Laba yang Dibagi sebagai Dividen",
        desc: "Seberapa besar porsi laba bersih perusahaan yang dibagikan ke pemegang saham sebagai dividen. Sisa laba ditahan untuk ekspansi bisnis.",
        how: "Rumus: (Total Dividen ÷ Laba Bersih) × 100%",
        guide: "20-50% = Konservatif (banyak ditahan untuk tumbuh) | 50-80% = Sehat & Seimbang | > 80% = Agresif (risiko dipotong)"
    },

    // === HARGA & TARGET ===
    buy_zone: {
        term: "Area Beli Ideal",
        full: "Berdasarkan 52-Week Low",
        id: "Zona Harga Terbaik untuk Membeli",
        desc: "Area harga di mana saham secara historis sering memantul naik. Dihitung dari harga terendah 1 tahun terakhir (52-Week Low) ditambah buffer 5%.",
        how: "Rumus: 52-Week Low × 1.05",
        guide: "Beli di area ini = beli di 'diskon' dengan risiko turun lebih lanjut yang minim."
    },

    target_sell: {
        term: "Target Jual",
        full: "Berdasarkan Re-rating Valuasi",
        id: "Harga Jual yang Ditargetkan",
        desc: "Harga target jika pasar melakukan 're-rating' (penilaian ulang) dan menghargai saham ke level valuasi wajar (PBV 1.2x).",
        how: "Rumus: Harga Saat Ini × (Target PBV 1.2 ÷ PBV Saat Ini)",
        guide: "Target ini realistis untuk hold 6-12 bulan pada saham Big Caps yang solid."
    },

    capital_gain: {
        term: "Capital Gain",
        full: "Keuntungan Modal",
        id: "Persentase Kenaikan Harga dari Beli ke Jual",
        desc: "Selisih keuntungan dari selisih harga jual dan harga beli. Dihitung dari Area Beli Ideal ke Target Jual (bukan dari harga saat ini).",
        how: "Rumus: ((Target Jual - Area Beli) ÷ Area Beli) × 100%",
        guide: "Gain > 50% = Sangat Menarik | 25-50% = Menarik | 10-25% = Moderat | < 10% = Rendah"
    },

    stop_loss: {
        term: "Stop Loss",
        full: "Batasi Kerugian",
        id: "Batas Harga untuk Cut Loss",
        desc: "Harga batas di mana Anda harus menjual saham untuk membatasi kerugian. Mencegah kerugian kecil berubah menjadi bencana besar.",
        how: "Rumus: Harga Saat Ini × 0.85 (cut loss 15%)",
        guide: "Disiplin cut loss adalah kunci survival jangka panjang di pasar saham."
    },

    // === FUNDAMENTAL LAIN ===
    der: {
        term: "DER",
        full: "Debt to Equity Ratio",
        id: "Rasio Utang terhadap Ekuitas",
        desc: "Mengukur seberapa besar perusahaan dibiayai oleh utang dibandingkan modal sendiri. DER tinggi = risiko finansial lebih besar.",
        how: "Rumus: Total Utang  Total Ekuitas",
        guide: "DER < 50% = Sangat Aman | 50-100% = Aman | 100-150% = Waspada | > 150% = Berisiko Tinggi",
        note: "Pengecualian: Sektor perbankan WAJIB memiliki DER tinggi karena dana nasabah dicatat sebagai utang."
    },

    market_cap: {
        term: "Market Cap",
        full: "Market Capitalization",
        id: "Kapitalisasi Pasar",
        desc: "Total nilai perusahaan di pasar saham. Mengukur seberapa 'besar' sebuah perusahaan.",
        how: "Rumus: Harga Saham × Jumlah Saham Beredar",
        guide: "> Rp 40T = Mega Cap | Rp 10-40T = Large Cap | Rp 1-10T = Mid Cap | < Rp 1T = Small Cap"
    },

    earnings_growth: {
        term: "Earnings Growth",
        full: "Pertumbuhan Laba",
        id: "Persentase Kenaikan/Turunan Laba Tahunan",
        desc: "Seberapa cepat laba perusahaan tumbuh (atau menyusut) dibandingkan tahun sebelumnya. Indikator kesehatan bisnis.",
        how: "Rumus: ((Laba Tahun Ini - Laba Tahun Lalu) ÷ Laba Tahun Lalu) × 100%",
        guide: "> 15% = Tumbuh Cepat | 5-15% = Tumbuh Stabil | 0-5% = Stagnan | Negatif = Menurun"
    },

    // === TEKNIKAL ===
    sma: {
        term: "SMA",
        full: "Simple Moving Average",
        id: "Rata-rata Pergerakan Harga Sederhana",
        desc: "Rata-rata harga saham dalam periode waktu tertentu. Digunakan untuk mengidentifikasi tren dan area support/resistance.",
        how: "Rumus: Jumlahkan harga penutupan N hari ÷ N",
        guide: "SMA 20 Mingguan = rata-rata harga 20 minggu terakhir. Harga di atas SMA = tren naik, di bawah = tren turun."
    },

    accumulation: {
        term: "Akumulasi",
        full: "Fase Akumulasi Institusi",
        id: "Tahap Pencicilan Beli oleh Pemain Besar",
        desc: "Fase di mana institusi/bandar mencicil membeli saham dalam jumlah besar secara diam-diam, biasanya saat harga sideways di area support.",
        how: "Deteksi: Harga stabil di sekitar SMA 20W + Volume 4 minggu > 1.15x Volume 20 minggu",
        guide: "Akumulasi biasanya berlangsung 3-6 bulan sebelum harga naik signifikan (fase markup)."
    },

    re_rating: {
        term: "Re-rating",
        full: "Penilaian Ulang Valuasi",
        id: "Proses Pasar Menghargai Kembali Saham",
        desc: "Ketika pasar mengubah persepsi terhadap sebuah saham dan menaikkan valuasinya (misal dari PBV 0.7x ke 1.2x). Ini sumber utama capital gain besar.",
        how: "Pemicu: Perbaikan fundamental, sentimen positif, atau masuknya dana institusi besar",
        guide: "Re-rating dari PBV 0.6x ke 1.2x = kenaikan harga 100% (uang jadi 2x lipat)."
    },

    // === KATEGORI VALUASI ===
    valuation_deep_value: {
        term: "Sangat Murah",
        full: "Deep Value",
        id: "Saham Dijual Jauh di Bawah Nilai Wajar",
        desc: "Saham dengan PBV < 0.7x. Potensi gain sangat besar jika pasar melakukan re-rating, tapi bisa juga value trap (murah karena fundamental rusak).",
        guide: "Cek fundamental dengan teliti: laba harus positif, dividen konsisten, utang terkendali."
    },

    valuation_undervalued: {
        term: "Murah",
        full: "Undervalued",
        id: "Saham Dijual di Bawah Nilai Wajar",
        desc: "Saham dengan PBV 0.7x - 0.9x. Zona ideal untuk akumulasi dengan margin of safety yang baik.",
        guide: "Ini adalah sweet spot strategi WPscanner — murah tapi tidak terlalu berisiko."
    },

    valuation_fair: {
        term: "Wajar",
        full: "Fair Value",
        id: "Saham Dihargai Sesuai Nilai Wajarnya",
        desc: "Saham dengan PBV 0.9x - 1.2x. Tidak ada diskon signifikan, tapi juga tidak mahal. Cocok untuk hold jangka panjang dengan dividen.",
        guide: "Capital gain dari re-rating terbatas, tapi dividen yield biasanya masih menarik."
    },

    valuation_slightly_over: {
        term: "Agak Mahal",
        full: "Slightly Overvalued",
        id: "Saham Sedikit di Atas Nilai Wajar",
        desc: "Saham dengan PBV 1.2x - 1.5x. Pasar sudah menghargai dengan premium. Upside terbatas, downside risiko lebih besar.",
        guide: "Hindari akumulasi baru. Tunggu koreksi atau fokus pada saham lain yang lebih murah."
    },

    valuation_overvalued: {
        term: "Mahal",
        full: "Overvalued",
        id: "Saham Dijual di Atas Nilai Wajar",
        desc: "Saham dengan PBV > 1.5x. Harga sudah jauh melampaui nilai buku. Risiko koreksi tinggi jika sentimen berubah.",
        guide: "Bukan zona beli untuk strategi deep value. Pertimbangkan take profit jika sudah hold."
    }
};

// Fungsi helper untuk generate HTML tooltip dari glossary
function getTooltipHTML(key) {
    const item = GLOSSARY[key];
    if (!item) return '';
    
    let html = `<b>${item.term}</b> <span style="opacity:0.7;font-size:0.72rem;">(${item.full})</span><br>`;
    html += `<i style="font-size:0.72rem;color:#ffd700;">${item.id}</i><br><br>`;
    html += `<span style="font-size:0.75rem;">${item.desc}</span><br><br>`;
    
    if (item.how) {
        html += `<b style="color:#90ee90;font-size:0.75rem;">📐 Cara Hitung:</b><br><span style="font-size:0.72rem;">${item.how}</span><br><br>`;
    }
    
    if (item.guide) {
        html += `<b style="color:#87ceeb;font-size:0.75rem;">📊 Panduan:</b><br><span style="font-size:0.72rem;">${item.guide}</span>`;
    }
    
    if (item.note) {
        html += `<br><br><i style="color:#ffa500;font-size:0.7rem;">⚠️ ${item.note}</i>`;
    }
    
    return html;
}