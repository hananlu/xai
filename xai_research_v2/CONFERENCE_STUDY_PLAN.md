# Rencana menuju paper konferensi

Target ditetapkan pengguna pada 5 November 2026: paper konferensi dengan research gap yang nyata; arsitektur baru tidak wajib. Belum ada venue/deadline tertentu yang dipilih, sehingga tidak ada janji penerimaan atau batas halaman/deadline yang diasumsikan.

## Argumen paper yang hendak dibuktikan

Masalah operasional: operator melihat forecast dan explanation, tetapi sebagian history berasal dari kehilangan telemetry dan nilai pengganti. Model bisa dijelaskan dengan benar secara matematis namun explanation itu tidak membuktikan bahwa informasi demand aslinya tersedia atau prediksinya dapat diandalkan.

Kontribusi empiris harus menjawab **kapan dan seberapa besar masalah ini terjadi**, apakah teknik XAI memberi diagnosis tambahan, dan kontrol murah apa yang cukup. Menemukan bahwa salah satu metode gagal pada satu grafik tidak cukup.

## Tahapan dan keluaran

1. Audit terarah penelitian terdekat + keputusan worth/not-worth. Sediakan matriks tumpang tindih dan status bacaan, bukan sekadar menambah daftar pustaka.
2. Dataset resmi + protokol pilot yang dibekukan sebelum hasil. Verifikasi archive checksum, time IDs, coverage dan selected institutions.
3. Pilot kontrol linear: apakah intervensi/atribusi benar secara numerik, apakah pola loss/replacement memberi perilaku berbeda, apakah diagnostik dasar memiliki keterbatasan yang perlu diuji di model neural.
4. Protokol studi penuh baru: severity-varying loss, beberapa keluarga model, augmentation/mask ablation, beberapa periode dan jaringan eksternal. Bekukan analisis utama serta outcome yang disisihkan sebelum membuka hasilnya.
5. Jalankan studi penuh, uji sensitivitas, serta perbandingan dekat. Jika novelty empiris tidak muncul, framing tetap studi batas/replikasi; jangan memaksakan klaim superiority.
6. Tulis paper dari hasil: problem -> prior work/gap -> protocol -> forecast results -> explanation/decision results -> threats to validity. Gunakan hasil v1 hanya sebagai motivasi/preliminary evidence, dengan label dan keterbatasannya.
7. Buat PPT: slide 1 opening; slide 2 gap dan goal; slide 3 diagram pipeline; slide 4 dan seterusnya hasil nyata. Pengguna meminta PPT nanti, sehingga tahap ini belum dikerjakan sekarang.

Pilot bukan hasil konfirmatori dan bukan seluruh eksperimen akhir. Periode reserved tetap unscored pada tahap ini. Kontribusi konferensi dinilai dari argumen dan bukti, bukan model yang paling rumit.

## Detail XAI untuk protokol studi penuh

Mulai dengan model dan penjelasan yang dapat dikalibrasi, lalu gunakan keluarga neural sebagai uji generalitas. Paket minimal: Ridge dengan dekomposisi eksak; satu forecaster linear/decomposition seperti DLinear; satu GRU/LSTM; dan satu patch forecaster bila sumber daya cukup. Seasonal-naive wajib. Model attention dapat tetap menjadi pembanding, tanpa dijadikan solusi yang harus menang.

Penjelasan: kontribusi linear eksak, grouped/block occlusion, IG yang lolos konvergensi dan completeness per kasus, serta grouped Shapley jika biaya memungkinkan. Sebagai contoh, tujuh kelompok harian pada history satu minggu memungkinkan enumerasi 128 coalitions untuk attribution tingkat hari, dengan semantics replacement yang eksplisit. Itu attribution antarkelompok; jangan menamainya penjelasan setiap lag atau conditional SHAP tanpa conditional sampler. Pembanding random, recency dan koefisien/sensitivity sederhana tetap diperlukan.

Reference explanation dan replacement telemetry perlu divariasikan sebagai faktor terpisah. Perturbasi yang menghasilkan ranking tidak boleh menjadi satu-satunya operator yang menilai ranking tersebut. IG gagal toleransi harus dilaporkan sebagai kegagalan numerik, bukan dimasukkan ke ranking kemenangan. Perhitungan kontribusi harus mencakup skip/normalization/mask path yang dinyatakan; conditional explanations diperbolehkan apabila konteks yang dibekukan diungkapkan.

Keputusan model tuning dan evaluasi XAI tidak memakai outcome reserved. Aturan final mengenai severity, sampel explanation, kriteria numerik, pembanding prior work, biaya komputasi dan analisis utama harus masuk protokol studi penuh yang baru sebelum reserved outcomes dibuka. Detail ini merupakan rencana lanjutan, bukan bagian dari eksperimen pilot yang sudah dibekukan.

## Penyesuaian rencana setelah pilot, tanpa mengubah hasil pilot

Pilot menunjukkan dua prioritas studi penuh. Pertama, Ridge linear kontrol menghasilkan prediksi negatif pada sebagian origin; evaluasi forecaster volume operasional memerlukan output nonnegatif. Bila fungsi prediksi di-clamp/ditransformasi, penjelasan harus mengikuti fungsi akhir tersebut, sedangkan dekomposisi linear pilot tetap dilabeli sebagai kontrol untuk fungsi unclipped.

Kedua, konfigurasi mask+augmentation tidak otomatis meningkatkan robustness. Studi penuh harus memisahkan augmentation dari akses mask dan mengevaluasi trade-off clean/stress pada validation saja. Masker training independen target, severity validation ditetapkan lebih dahulu, dan budget tuning antar metode disamakan. Pilihan konfigurasi yang hanya dinilai melalui clean validation tidak menjamin kinerja saat kehilangan telemetry. Hasil pilot yang buruk tetap dilaporkan.
