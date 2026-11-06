# Status development terbaru

Kalibrasi metrik dan prototipe nonnegative log-Ridge telah selesai pada 12 institusi development lama. Lihat [DEVELOPMENT_RESULTS.md](DEVELOPMENT_RESULTS.md) dan [MEASUREMENT_CONTRACT.md](MEASUREMENT_CONTRACT.md). Delapan institusi target baru tetap belum digunakan; eksperimen transfer konfirmatori 48 institusi belum dijalankan.

---

# Brief penelitian

5 November 2026, Asia/Jakarta. Judul kerja: **Cross-Institution Reliability of Temporal Attributions in Network Traffic Forecasting**.

## Inti penelitian

Model forecasting yang dilatih pada sekelompok institusi akan dipakai di institusi baru. Kita mengukur dua hal secara terpisah: apakah volume traffic masih diprediksi dengan akurat, dan apakah kontribusi kelompok lag yang ditampilkan explanation sesuai ketergantungan model di tempat baru. Penjelasan tepat tidak menjamin prediksi tepat; perubahan ranking dapat mencerminkan perubahan input yang sah.

## Pertanyaan riset

1. Bagaimana forecast error dan kualitas temporal attribution berbeda antara institusi training dan institusi target pada periode evaluasi yang sama?
2. Seberapa sensitif penilaian explanation terhadap pemilihan reference source versus reference dari history target yang sudah tersedia?
3. Apakah adaptasi dengan data target terbatas memperbaiki forecast error dan kualitas attribution secara sejalan atau berbeda?

Tidak ada hipotesis bahwa XAI pasti gagal atau model tertentu harus menang.

## Dataset dan pembagian yang sudah dibuat

CESNET-TimeSeries26 resmi, volume n_bytes hourly, coverage menggunakan time grid 10 menit. Target: GB pada endpoint 1 dan 6 jam berikutnya; context awal satu minggu. Dataset mencakup satu ISP, sehingga hasil awal berlaku lintas institusi dalam ISP tersebut.

| Kelompok | Institusi | Penggunaan |
|---|---:|---|
| Development | 12 | Pilot lama, debugging dan kalibrasi ukuran evaluasi |
| Source | 32 | Training forecaster transfer |
| Validation | 8 | Pemilihan konfigurasi tanpa outcome institusi target |
| Target | 8 | Evaluasi institusi baru setelah protokol lengkap dibekukan |

Jumlah studi baru 48 institusi, di luar 12 development. Membership sudah dibekukan dalam INSTITUTION_SPLIT.csv dan SPLIT_MANIFEST.json. Pemilihan memakai empat strata volume dan hash deterministik atas audit training 2024; 265 kandidat memenuhi eligibility setelah development dikeluarkan. Source, validation, target dan development tidak tumpang tindih.

Membership baru bukan bukti generalisasi atau jaminan perbedaan domain. Semua berasal dari ISP yang sama, dan role assignment menggunakan ringkasan volume training target untuk stratifikasi. Ringkasan tersebut tidak digunakan untuk fitting/normalisasi model zero-shot. Aturan normalisasi hanya boleh memakai source fitting data atau history yang tersedia saat forecast, sesuai definisi protokol.

## Eksperimen inti

Alur: audit coverage -> split institusi dan waktu -> training source -> transfer tanpa update parameter -> forecast dan attribution pada target -> evaluasi terpisah -> arm adaptasi terbatas.

Pembanding awal: persistence/seasonal-naive, Ridge sebagai kontrol matematis, DLinear, dan GRU. Neural models memakai tiga seed. Bentuk output nonnegatif dan fungsi preprocessing harus ditetapkan sebelum fitting; explanation harus mengacu pada fungsi prediksi akhir yang sama.

Temporal attribution awal: IG dengan pemeriksaan numerik, block occlusion, grouped Shapley bila biaya memungkinkan, serta kontrol random/recency. Kolom hasil harus membedakan arithmetic correctness, fidelity terhadap intervensi input yang dinyatakan, sensitivitas ranking/reference, dan forecast error. Kesamaan heatmap bukan ukuran keberhasilan utama.

Pisahkan evaluasi pada institusi baru dari perubahan waktu: bandingkan source dan target pada timestamp/periode yang sepadan, lalu tambahkan periode baru sebagai faktor. Training source 2024 menjadi rencana awal. Periode final April 2025–Juni 2026 tetap belum diberi skor. Tanggal validation, kalender adaptation, sampel attribution, operator intervensi, toleransi numerik dan analisis utama belum menjadi protokol final.

## Posisi terhadap literatur

- [TransMUSE](https://arxiv.org/html/2203.02083v1), §4.5: transfer traffic forecasters antar region dengan evaluasi error sudah ada. Bagian model-transfer validation diperiksa. Kita tidak mengklaim memperkenalkan transfer forecasting.
- [TimeSAE, v2](https://arxiv.org/html/2601.09776v2), §3.3 dan §4.2: sudah mempelajari faithful explanations dan menguji transfer ETTh-1 ke ETTh-2. [Metadata terkini](https://arxiv.org/abs/2601.09776) menyatakan accepted at ICML 2026; penyebutan sebelumnya sebagai preprint saja perlu diperbarui. Kita tidak mengklaim pertama mengevaluasi explanation under shift. Bagian metode/OOD ditinjau; pembandingan implementasi dan keseluruhan eksperimennya belum selesai.
- [AIChronoLens](https://dspace.networks.imdea.org/handle/20.500.12761/1917): diagnosis error melalui penjelasan temporal jaringan sudah ada. Perbedaan yang dituju perlu dibuktikan lewat desain deployment institusi, reference controls dan adaptation, bukan nama metode baru.

Kandidat novelty: **benchmark empiris deployment lintas institusi yang memisahkan akurasi, attribution fidelity dan pengaruh reference/adaptation**. Ini belum novelty yang terkonfirmasi; domain jaringan atau banyaknya institusi saja tidak cukup. Temuan akhirnya harus memberi pengetahuan yang lebih spesifik daripada “distribution shift memengaruhi model”.

## Status dan pekerjaan berikutnya

Sudah selesai: dataset resmi/pilot v2, audit awal literatur, pemilihan topik, pembagian 48 institusi baru dan pemeriksaan disjointness.

Belum dilakukan: training model transfer, scoring target baru, pembuktian kualitas attribution lintas institusi, studi konfirmatori, paper final dan PPT.

Tahap berikutnya: selesaikan pembandingan metode/metric penelitian terdekat; kalibrasi metric pada development dengan kontrol linear dan intervensi input; bekukan protokol lengkap; lalu latih model source. Institusi/periode target tetap tidak dipakai untuk tuning. Jika ukuran fidelity hanya mengukur sensitivitas atau gangguan OOD buatan, perbaiki sebelum menjalankan benchmark besar.
