# screener.py - Versi Tahan Banting
import requests
import json
from datetime import datetime

STOCKS = {
    "ITMG": {"buy": 22000, "sell": 30000},
    "PTBA": {"buy": 2200, "sell": 3000}
}

def get_data(code):
    try:
        # Menggunakan endpoint Yahoo Finance yang lebih stabil
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{code}.JK?interval=1d&range=5d"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status() # Raise error jika status bukan 200
        
        data = r.json()
        result = data['chart']['result'][0]
        meta = result['meta']
        
        price = meta.get('regularMarketPrice', 0)
        
        # Hitung RSI Sederhana
        closes = [c for c in result['indicators']['quote'][0]['close'] if c is not None]
        rsi = 50
        if len(closes) > 14:
            gains = sum(max(0, closes[i]-closes[i-1]) for i in range(len(closes)-14, len(closes)))
            losses = sum(max(0, closes[i-1]-closes[i]) for i in range(len(closes)-14, len(closes)))
            rs = (gains/14) / (losses/14) if losses > 0 else 100
            rsi = round(100 - (100 / (1 + rs)), 1)
            
        # Tentukan Status
        status = "WAIT"
        if price <= STOCKS[code]["buy"] * 1.1 and rsi < 40: 
            status = "BUY ZONE 🟢"
        elif price >= STOCKS[code]["sell"]: 
            status = "TAKE PROFIT 🔴"
            
        return {"code": code, "price": price, "rsi": rsi, "status": status}
        
    except Exception as e:
        print(f"Error fetching {code}: {e}")
        return {"code": code, "price": 0, "rsi": 0, "status": f"ERROR: {str(e)[:50]}"}

# Jalankan screening
results = [get_data(k) for k in STOCKS.keys()]

# PENTING: Pastikan file selalu tercipta meski error
output = {
    "updated": datetime.now().strftime("%Y-%m-%d %H:%M WIB"),
    "stocks": results
}

with open("data.json", "w") as f:
    json.dump(output, f, indent=2)

print("✅ Screening selesai. data.json berhasil dibuat.")
print(json.dumps(output, indent=2))
