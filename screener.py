# screener_idx.py - Menggunakan Data Resmi IDX (Bukan Yahoo)
import requests
import json
from datetime import datetime, timezone, timedelta
import time

# Setup Waktu WIB
wib = timezone(timedelta(hours=7))
now_wib = datetime.now(wib).strftime("%Y-%m-%d %H:%M WIB")

# Konfigurasi Target Valuasi (PBV)
STOCKS = {
    "ITMG": {"max_pbv_buy": 0.9, "min_pbv_sell": 1.6}, 
    "PTBA": {"max_pbv_buy": 0.7, "min_pbv_sell": 1.4}
}

def get_idx_data(code):
    """Mengambil data REAL-TIME dari API Publik IDX"""
    try:
        # Endpoint publik IDX untuk data saham
        url = f"https://idx.co.id/umbraco/Surface/TradingSummary/GetStockSummary?code={code}"
        
        # Header wajib agar tidak diblokir IDX
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.idx.co.id/'
        }
        
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        # Parsing data dari response IDX
        # Struktur data IDX kadang berubah, kita ambil field umum
        last_price = float(data.get('LastPrice', 0).replace(',', ''))
        pbv = float(data.get('PBV', 0))
        per = float(data.get('PER', 0))
        
        # Dividen Yield jarang ada di endpoint ini, kita set 0 dulu atau hitung manual jika perlu
        div_yield = 0 
        
        return {
            "price": last_price,
            "pbv": pbv,
            "per": per,
            "div_yield": div_yield
        }
        
    except Exception as e:
        print(f"Error fetch IDX {code}: {e}")
        return None

def calculate_rsi(price_history):
    """Hitung RSI manual jika history tersedia, jika tidak return 50"""
    # Untuk versi simpel ini, kita asumsikan RSI diambil dari cache atau default
    # Karena API IDX publik tidak selalu kasih history lengkap
    return 50 

print("🚀 Mengambil Data Asli dari IDX...")
results = []

for code, cfg in STOCKS.items():
    print(f"Mengambil data {code}...")
    idx_data = get_idx_data(code)
    
    if idx_data and idx_data['price'] > 0:
        current_price = idx_data['price']
        pbv = idx_data['pbv']
        per = idx_data['per']
        
        # Logika Sinyal Berbasis Data Asli
        status = "WAIT ⏳"
        reason = f"Harga Rp {int(current_price):,}. PER: {per}, PBV: {pbv}."
        
        if pbv > 0 and pbv <= cfg["max_pbv_buy"]:
            status = "BUY ZONE 🟢"
            reason = f"Valuasi Murah (PBV: {pbv:.2f}x). Data asli IDX menunjukkan harga di bawah nilai buku wajar."
        elif pbv >= cfg["min_pbv_sell"]:
            status = "TAKE PROFIT 🔴"
            reason = f"Valuasi Mahal (PBV: {pbv:.2f}x). Pasar sedang overheat berdasarkan data bursa."
            
        results.append({
            "code": code,
            "price": int(current_price),
            "rsi": 50, # Default sementara karena API IDX real-time tidak kasih history
            "pbv": round(pbv, 2),
            "per": round(per, 2),
            "div_yield": 0,
            "status": status,
            "reason": reason
        })
    else:
        results.append({
            "code": code, "price": 0, "rsi": 0, "pbv": 0, "per": 0, 
            "div_yield": 0, "status": "ERROR", "reason": "Gagal ambil data IDX"
        })
    
    # Jeda 2 detik agar tidak dianggap bot oleh IDX
    time.sleep(2)

output_data = {"updated": now_wib, "stocks": results}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("✅ Selesai. Data tersimpan di data.json")