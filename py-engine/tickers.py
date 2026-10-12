# py-engine/tickers.py
# ==========================================
# WHITELIST SAHAM "KOLAM BESAR" (BIG CAPS)
# ==========================================
# Aturan: Hanya saham dengan Market Cap > Rp 10T & Likuiditas Tinggi.
# Tujuannya: Mencegah false momentum dari kerumunan ritel.
# ==========================================

TICKERS = [
    # --- SEKTOR KEUANGAN ---
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK',
    
    # --- SEKTOR PERTAMBANGAN & ENERGI ---
    'ADRO.JK', 'PTBA.JK', 'ITMG.JK', 'PGAS.JK', 'MEDC.JK',
    
    # --- SEKTOR INFRASTRUKTUR & TELEKOMUNIKASI ---
    'TLKM.JK', 'ISAT.JK', 'EXCL.JK', 'JSMR.JK',
    
    # --- SEKTOR KONSUMSI ---
    'ICBP.JK', 'INDF.JK', 'MYOR.JK', 'UNVR.JK',
    
    # --- SEKTOR INDUSTRI & OTOMOTIF ---
    'ASII.JK', 'UNTR.JK', 'SMGR.JK',
    
    # --- SEKTOR PROPERTI ---
    'BSDE.JK', 'CTRA.JK', 'SMRA.JK',
]
