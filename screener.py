# screener.py - Versi yfinance (Paling Stabil)
import yfinance as yf
import json
from datetime import datetime, timezone, timedelta

# Konfigurasi Waktu Indonesia Barat (WIB)
wib = timezone(timedelta(hours=7))
now_wib = datetime.now(wib).strftime("%Y-%m-%d %H:%M WIB")

STOCKS = {
    "ITMG": {"buy": 22000, "sell": 30000},
    "PTBA": {"buy": 2200, "sell": 3000}
}

def get_stock_data(ticker):
    try:
        # Download data 1 bulan terakhir untuk kalkulasi RSI
        stock = yf.Ticker(f"{ticker}.JK")
        hist = stock.history(period="1mo")
        
        if hist.empty:
            return {"code": ticker, "price": 0, "rsi": 0, "status": "ERROR: No Data"}

        current_price = float(hist['Close'].iloc[-1])
        
        # Kalkulasi RSI Manual (14 periode)
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = float(100 - (100 / (1 + rs)).iloc[-1])
        
        # Logika Sinyal
        status = "WAIT ⏳"
        if current_price <= STOCKS[ticker]["buy"] * 1.05 and rsi < 40:
            status = "BUY ZONE 🟢"
        elif current_price >= STOCKS[ticker]["sell"]:
            status = "TAKE PROFIT 🔴"
            
        return {
            "code": ticker, 
            "price": int(current_price), 
            "rsi": round(rsi, 1), 
            "status": status
        }
        
    except Exception as e:
        print(f"Gagal mengambil data {ticker}: {e}")
        return {"code": ticker, "price": 0, "rsi": 0, "status": f"ERROR: {str(e)[:30]}"}

# --- EKSEKUSI UTAMA ---
print("🚀 Memulai screening saham batubara...")
results = [get_stock_data(code) for code in STOCKS.keys()]

output_data = {
    "updated": now_wib,
    "stocks": results
}

# PENTING: Tulis ke file JSON
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("✅ Selesai! File data.json berhasil dibuat.")
print(json.dumps(output_data, indent=2))
