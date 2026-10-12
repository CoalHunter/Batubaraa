// app.js - WPscanner v4.1 (Lengkap dengan Clear Cache & Glossary)

// 1. Fungsi Format Tanggal Indonesia
function formatTanggalIndo(dateStr) {
    const days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
    const months = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
    
    const d = new Date(dateStr);
    const hari = days[d.getDay()];
    const tanggal = d.getDate();
    const bulan = months[d.getMonth()];
    const tahun = d.getFullYear();
    const jam = String(d.getHours()).padStart(2, '0');
    const menit = String(d.getMinutes()).padStart(2, '0');
    const detik = String(d.getSeconds()).padStart(2, '0');
    
    return `${hari}, ${tanggal}-${bulan}-${tahun} pada ${jam}:${menit}:${detik} WIB`;
}

// 2. Helper untuk membuat Tooltip dari glossary.js
function makeTooltip(label, glossaryKey) {
    const tooltipContent = glossaryKey && GLOSSARY[glossaryKey] ? getTooltipHTML(glossaryKey) : '';
    const hasTooltip = tooltipContent !== '';
    return `
        <div class="label-group">
            <span>${label}</span>
            ${hasTooltip ? `<span class="tooltip-trigger" tabindex="0">?<span class="tooltip-text">${tooltipContent}</span></span>` : ''}
        </div>
    `;
}

let allStocks = [];
let scanData = null;

// 3. Main Event Listener
document.addEventListener('DOMContentLoaded', () => {
    fetch('data.json?v=' + Date.now())
        .then(res => {
            if (!res.ok) throw new Error('Gagal memuat data.json.');
            return res.json();
        })
        .then(data => {
            scanData = data;
            const grid = document.getElementById('stockGrid');
            const totalStocksEl = document.getElementById('totalStocks');
            const lastUpdateEl = document.getElementById('lastUpdate');
            
            const stocks = data.stocks || data;
            if (!Array.isArray(stocks)) throw new Error('Data bukan array');
            
            // Sorting Abjad
            allStocks = [...stocks].sort((a, b) => {
                return a.ticker.localeCompare(b.ticker, 'id', { sensitivity: 'base' });
            });
            
            // Update Stats Header
            const recommended = allStocks.filter(s => s.status === 'recommended').length;
            totalStocksEl.innerText = `${recommended} Rekomendasi dari ${allStocks.length} Saham`;
            
            const scanTime = data.scan_time || (allStocks[0] && allStocks[0].last_updated);
            if (scanTime) {
                lastUpdateEl.innerText = `Data diperbarui: ${formatTanggalIndo(scanTime)}`;
            } else {
                lastUpdateEl.innerText = 'Belum ada data screening.';
            }
            
            if (allStocks.length === 0) {
                grid.innerHTML = `
                    <div style="grid-column: 1/-1; text-align:center; padding: 40px; color:#757575;">
                        <h3>🔍 Tidak ada data saham.</h3>
                        <p>Jalankan GitHub Actions untuk generate data.</p>
                    </div>`;
                return;
            }

            renderStocks(allStocks);

            // --- EVENT LISTENERS ---

            // A. Search Bar
            const searchInput = document.getElementById('searchInput');
            searchInput.addEventListener('input', (e) => {
                const keyword = e.target.value.toLowerCase().trim();
                const filtered = allStocks.filter(stock => 
                    stock.ticker.toLowerCase().includes(keyword) || 
                    (stock.name && stock.name.toLowerCase().includes(keyword))
                );
                renderStocks(filtered);
            });

            // B. Tombol Log Analisis
            document.getElementById('logBtn').addEventListener('click', showLogModal);
            
            // C. Tombol Clear Cache (BARU)
            document.getElementById('clearCacheBtn').addEventListener('click', () => {
                // Paksa browser reload dengan parameter waktu unik untuk bypass cache
                const baseUrl = window.location.href.split('?')[0];
                window.location.href = baseUrl + '?v=' + Date.now();
            });
            
            // D. Support Tap untuk Tooltip di Mobile
            document.addEventListener('click', (e) => {
                const trigger = e.target.closest('.tooltip-trigger');
                if (trigger) {
                    document.querySelectorAll('.tooltip-trigger.active').forEach(t => {
                        if (t !== trigger) t.classList.remove('active');
                    });
                    trigger.classList.toggle('active');
                    e.stopPropagation();
                } else {
                    document.querySelectorAll('.tooltip-trigger.active').forEach(t => {
                        t.classList.remove('active');
                    });
                }
            });
        })
        .catch(err => {
            console.error('Error loading data:', err);
            document.getElementById('stockGrid').innerHTML = `
                <div style="grid-column: 1/-1; text-align:center; padding: 40px; color: #ee4d2d;">
                    <h3>⚠️ Gagal Memuat Data</h3>
                    <p>Pastikan file <code>data.json</code> valid.</p>
                    <p><small>Detail error: ${err.message}</small></p>
                </div>`;
            document.getElementById('lastUpdate').innerText = 'Gagal memuat waktu update.';
        });
});

// 4. Fungsi Render Kartu Saham
function renderStocks(stocks) {
    const grid = document.getElementById('stockGrid');
    grid.innerHTML = '';
    
    if (stocks.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align:center; padding: 40px; color:#757575;">
                <h3>🔍 Tidak ada saham yang cocok.</h3>
                <p>Coba kata kunci lain.</p>
            </div>`;
        return;
    }

    stocks.forEach(stock => {
        if (stock.status === 'failed' && !stock.price) return;
        
        const card = document.createElement('div');
        card.className = stock.status === 'recommended' ? 'card recommended' : 'card not-recommended';
        
        if (stock.status === 'recommended') {
            card.innerHTML = `
                <div class="ticker">${stock.ticker}</div>
                <div class="price">Rp ${stock.price.toLocaleString('id-ID')}</div>
                <div class="valuation-badge" style="background:${stock.valuation_color || '#26aa99'};">
                    ${stock.valuation_label || 'Wajar'}
                </div>
                <div class="gain-preview">🚀 Potensi Gain: +${stock.capital_gain_potential}%</div>
                <div class="badge badge-recommend">✅ REKOMENDASI BELI</div>
                <div class="badge badge-accum">Dividen di Area Beli: ${stock.dividend_yield}%</div>
            `;
            card.onclick = () => showModal(stock, true);
        } else {
            card.innerHTML = `
                <div class="ticker">${stock.ticker}</div>
                <div class="price">Rp ${stock.price ? stock.price.toLocaleString('id-ID') : '-'}</div>
                <div class="valuation-badge" style="background:${stock.valuation_color || '#757575'};">
                    ${stock.valuation_label || '-'}
                </div>
                <div class="reason-text">⏸️ Belum layak</div>
                <div class="reason-list">${stock.reasons ? stock.reasons.slice(0, 2).join(', ') : (stock.fail_reason || 'Tidak memenuhi kriteria')}</div>
            `;
            card.onclick = () => showModal(stock, false);
        }
        
        grid.appendChild(card);
    });
}

// 5. Fungsi Modal Detail Saham
function showModal(stock, isRecommended = false) {
    document.getElementById('modalTicker').innerText = stock.ticker;
    document.getElementById('modalName').innerText = stock.name || '-';
    
    const gainText = stock.capital_gain_potential < 0 
        ? `${stock.capital_gain_potential}%` 
        : `+${stock.capital_gain_potential}%`;
        
    document.getElementById('modalGain').innerText = gainText;
    document.getElementById('modalDiv').innerText = `${stock.dividend_yield}%`;
    document.getElementById('modalSL').innerText = `Rp ${stock.stop_loss ? stock.stop_loss.toLocaleString('id-ID') : '-'}`;

    // Badge Valuasi di header modal
    const valuationBadge = stock.valuation_label 
        ? `<div style="display:inline-block;background:${stock.valuation_color || '#0284c7'};color:white;padding:6px 14px;border-radius:20px;font-size:0.85rem;font-weight:700;margin-bottom:15px;">
             Valuasi: ${stock.valuation_label} (PBV ${stock.pbv}x)
           </div>` 
        : '';

    // Riwayat Dividen
    let divHtml = '';
    if (stock.div_history && stock.div_history.length > 0) {
        divHtml = `<div class="div-history">
            <h4>🛡️ Safety Net: Riwayat Dividen 3 Tahun</h4>
            <ul>`;
        stock.div_history.forEach(h => {
            divHtml += `<li><strong>Tahun ${h.year}:</strong> Dibagi Rp ${h.dps.toLocaleString('id-ID')}/lembar (Est. Yield ${h.yield}%)</li>`;
        });
        divHtml += `</ul>
            <p style="margin-top:10px; padding:8px; background:#e6f7f4; border-radius:4px; font-size:0.85rem;">
                <strong>💡 Proyeksi di Area Beli:</strong><br>
                DPS Rata-rata: <strong>Rp ${stock.avg_dps_3y || 0}</strong>/lembar<br>
                Yield di Area Beli (Rp ${stock.buy_zone ? stock.buy_zone.toLocaleString('id-ID') : '-'}): <strong style="color:#26aa99;">${stock.dividend_yield}%</strong>
            </p>
        </div>`;
    }

    // Status Belum Direkomendasikan
    let statusHtml = '';
    if (!isRecommended) {
        const reasons = stock.reasons || [stock.fail_reason || 'Tidak memenuhi kriteria'];
        statusHtml = `<div class="not-recommended-notice">
            <h4>⏸️ Belum Direkomendasikan</h4>
            <p>Saham ini belum memenuhi semua kriteria ketat WPscanner. Alasan:</p>
            <ul>${reasons.map(r => `<li>${r}</li>`).join('')}</ul>
            <p><strong>Pantau terus</strong> dan tunggu sampai semua kriteria terpenuhi.</p>
        </div>`;
    }

    // Detail Row dengan Tooltip
    const priceHtml = stock.price ? `
        <div class="detail-row">
            ${makeTooltip('Harga Saat Ini', '')}
            <strong>Rp ${stock.price.toLocaleString('id-ID')}</strong>
        </div>
        <div class="detail-row">
            ${makeTooltip('Valuasi Saat Ini', 'pbv')}
            <span><strong style="color:${stock.valuation_color || '#0284c7'};">${stock.valuation_label || '-'}</strong> | PBV: ${stock.pbv}x | PER: ${stock.per}x</span>
        </div>
        <div class="detail-row">
            ${makeTooltip('Dividen Yield (Harga Sekarang)', 'dividend_yield')}
            <span style="color:#757575;">${stock.dividend_yield_current || 0}%</span>
        </div>
        <div class="detail-row">
            ${makeTooltip('Area Beli Ideal', 'buy_zone')}
            <span style="color:#26aa99; font-weight:700;">Rp ${stock.buy_zone ? stock.buy_zone.toLocaleString('id-ID') : '-'}</span>
        </div>
        <div class="detail-row">
            ${makeTooltip('Dividen Yield (di Area Beli)', 'dividend_yield')}
            <span style="color:#26aa99; font-weight:700;">${stock.dividend_yield}%</span>
        </div>
        <div class="detail-row">
            ${makeTooltip('Target Jual', 'target_sell')}
            <span style="color:#ee4d2d; font-weight:700;">Rp ${stock.target_sell ? stock.target_sell.toLocaleString('id-ID') : '-'}</span>
        </div>
        <div class="detail-row">
            ${makeTooltip('Potensi Capital Gain', 'capital_gain')}
            <span style="color:${stock.capital_gain_potential >= 0 ? '#26aa99' : '#ee4d2d'}; font-weight:700;">${gainText}</span>
        </div>
        <div class="detail-row">
            ${makeTooltip('Payout Ratio', 'payout_ratio')}
            <span>${stock.payout_ratio ? stock.payout_ratio + '%' : '-'}</span>
        </div>
        <div class="detail-row">
            ${makeTooltip('Stop Loss', 'stop_loss')}
            <span style="color:#ee4d2d; font-weight:700;">Rp ${stock.stop_loss ? stock.stop_loss.toLocaleString('id-ID') : '-'}</span>
        </div>
    ` : `<div class="detail-row"><span>Status</span> <strong style="color:#c62828;">Gagal Dianalisis</strong></div>
        <div class="detail-row"><span>Alasan</span> <span>${stock.fail_reason || 'Data tidak tersedia'}</span></div>`;

    document.getElementById('modalDetails').innerHTML = `
        ${valuationBadge}
        ${statusHtml}
        ${priceHtml}
        ${divHtml}
    `;
    
    document.getElementById('stockModal').style.display = 'flex';
}

// 6. Fungsi Modal Log Analisis
function showLogModal() {
    if (!scanData) return;
    
    document.getElementById('logScanTime').innerText = `Waktu scan: ${formatTanggalIndo(scanData.scan_time)}`;
    
    const stats = scanData.stats || {};
    document.getElementById('logStats').innerHTML = `
        <div class="log-stat-box recommended">
            ✅ Direkomendasikan
            <span class="stat-number">${stats.recommended || 0}</span>
        </div>
        <div class="log-stat-box not_recommended">
            ⏸️ Belum Layak
            <span class="stat-number">${stats.not_recommended || 0}</span>
        </div>
        <div class="log-stat-box failed">
            ❌ Gagal Analisis
            <span class="stat-number">${stats.failed || 0}</span>
        </div>
    `;
    
    const stocks = scanData.stocks || scanData;
    const sortedStocks = [...stocks].sort((a, b) => a.ticker.localeCompare(b.ticker, 'id', { sensitivity: 'base' }));
    
    let logHtml = '';
    sortedStocks.forEach(stock => {
        let icon, reasonText;
        if (stock.status === 'recommended') {
            icon = '✅';
            reasonText = `Gain: +${stock.capital_gain_potential}% | Yield: ${stock.dividend_yield}% | Valuasi: ${stock.valuation_label || '-'}`;
        } else if (stock.status === 'not_recommended') {
            icon = '⏸️';
            reasonText = stock.reasons ? stock.reasons.join(', ') : (stock.fail_reason || '-');
        } else {
            icon = '❌';
            reasonText = stock.fail_reason || 'Data tidak tersedia';
        }
        
        logHtml += `
            <div class="log-item ${stock.status}">
                <span class="log-status-icon">${icon}</span>
                <div class="log-item-content">
                    <div class="log-item-ticker">
                        ${stock.ticker} 
                        <span style="display:inline-block;background:${stock.valuation_color || '#757575'};color:white;padding:2px 6px;border-radius:3px;font-size:0.7rem;margin-left:6px;">
                            ${stock.valuation_label || '-'}
                        </span>
                    </div>
                    <div class="log-item-name">${stock.name || '-'}</div>
                    <div class="log-item-reason">${reasonText}</div>
                </div>
            </div>
        `;
    });
    
    document.getElementById('logList').innerHTML = logHtml;
    document.getElementById('logModal').style.display = 'flex';
}

// 7. Fungsi Tutup Modal
function closeModal() {
    document.getElementById('stockModal').style.display = 'none';
}

function closeLogModal() {
    document.getElementById('logModal').style.display = 'none';
}

// Tutup modal jika klik di area gelap (luar modal)
window.onclick = function(event) {
    if (event.target == document.getElementById('stockModal')) {
        closeModal();
    }
    if (event.target == document.getElementById('logModal')) {
        closeLogModal();
    }
}