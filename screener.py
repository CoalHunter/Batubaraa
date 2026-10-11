# screener.py - Versi Final Fix
import yfinance as yf
import json
from datetime import datetime, timezone, timedelta

wib = timezone(timedelta(hours=7))
now_wib = datetime.now(wib).strftime("%Y-%m-%d %H:%M WIB")

STOCKS = {
    "ITMG": {"max_pbv_buy": 0.9, "min_pbv_sell": 1.6}, 
    "PTBA": {"max_pbv_buy": 0.7, "min_pbv_sell": 1.4}
}

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(f"{ticker}.JK")
        hist = stock.history(period="1mo")
        
        if hist.empty: 
            return {"code": ticker, "price": 0, "rsi": 0, "pbv": 0, "per": 0, "div_yield": 0, "status": "ERROR", "reason": "Data historis kosong"}
        
        current_price = float(hist['Close'].iloc[-1])
        
        # Hitung RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = float(100 - (100 / (1 + rs)).iloc[-1])
        
        # Ambil Fundamental (Dengan Fallback)
        pbv, per, div_yield = 0, 0, 0
        try:
            info = stock.info
            pbv = info.get('priceToBook', 0) or 0
            per = info.get('trailingPE', 0) or 0
            dy = info.get('dividendYield', 0)
            div_yield = round(dy * 100, 2) if dy else 0
        except Exception:
            # Jika info gagal (sering terjadi di server GitHub), pakai estimasi kasar
            # Atau biarkan 0 agar tidak crash
            pass

        # Logika Sinyal & Alasan
        status = "WAIT ⏳"
        reason = f"Harga saat ini Rp {int(current_price):,}. Valuasi PBV {pbv:.2f}x. Menunggu sinyal valuasi lebih jelas."
        
        cfg = STOCKS[ticker]
        if pbv > 0 and pbv <= cfg["max_pbv_buy"]:
            status = "BUY ZONE "
            reason = f"Valuasi Sangat Murah (PBV: {pbv:.2f}x). Harga saham tertekan, cocok untuk akumulasi jangka panjang menunggu siklus bangkit."
        elif pbv >= cfg["min_pbv_sell"]:
            status = "TAKE PROFIT 🔴"
            reason = f"Valuasi Sudah Mahal (PBV: {pbv:.2f}x). Pasar terlalu optimis. Amankan profit sebelum siklus berbalik arah."

        return {
            "code": ticker, 
            "price": int(current_price), 
            "rsi": round(rsi, 1),
            "pbv": round(pbv, 2),
            "per": round(per, 1),
            "div_yield": div_yield,
            "status": status,
            "reason": reason # PASTIKAN NAMA INI 'reason'
        }
        
    except Exception as e:
        return {"code": ticker, "price": 0, "rsi": 0, "pbv": 0, "per": 0, "div_yield": 0, "status": "ERROR", "reason": str(e)}

print(" Running Screener...")
results = [get_stock_data(code) for code in STOCKS.keys()]
output_data = {"updated": now_wib, "stocks": results}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("✅ Done.")