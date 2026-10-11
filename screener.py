# screener_dynamic.py - Versi Valuation Based
import yfinance as yf
import json
from datetime import datetime, timezone, timedelta

wib = timezone(timedelta(hours=7))
now_wib = datetime.now(wib).strftime("%Y-%m-%d %H:%M WIB")

# KONFIGURASI VALUASI (Bukan Harga Nominal)
# Logika: Batubara biasanya murah di PBV < 0.8 dan mahal di PBV > 1.5
STOCKS = {
    "ITMG": {"max_pbv_buy": 0.9, "min_pbv_sell": 1.6}, 
    "PTBA": {"max_pbv_buy": 0.7, "min_pbv_sell": 1.4}
}

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(f"{ticker}.JK")
        
        # 1. Ambil Data Historis untuk RSI
        hist = stock.history(period="1mo")
        if hist.empty: return {"code": ticker, "error": "No History"}
        
        current_price = float(hist['Close'].iloc[-1])
        
        # Hitung RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = float(100 - (100 / (1 + rs)).iloc[-1])
        
        # 2. Ambil Data Fundamental (PBV & PER)
        info = stock.fast_info # Menggunakan fast_info agar lebih cepat & ringan
        # Catatan: fast_info kadang tidak punya PBV, fallback ke info biasa jika perlu
        # Atau gunakan key 'priceToBook' dari regular info
        
        # Cara paling aman ambil PBV/PER di yfinance terbaru:
        f_data = stock.info 
        pbv = f_data.get('priceToBook', 0)
        per = f_data.get('trailingPE', 0)
        div_yield = f_data.get('dividendYield', 0)
        if div_yield: div_yield *= 100 # Convert to percent

        # 3. Logika Sinyal Dinamis Berdasarkan Valuasi
        status = "WAIT "
        reason = ""
        
        target_config = STOCKS[ticker]
        
        if pbv > 0 and pbv <= target_config["max_pbv_buy"]:
            status = "BUY ZONE 🟢"
            reason = f"Valuasi Murah (PBV: {pbv:.2f}x). Harga saham terkoreksi seiring siklus batubara, namun fundamental masih solid di bawah nilai buku."
        elif pbv >= target_config["min_pbv_sell"]:
            status = "TAKE PROFIT 🔴"
            reason = f"Valuasi Mahal (PBV: {pbv:.2f}x). Pasar sudah menghargaikan ekspektasi tinggi. Amankan profit sebelum siklus berbalik."
        else:
            reason = f"Valuasi Wajar (PBV: {pbv:.2f}x). Menunggu koreksi valuasi atau breakout fundamental."

        return {
            "code": ticker, 
            "price": int(current_price), 
            "rsi": round(rsi, 1),
            "pbv": round(pbv, 2),
            "per": round(per, 1) if per else 0,
            "div_yield": round(div_yield, 1),
            "status": status,
            "reason": reason
        }
        
    except Exception as e:
        print(f"Error {ticker}: {e}")
        return {"code": ticker, "error": str(e)}

print("🚀 Running Dynamic Screener...")
results = [get_stock_data(code) for code in STOCKS.keys()]

output_data = {"updated": now_wib, "stocks": results}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("✅ Done. data.json updated.")
