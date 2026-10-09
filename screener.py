# screener.py
import requests
import json
from datetime import datetime

STOCKS = {
    "ITMG": {"buy": 22000, "sell": 30000},
    "PTBA": {"buy": 2200, "sell": 3000}
}

def get_data(code):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{code}.JK?interval=1d&range=1mo"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        d = r.json()['chart']['result'][0]
        price = d['meta']['regularMarketPrice']
        closes = [c for c in d['indicators']['quote'][0]['close'] if c][-15:]
        
        # Hitung RSI Manual
        gains = sum(max(0, closes[i]-closes[i-1]) for i in range(1, len(closes)))
        losses = sum(max(0, closes[i-1]-closes[i]) for i in range(1, len(closes)))
        rs = (gains/14) / (losses/14) if losses > 0 else 100
        rsi = 100 - (100 / (1 + rs))
        
        status = "WAIT"
        if price <= STOCKS[code]["buy"] * 1.05 and rsi < 40: status = "BUY ZONE"
        elif price >= STOCKS[code]["sell"]: status = "TAKE PROFIT"
        
        return {"code": code, "price": price, "rsi": round(rsi,1), "status": status}
    except Exception as e:
        return {"code": code, "error": str(e)}

results = [get_data(k) for k in STOCKS.keys()]

# Simpan hasil ke JSON file (bisa dibaca GitHub Pages nanti)
with open("data.json", "w") as f:
    json.dump({"updated": str(datetime.now()), "stocks": results}, f, indent=2)

print("Screening selesai. Data tersimpan di data.json")
for r in results: print(f"{r['code']}: {r.get('status', 'ERROR')} @ {r.get('price')}")
