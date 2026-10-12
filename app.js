fetch('data.json')
    .then(res => {
        if (!res.ok) throw new Error('Gagal memuat data.json.');
        return res.json();
    })
    .then(data => {
        const grid = document.getElementById('stockGrid');
        const totalStocksEl = document.getElementById('totalStocks');
        const lastUpdateEl = document.getElementById('lastUpdate');
        
        // Validasi data
        if (!Array.isArray(data)) {
            throw new Error('Data bukan array');
        }
        
        // Hitung yang direkomendasikan vs total
        const recommended = data.filter(s => s.is_recommended).length;
        totalStocksEl.innerText = `${recommended} Rekomendasi dari ${data.length} Saham`;
        
        if (data.length > 0 && data[0].last_updated) {
            lastUpdateEl.innerText = `Data diperbarui: ${formatTanggalIndo(data[0].last_updated)}`;
        } else {
            lastUpdateEl.innerText = 'Belum ada data screening.';
        }
        
        if (data.length === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1/-1; text-align:center; padding: 40px; color:#757575;">
                    <h3>🔍 Tidak ada data saham.</h3>
                    <p>Jalankan GitHub Actions untuk generate data.</p>
                </div>`;
            return;
        }

        // Render semua saham
        data.forEach(stock => {
            const card = document.createElement('div');
            card.className = stock.is_recommended ? 'card recommended' : 'card not-recommended';
            
            if (stock.is_recommended) {
                card.innerHTML = `
                    <div class="ticker">${stock.ticker}</div>
                    <div class="price">Rp ${stock.price.toLocaleString('id-ID')}</div>
                    <div class="gain-preview"> Potensi Gain: +${stock.capital_gain_potential}%</div>
                    <div class="badge badge-recommend">✅ REKOMENDASI BELI</div>
                    <div class="badge badge-accum">Dividen: ${stock.dividend_yield}%</div>
                `;
                card.onclick = () => showModal(stock);
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