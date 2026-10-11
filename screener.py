# screener_auto_idx.py - Full Otomatis Data Asli Bursa
import requests
import json
from datetime import datetime, timezone, timedelta
import time

wib = timezone(timedelta(hours=7))
now_wib = datetime.now(wib).strftime("%Y-%m-%d %H:%M WIB")

STOCKS = {
    "ITMG": {"max_pbv_buy": 0.9, "min_pbv_sell": 1.6}, 
    "PTBA": {"max_pbv_buy": 0.7, "min_pbv_sell": 1.4}
}

def get_realtime_data(code):
    """Mengambil data real-time dari endpoint publik IDX"""
    try:
        # Endpoint backdoor IDX yang sering digunakan aplikasi pihak ketiga
        url = f"https://www.idx.co.id/umbraco/Surface/TradingSummary/GetStockSummary?code={code}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.idx.co.id/id-id/perusahaan-tercatat/',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8'
        }
        
        resp = requests.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            
            # Parsing data dari response IDX
            # Catatan: Field name bisa berubah sewaktu-waktu tergantung update sistem IDX
            price_str = str(data.get('LastPrice', '0')).replace(',', '').replace('.', '')
            pbv_str = str(data.get('PBV', '0')).replace(',', '')
            per_str = str(data.get('PER', '0')).replace(',', '')
            
            price = float(price_str) if price_str else 0
            pbv = float(pbv_str) if pbv_str else 0
            per = float(per_str) if per_str else 0
            
            return price, pbv, per
        else:
            print(f"IDX returned status {resp.status_code} for {code}")
            return 0, 0, 0
            
    except Exception as e:
        print(f"Error fetching {code}: {e}")
        return 0, 0, 0

print("🚀 Mengambil Data Otomatis dari Bursa IDX...")
results = []

for code, cfg in STOCKS.items():
    print(f"Processing {code}...")
    
    price, pbv, per = get_realtime_data(code)
    
    # Jeda 3 detik agar tidak dianggap serangan DDoS oleh IDX
    time.sleep(3)
    
    # Logika Sinyal Dinamis
    status = "WAIT "
    reason = f"Harga Rp {int(price):,}. PER: {per}, PBV: {pbv}."
    
    if pbv > 0 and pbv <= cfg["max_pbv_buy"]:
        status = "BUY ZONE 🟢"
        reason = f"Valuasi Murah (PBV: {pbv:.2f}x). Data bursa menunjukkan harga di bawah nilai buku wajar."
    elif pbv >= cfg["min_pbv_sell"]:
        status = "TAKE PROFIT 🔴"
        reason = f"Valuasi Mahal (PBV: {pbv:.2f}x). Pasar sedang overheat berdasarkan data resmi."
    elif price > 0:
        reason = f"Data valuasi belum tersedia hari ini. Sinyal berbasis harga terakhir."

    results.append({
        "code": code,
        "price": int(price),
        "rsi": 50, # RSI butuh history, API real-time IDX tidak menyediakan
        "pbv": round(pbv, 2),
        "per": round(per, 2),
        "div_yield": 0,
        "status": status,
        "reason": reason
    })

output_data = {"updated": now_wib, "stocks": results}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("✅ Selesai. Data tersimpan di data.json")