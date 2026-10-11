# screener_hybrid.py - Kombinasi Yahoo (History) + Stockbit/GoAPI (Fundamental)
import yfinance as yf
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

def get_fundamental_id(code):
    """Mengambil PER & PBV dari API GoAPI/Stockbit (Sumber Data Indo)"""
    try:
        # Menggunakan endpoint publik yang lebih ramah server cloud
        url = f"https://goapi.io/api/v1/stocks/{code}" 
        # Alternatif jika goapi down: https://api.stockbit.com/v1/AmsQuote.GetSummary?symbol={code}
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            # Parsing sesuai struktur GoAPI/Stockbit
            # Catatan: Struktur API bisa berubah, ini adalah format umum
            pbv = float(data.get('pbv', 0))
            per = float(data.get('per', 0))
            return pbv, per
        return 0, 0
    except Exception as e:
        print(f"Gagal ambil fundamental {code}: {e}")
        return 0, 0

def get_technical_yahoo(code):
    """Mengambil Harga & RSI dari Yahoo Finance (Paling Stabil untuk History)"""
    try:
        stock = yf.Ticker(f"{code}.JK")
        hist = stock.history(period="1mo")
        
        if hist.empty: return 0, 50
        
        price = float(hist['Close'].iloc[-1])
        
        # Hitung RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = float(100 - (100 / (1 + rs)).iloc[-1])
        
        return price, round(rsi, 1)
    except Exception as e:
        print(f"Error Yahoo {code}: {e}")
        return 0, 50

print("🚀 Running Hybrid Screener (Yahoo + Indo API)...")
results = []

for code, cfg in STOCKS.items():
    print(f"Processing {code}...")
    
    # 1. Ambil Teknikal dari Yahoo
    price, rsi = get_technical_yahoo(code)
    
    # 2. Ambil Fundamental dari API Indo
    pbv, per = get_fundamental_id(code)
    
    # Jeda sebentar agar tidak diblokir API Indo
    time.sleep(1.5)
    
    # 3. Logika Sinyal
    status = "WAIT ⏳"
    reason = f"Harga Rp {int(price):,}. RSI: {rsi}."
    
    if pbv > 0: # Hanya pakai logika PBV jika data Indo berhasil diambil
        if pbv <= cfg["max_pbv_buy"]:
            status = "BUY ZONE 🟢"
            reason = f"Valuasi Murah (PBV: {pbv:.2f}x). Data bursa menunjukkan harga di bawah nilai buku wajar."
        elif pbv >= cfg["min_pbv_sell"]:
            status = "TAKE PROFIT 🔴"
            reason = f"Valuasi Mahal (PBV: {pbv:.2f}x). Pasar sedang overheat berdasarkan data resmi."
    else:
        reason += " (Data valuasi sedang gangguan, sinyal berbasis teknikal saja)"

    results.append({
        "code": code,
        "price": int(price),
        "rsi": rsi,
        "pbv": round(pbv, 2),
        "per": round(per, 2),
        "div_yield": 0, # Dividen jarang ada di API publik gratisan
        "status": status,
        "reason": reason
    })

output_data = {"updated": now_wib, "stocks": results}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("✅ Selesai. Data tersimpan di data.json")