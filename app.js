// app.js - WPscanner
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
    
    return `${hari}, ${tanggal}-${bulan}-${tahun} pada ${jam}:${menit}:${detik}`;
}

let allStocks = []; // Simpan data global untuk search

document.addEventListener('DOMContentLoaded', () => {
    fetch('data.json')
        .then(res => {
            if (!res.ok) throw new Error('Gagal memuat data.json.');
            return res.json();
        })
        .then(data => {
            const grid = document.getElementById('stockGrid');
            const totalStocksEl = document.getElementById('totalStocks');
            const lastUpdateEl = document.getElementById('lastUpdate');
            
            if (!Array.isArray(data)) throw new Error('Data bukan array');
            
            // ✅ SORTIR ABJAD berdasarkan ticker
            allStocks = data.sort((a, b) => a.ticker.localeCompare(b.ticker));
            
            const recommended = allStocks.filter(s => s.is_recommended).length;
            totalStocksEl.innerText = `${recommended} Rekomendasi dari ${allStocks.length} Saham`;
            
            if (allStocks.length > 0 && allStocks[0].last_updated) {
                lastUpdateEl.innerText = `Data diperbarui: ${formatTanggalIndo(allStocks[0].last_updated)}`;
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

            // ✅ SEARCH BAR - Filter real-time
            const searchInput = document.getElementById('searchInput');
            searchInput.addEventListener('input', (e) => {
                const keyword = e.target.value.toLowerCase().trim();
                const filtered = allStocks.filter(stock => 
                    stock.ticker.toLowerCase().includes(keyword) || 
                    stock.name.toLowerCase().includes(keyword)
                );
                renderStocks(filtered);
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

function renderStocks(stocks) {
    const grid = document.getElementById('stockGrid');
    grid.innerHTML = ''; // Clear grid
    
    if (stocks.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align:center; padding: 40px; color:#757575;">
                <h3>🔍 Tidak ada saham yang cocok.</h3>
                <p>Coba kata kunci lain.</p>
            </div>`;
        return;
    }

    stocks.forEach(stock => {
        const card = document.createElement('div');
        card.className = stock.is_recommended ? 'card recommended' : 'card not-recommended';
        
        if (stock.is_recommended) {
            card.innerHTML = `
                <div class="ticker">${stock.ticker}</div>
                <div class="price">Rp ${stock.price.toLocaleString('id-ID')}</div>
                <div class="gain-preview">🚀 Potensi Gain: +${stock.capital_gain_potential}%</div>
                <div class="badge badge-recommend">✅ REKOMENDASI BELI</div>
                <div class="badge badge-accum">Dividen: ${stock.dividend_yield}%</div>
            `;
            card.onclick = () => showModal(stock, true);
        } else {
            card.innerHTML = `
                <div class="ticker">${stock.ticker}</div>
                <div class="price">Rp ${stock.price.toLocaleString('id-ID')}</div>
                <div class="reason-text">⏸️ Belum layak</div>
                <div class="reason-list">${stock.reasons ? stock.reasons.slice(0, 2).join(', ') : 'Tidak memenuhi kriteria'}</div>
            `;
            card.onclick = () => showModal(stock, false);
        }
        
        grid.appendChild(card);
    });
}

function showModal(stock, isRecommended = false) {
    document.getElementById('modalTicker').innerText = stock.ticker;
    document.getElementById('modalName').innerText = stock.name;
    document.getElementById('modalGain').innerText = `${stock.capital_gain_potential >= 0 ? '+' : ''}${stock.capital_gain_potential}%`;
    document.getElementById('modalDiv').innerText = `${stock.dividend_yield}%`;
    document.getElementById('modalSL').innerText = `Rp ${stock.stop_loss.toLocaleString('id-ID')}`;

    let divHtml = '';
    if (stock.div_history && stock.div_history.length > 0) {
        divHtml = `<div class="div-history">
            <h4>🛡️ Safety Net: Riwayat Dividen 3 Tahun</h4>
            <ul>`;
        stock.div_history.forEach(h => {
            divHtml += `<li><strong>Tahun ${h.year}:</strong> Dibagi Rp ${h.dps.toLocaleString('id-ID')}/lembar (Est. Yield ${h.yield}%)</li>`;
        });
        divHtml += `</ul>
            <p>*Dividen konsisten adalah bukti arus kas nyata, bukan akuntansi palsu.</p>
        </div>`;
    }

    let statusHtml = '';
    if (!isRecommended) {
        statusHtml = `<div class="not-recommended-notice">
            <h4>⏸️ Belum Direkomendasikan</h4>
            <p>Saham ini belum memenuhi semua kriteria ketat WPscanner. Alasan:</p>
            <ul>${stock.reasons.map(r => `<li>${r}</li>`).join('')}</ul>
            <p><strong>Pantau terus</strong> dan tunggu sampai semua kriteria terpenuhi.</p>
        </div>`;
    }

    document.getElementById('modalDetails').innerHTML = `
        ${statusHtml}
        <div class="detail-row"><span>Harga Saat Ini</span> <strong>Rp ${stock.price.toLocaleString('id-ID')}</strong></div>
        <div class="detail-row"><span>Area Beli Ideal (Support Kuat)</span> <span style="color:#26aa99; font-weight:700;">Rp ${stock.buy_zone.toLocaleString('id-ID')}</span></div>
        <div class="detail-row"><span>Target Jual (Re-rating)</span> <span style="color:#ee4d2d; font-weight:700;">Rp ${stock.target_sell.toLocaleString('id-ID')}</span></div>
        <div class="detail-row"><span>Valuasi Saat Ini</span> <span>PBV: ${stock.pbv}x | PER: ${stock.per}x</span></div>
        <div class="detail-row"><span>Payout Ratio</span> <span>${stock.payout_ratio}%</span></div>
        ${divHtml}
    `;
    
    document.getElementById('stockModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('stockModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('stockModal');
    if (event.target == modal) {
        closeModal();
    }
}