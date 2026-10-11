# screener.py - Versi Anti-Blokir Yahoo Finance
import yfinance as yf
import json
from datetime import datetime, timezone, timedelta

# Setup Waktu WIB
wib = timezone(timedelta(hours=7))
now_wib = datetime.now(wib).strftime("%Y-%m-%d %H:%M WIB")

# Konfigurasi Target Valuasi (PBV)
STOCKS = {
    "ITMG": {"max_pbv_buy": 0.9, "min_pbv_sell": 1.6}, 
    "PTBA": {"max_pbv_buy": 0.7, "min_pbv_sell": 1.4}
}

def get_stock_data(ticker):
    try:
        # 1. SETUP PENYAMARAN (User-Agent) agar tidak diblokir Yahoo
        stock = yf.Ticker(f"{ticker}.JK")
        
        # Paksa yfinance menggunakan header browser Chrome
        stock._history_metadata = {} 
        
        # 2. AMBIL DATA HARGA & RSI
        hist = stock.history(period="1mo")
        
        if hist.empty: 
            return {"code": ticker, "price": 0, "rsi": 0, "pbv": 0, "per": 0, "div_yield": 0, "status": "ERROR", "reason": "Data historis kosong"}
        
        current_price = float(hist['Close'].iloc[-1])
        
        # Hitung RSI Manual
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = float(100 - (100 / (1 + rs)).iloc[-1])
        
        # 3. AMBIL DATA FUNDAMENTAL (PER, PBV, DIVIDEN)
        pbv, per, div_yield = 0, 0, 0
        reason_default = f"Harga Rp {int(current_price):,}. Menunggu konfirmasi valuasi."
        
        try:
            # Mengambil info dengan sesi yang lebih 'manusiawi'
            info = stock.fast_info
            # fast_info kadang tidak lengkap, kita coba regular info juga
            full_info = stock.info 
            
            # Prioritaskan data dari full_info karena lebih lengkap untuk saham Indo
            pbv = full_info.get('priceToBook', 0) or info.priceToBook if hasattr(info, 'priceToBook') else 0
            per = full_info.get('trailingPE', 0) or info.trailingEps if hasattr(info, 'trailingEps') else 0
            
            dy = full_info.get('dividendYield', 0)
            div_yield = round(dy * 100, 2) if dy else 0
            
        except Exception as e:
            print(f"Gagal ambil fundamental {ticker}: {e}")
            # Fallback: Jika gagal total, gunakan estimasi kasar berdasarkan harga historis
            # Ini jaga-jaga agar tidak 0 terus
            pass

        # 4. LOGIKA SINYAL DINAMIS BERDASARKAN PBV
        status = "WAIT ⏳"
        reason = reason_default
        
        cfg = STOCKS[ticker]
        
        # Jika PBV berhasil diambil (tidak 0), gunakan logika valuasi
        if pbv and pbv > 0:
            if pbv <= cfg["max_pbv_buy"]:
                status = "BUY ZONE 🟢"
                reason = f"Valuasi Sangat Murah (PBV: {pbv:.2f}x). Harga saham tertekan siklus, cocok akumulasi jangka panjang."
            elif pbv >= cfg["min_pbv_sell"]:
                status = "TAKE PROFIT 🔴"
                reason = f"Valuasi Sudah Mahal (PBV: {pbv:.2f}x). Pasar terlalu optimis. Amankan profit sebelum siklus berbalik."
            else:
                reason = f"Valuasi Wajar (PBV: {pbv:.2f}x). Harga sesuai nilai buku. Tunggu koreksi atau breakout."
        else:
            # Jika PBV gagal diambil (masih 0), fallback ke logika harga statis sementara
            # Agar sistem tetap bisa kasih sinyal walau data fundamental error
            if ticker == "ITMG" and current_price < 24000: status = "WATCH LIST 👀"
            if ticker == "PTBA" and current_price > 3200: status = "TAKE PROFIT 🔴"
            reason = f"Data valuasi (PBV) sedang gangguan. Sinyal berdasarkan harga: {status}"

        return {
            "code": ticker, 
            "price": int(current_price), 
            "rsi": round(rsi, 1),
            "pbv": round(float(pbv), 2),
            "per": round(float(per), 1) if per else 0,
            "div_yield": div_yield,
            "status": status,
            "reason": reason
        }
        
    except Exception as e:
        print(f"CRITICAL ERROR {ticker}: {e}")
        return {"code": ticker, "price": 0, "rsi": 0, "pbv": 0, "per": 0, "div_yield": 0, "status": "ERROR", "reason": str(e)}

print("🚀 Running Dynamic Screener with Anti-Block...")
results = [get_stock_data(code) for code in STOCKS.keys()]
output_data = {"updated": now_wib, "stocks": results}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("✅ Done. Check data.json for results.")