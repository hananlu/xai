# Kandidat paper konferensi lain

Disesuaikan dengan target pengguna: kontribusi empiris yang berarti, tanpa kewajiban menciptakan arsitektur baru. Semua judul di bawah adalah **hipotesis paper**, bukan klaim novelty yang sudah terbukti. Prioritaskan satu paper utama sampai pertanyaan dan buktinya kuat. Pemakaian dataset yang sama boleh untuk pertanyaan berbeda dengan disclosure yang jelas; jangan memecah hasil yang sama menjadi beberapa paper yang substansinya berulang.

## 1. Rekomendasi utama sekarang

**What Does the Explanation Explain? Auditing Network Traffic Forecasts under Telemetry Loss**

Pertanyaan: apakah explanation menggambarkan informasi demand yang benar-benar tercatat, nilai imputasi, atau proses pengukuran yang hilang? Ketika prediksi rusak akibat kehilangan input, apakah informasi atribusi lebih berguna daripada coverage dan recency sederhana?

Celah kandidat: interaksi observation loss dan attribution pada forecasting volume, diuji dengan input asli–rusak berpasangan, target tetap terukur, serta pemisahan value/mask dependence. Ini lebih sempit daripada klaim umum “XAI untuk jaringan” yang sudah banyak diteliti.

Bukti minimum untuk submission: beberapa keluarga model, beberapa tingkat/pola loss, replacement silang, banyak institusi/periode, kontrol linear eksak, sanity checks, dan hasil di jaringan eksternal atau batas generalisasi yang kuat. Temuan negatif yang konsisten dapat menjadi hasil utama. Pilot yang berjalan sekarang memeriksa kelayakan desainnya; belum mencukupi keseluruhan bukti tersebut.

Tumpang tindih terdekat: AIChronoLens, DeExp, MCal, IB-Forecast, dan audit evidence fault jaringan. Lihat LITERATURE_MATRIX.md. Kelayakan: **paling realistis untuk dikerjakan sekarang**, novelty empiris masih bersyarat pada hasil.

## 2. Calon paper kedua — keputusan pemulihan data

**Which Measurements Should Be Recovered First? Budgeted Telemetry Recovery for Network Traffic Forecasting**

Pertanyaan: bila collector menyimpan data lokal yang dapat diminta ulang, enam sampai puluhan input yang hilang tidak selalu sama pentingnya. Dengan biaya query terbatas, apakah pemilihan input yang dipandu model membantu pemulihan akurasi forecast dibandingkan “ambil yang terbaru dulu”?

Perbedaannya dari paper utama: output riset berupa **kebijakan memilih data untuk diambil ulang**, bukan penilaian kualitas penjelasan. Evaluasi error-versus-query-budget, biaya komputasi, dan latensi permintaan; bandingkan recency, random, seasonal sensitivity, acquisition policy yang mempelajari utility, dan oracle sebagai batas atas saja. Pilihan query tidak boleh melihat nilai tersembunyi atau target masa depan; hasil data baru hanya diketahui setelah query.

Dataset: deret CESNET lengkap untuk simulasi retrieval, kemudian testbed/cache trace jika ingin klaim sistem nyata. Data yang benar-benar hilang permanen tidak dapat diambil ulang; jangan menyebut imputasi sebagai pemulihan pengukuran asli.

Prior art: [Dynamic Measurement Scheduling, ICML 2019](https://proceedings.mlr.press/v97/chang19a.html) sudah mengatur acquisition temporal; [sequential forecast auditing, 2026](https://arxiv.org/abs/2611.03928) mengambil outcome yang belum terlihat; [repair-based anomaly explanations, 2026](https://doi.org/10.3390/app16115450) menguji counterfactual repair. Jadi, novelty tidak terletak pada ide “query yang penting” atau repair itu sendiri. Harus menunjukkan trade-off dan batas keputusan baru untuk input forecasting telemetry.

Kelayakan: **menjanjikan sebagai proyek lanjutan**, tetapi butuh tambahan asumsi sistem dan baseline acquisition. Sebaiknya dikerjakan setelah paper utama membuktikan bahwa peringkat/model dependence cukup berguna. Apabila hanya menambahkan kurva repair pada benchmark yang sama, gabungkan sebagai bagian paper utama.

## 3. Alternatif bila mengutamakan keputusan operator

**When Should a Traffic Forecaster Abstain? Coverage-Aware Selective Forecasting under Telemetry Loss**

Pertanyaan: pada coverage pengukuran berapa dan pola loss seperti apa model sebaiknya menahan forecast, memakai fallback musiman, atau tetap mengeluarkan prediksi? Apakah strategi itu berpindah ke institusi/periode baru?

Kontribusi yang dicari: pengukuran risiko terhadap jumlah forecast yang tetap dilayani, biaya penolakan/fallback, dan generalisasi threshold saat missingness berubah. Bandingkan coverage-only, recency-only, forecast-interval width, learned selector, dan varian dengan fitur XAI. XAI opsional; apabila tidak menambah manfaat, hasilnya harus tetap dilaporkan.

Batas novelty: [Bounded-Abstention Multi-horizon Forecasting, 2026](https://arxiv.org/abs/2602.04714) dan [Selective Forecasting via Metalearning, 2026](https://arxiv.org/abs/2606.23448) sudah mempelajari abstention. Yang belum dibuktikan di proyek ini ialah nilai metadata telemetry dan transfer operasional pada jaringan. Ini bukan ide baru “forecast dengan reject option”.

Kelayakan: **alternatif yang praktis** bila audit XAI menghasilkan sedikit manfaat tambahan. Dapat menjadi arah pengganti paper utama, bukan otomatis paper terpisah dari diagnostik risiko yang sama.

## Judul yang sebaiknya tidak dijadikan paper sendiri sekarang

- “LSTM versus GRU versus Transformer untuk traffic forecasting”: terlalu generik; benchmark luas sudah ada.
- “SHAP untuk prediksi traffic”: aplikasi XAI saja tidak cukup sebagai gap.
- “Attention is not explanation pada satu CSV”: generalisasi lemah dan masalah scope residual sudah beririsan dengan literatur.
- “Annual seasonality pada CESNET26”: sudah dibahas descriptor dataset; mengulangnya tidak menjadi kontribusi baru.

Urutan yang disarankan: selesaikan audit/pilot paper 1; pilih studi penuh berdasarkan hasil; paper 2 baru dimulai bila keputusan retrieval merupakan pertanyaan yang benar-benar berbeda. Jangan menjalankan tiga arah sekaligus untuk mengejar jumlah publikasi.
