# py-engine/screener.py
import sys
import os
import json
from datetime import datetime

try:
    from tickers import TICKERS
    if not TICKERS or len(TICKERS) == 0:
        raise ValueError("Daftar TICKERS kosong.")
except ImportError as e:
    print(f"❌ BATAL: File 'tickers.py' tidak ditemukan.\nDetail: {e}")
    sys.exit(1)
except Exception as e:
    print(f" BATAL: Error membaca ticker.\nDetail: {e}")
    sys.exit(1)

print(f"✅ Memuat {len(TICKERS)} ticker. Memulai screening (Mode Anti-Glitch)...")

import yfinance as yf
import pandas as pd
import numpy as np

def get_dividend_history(ticker):
    try:
        stock = yf.Ticker(ticker)
        divs = stock.dividends
        if divs.empty: return []
        cutoff_date = pd.Timestamp.now(tz=divs.index.tz) - pd.DateOffset(years=3)
        recent_divs = divs[divs.index >= cutoff_date]
        if recent_divs.empty: return []
        annual_divs = recent_divs.groupby(recent_divs.index.year).sum()
        hist_3y = stock.history(period="3y")
        history_list = []
        for year, dps in annual_divs.items():
            year_data = hist_3y[hist_3y.index.year == year]
            if not year_data.empty:
                avg_price = year_data['Close'].mean()
                est_yield = (dps / avg_price) * 100
                history_list.append({"year": int(year), "dps": round(float(dps), 2), "yield": round(float(est_yield), 2)})
        return sorted(history_list, key=lambda x: x['year'], reverse=True)
    except Exception as e:
        print(f"   ⚠️ Gagal ambil riwayat dividen {ticker}: {e}")
        return []

def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist_1mo = stock.history(period="1mo")
        hist_1y_weekly = stock.history(period="1y", interval="1wk")
        hist_1y_daily = stock.history(period="1y")  # Untuk cari 52-week low
        
        if len(hist_1y_weekly) < 20 or hist_1mo.empty or hist_1y_daily.empty: 
            return None

        current_price = info.get('currentPrice') or (hist_1mo['Close'].iloc[-1] if not hist_1mo['Close'].empty else 0)
        if not current_price or current_price <= 0:
            return None
        
        # 1. GERBANG LIKUIDITAS
        market_cap = info.get('marketCap', 0) or 0
        avg_daily_value = (hist_1mo['Close'] * hist_1mo['Volume']).mean()
        if market_cap < 10_000_000_000_000: return None
        if avg_daily_value < 50_000_000_000: return None

        # 2. SANITASI DATA
        raw_dy = info.get('dividendYield', 0) or 0
        dy = (raw_dy * 100) if raw_dy < 1 else raw_dy
        raw_pbv = info.get('priceToBook', 999) or 999
        pbv = raw_pbv if raw_pbv < 20 else 999
        raw_per = info.get('trailingPE', 999) or 999
        per = raw_per if raw_per < 100 else 999
        payout_ratio = info.get('payoutRatio', 0) or 0 
        earnings_growth = info.get('earningsGrowth', 0) or 0
        
        bank_tickers = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK']
        is_bank = ticker in bank_tickers
        raw_der = info.get('debtToEquity', 999) or 999
        der = raw_der if not is_bank else 0

        # 3. TEKNIKAL MINGGUAN
        sma_20_weekly = hist_1y_weekly['Close'].tail(20).mean()
        is_in_accumulation_zone = (current_price <= (sma_20_weekly * 1.15)) and (current_price >= (sma_20_weekly * 0.80))
        vol_4w = hist_1y_weekly['Volume'].tail(4).mean()
        vol_20w = hist_1y_weekly['Volume'].tail(20).mean()
        volume_expansion_weekly = vol_4w > (vol_20w * 1.15)

        # 4. KONSISTENSI DIVIDEN
        div_history = get_dividend_history(ticker)
        is_consistent = True
        if len(div_history) >= 2:
            if div_history[1]['dps'] > 0 and div_history[0]['dps'] < (div_history[1]['dps'] * 0.70):
                is_consistent = False

        # 5. KALKULASI RE-RATING
        target_pbv = 1.2
        if pbv > 0 and pbv < 20:
            re_rating_multiplier = target_pbv / pbv
        else:
            re_rating_multiplier = 1.0
        max_upside = min(re_rating_multiplier, 2.0)
        target_price = round(current_price * max_upside, 2)
        capital_gain_potential = round((max_upside - 1) * 100, 1)
        stop_loss = round(current_price * 0.85, 2)

        # ✅ 6. AREA BELI IDEAL BERDASARKAN SUPPORT KUAT (52-Week Low)
        # Ambil harga terendah 1 tahun terakhir sebagai acuan support kuat
        low_52_week = hist_1y_daily['Low'].min()
        # Area beli = 52-week low + buffer 5% (karena harga jarang tepat di low)
        buy_zone = round(low_52_week * 1.05, 2)
        # Jika buy_zone lebih tinggi dari harga sekarang, pakai harga sekarang × 0.95
        if buy_zone >= current_price:
            buy_zone = round(current_price * 0.95, 2)

        # 7. CEK FILTER & ALASAN
        reasons = []
        if pbv >= 0.9: reasons.append("PBV ≥ 0.9x")
        if dy < 5.0: reasons.append("Dividen < 5%")
        if not (0.20 <= payout_ratio <= 0.85): reasons.append("Payout Ratio tidak ideal")
        if earnings_growth <= -0.10: reasons.append("Laba anjlok")
        if not is_bank and der >= 100: reasons.append("Utang tinggi")
        if not is_in_accumulation_zone: reasons.append("Belum di area akumulasi")
        if not volume_expansion_weekly: reasons.append("Volume belum ekspansi")
        if not is_consistent: reasons.append("Dividen tidak konsisten")

        is_recommended = len(reasons) == 0

        return {
            "ticker": ticker.replace('.JK', ''),
            "name": info.get('shortName', ticker) or ticker,
            "price": round(float(current_price), 2),
            "pbv": round(float(pbv), 2),
            "per": round(float(per), 2),
            "dividend_yield": round(float(dy), 2),
            "payout_ratio": round(float(payout_ratio) * 100, 1),
            "category": "Deep Value & Re-rating",
            "buy_zone": buy_zone,  # ✅ Sekarang berbasis 52-week low
            "target_sell": target_price,
            "capital_gain_potential": capital_gain_potential,
            "stop_loss": stop_loss,
            "accumulation_signal": bool(is_in_accumulation_zone and volume_expansion_weekly),
            "div_history": div_history if div_history else [],
            "exit_rule": f"Jual bertahap saat harga mendekati Rp {target_price:,} (PBV {target_pbv}x) atau jika fundamental rusak.",
            "is_recommended": bool(is_recommended),
            "reasons": reasons,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"   ⚠️ Error memproses {ticker}: {e}")
        return None

# EKSEKUSI
results = []
for ticker in TICKERS:
    print(f"🔍 Menganalisis {ticker}...")
    data = analyze_stock(ticker)
    if data:
        if data['is_recommended']:
            print(f"   ✅ {data['ticker']} LOLOS! Potensi Gain: +{data['capital_gain_potential']}%")
        else:
            print(f"   ️ {data['ticker']} belum layak: {', '.join(data['reasons'])}")
        results.append(data)

# SIMPAN KE ROOT FOLDER
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
output_path = os.path.join(root_dir, 'data.json')

try:
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    recommended_count = sum(1 for r in results if r.get('is_recommended', False))
    print(f"\n SELESAI!")
    print(f"   Total saham dianalisis: {len(results)}")
    print(f"   Yang direkomendasikan: {recommended_count}")
    print(f"   Data disimpan ke {output_path}")
except Exception as e:
    print(f"\n⚠️ GAGAL menyimpan data.json. Detail: {e}")