# WPscanner (Wrong Price Scanner)

Screener saham otomatis yang mencari perusahaan Big Caps (LQ45/IDX30) yang "salah harga" (undervalued) secara ekstrem, namun memiliki fundamental kuat dan dividen yang konsisten.

## Filosofi
- **Deep Value:** Membeli di PBV < 0.9x untuk potensi re-rating maksimal.
- **Anti-Kerumunan:** Hanya saham dengan Market Cap > 10T & Likuiditas > 50M/hari.
- **Ketengan:** Dividen Yield > 5% sebagai bantal psikologis.

## Cara Kerja
Sistem ini berjalan otomatis setiap hari kerja jam 16:30 WIB menggunakan GitHub Actions. Data diperbarui secara real-time tanpa memerlukan server backend.
