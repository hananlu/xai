# Ringkasan hasil dan keputusan riset

**Studi inti sudah selesai dijalankan.** Judul: *Cross-Institution Reliability of Temporal Attributions in Network Traffic Forecasting*.

Dataset final adalah CESNET-TimeSeries26, bukan gabungan capture Westermo/BigFlows/botnet/VPN/Tor. Kita memakai 48 institusi: 32 training, 8 validasi, 8 target yang tidak masuk gradient fitting. Data resmi dan atribusinya tersedia di [Zenodo](https://doi.org/10.5281/zenodo.21945629). Target forecasting adalah volume GB per jam pada endpoint 1 dan 6 jam dari history 168 jam; ini bukan klasifikasi malware/VPN.

## Hasil yang aman diklaim

1. **Hipotesis primer belum konklusif.** Selisih target–source Q = -0,0189; nominal 95% CI [-0,0891; +0,0533]. Tujuh pasangan lengkap; satu pasangan tidak punya observasi eligible bersama di 2026. Kita belum membuktikan penurunan konsisten, dan juga belum membuktikan kesetaraan.
2. **Model sederhana kompetitif.** Target MASE 1 jam: Ridge 0,681; DLinear 0,682; GRU 0,684. Enam jam: 0,813; 0,812; 0,909. Angka deskriptif, tanpa klaim signifikansi ranking model.
3. **Reference dan operator memengaruhi hasil.** Pada history-hour-median, beberapa interval sekunder berada di bawah nol. Hasil sekunder tidak dikoreksi multiplicity dan tidak menggantikan hipotesis primer. Perubahan reference juga mengubah pertanyaan kontrastifnya.
4. **Numerik IG perlu dilaporkan.** 210 dari 3.360 kasus tidak lolos toleransi yang dibekukan. Kasus tetap disimpan; tidak diberi skor IG. Ini bukan bukti bahwa IG secara teori salah atau bahwa Shapley selalu lebih baik.

Q mengukur apakah ranking memilih grup yang menimbulkan respons model besar di bawah replacement tertentu. Q bukan causal truth, bukan peluang model salah, dan bukan pengganti akurasi forecast. Interpolation dan rotation adalah controlled operators, bukan jaminan sampel traffic alami.

## Research gap dan novelty

Transfer forecast sudah diteliti oleh TransMUSE; XAI forecasting jaringan oleh AIChronoLens; explanation generalization oleh TimeSAE (ICML 2026). Kita tidak boleh mengklaim pertama pada tiga topik tersebut. Novelty empiris yang bisa dipertahankan adalah kombinasi setting deployment institusi yang disjoint, paired timestamps, reference eksplisit, validasi numerik terpisah, dan inference yang memperhitungkan pasangan serta blok waktu. Ini kontribusi evaluasi, bukan algoritma baru.

**Penilaian saya: masih worth untuk paper empiris yang cakupannya sesuai, tetapi belum merupakan novelty metode yang kuat atau jaminan diterima konferensi.** Kelemahan terbesar: hanya satu ISP dan tujuh pasangan efektif, incomplete coverage, dua replacement operator yang belum divalidasi sebagai conditional distribution, serta pembanding explainer terbatas. Untuk target konferensi yang sangat kompetitif, prioritas berikutnya adalah replikasi independen di network kedua dan replacement yang lebih realistis, dengan protokol baru. Jangan mencari setting signifikan dari target yang sudah dibuka untuk mengganti headline studi ini.

## Yang sudah tersedia

- Draft paper Inggris 5 halaman, 18 referensi, source LaTeX.
- PPT 12 slide editable: opening; research gap/goal; pipeline; hasil dan batas.
- Dataset turunan 48 institusi, checkpoint, prediction per origin, attribution allocations, semua numerical rejection, protocol/hash manifests dan scripts.
- Audit akhir lolos: 48 data hash, model hash, semua forecast metrics, re-query checkpoint/label, Shapley permutation checks, dan titik estimasi primer.

## Keputusan yang masih perlu dari author

Tentukan target konferensi dan nama/afiliasi author agar format, batas halaman, anonymization serta disclosure dapat disesuaikan. Versi saat ini adalah anonymous research draft untuk review; belum disubmit. Jika menginginkan klaim lintas jaringan yang lebih kuat, itu memerlukan studi lanjutan baru dan tidak bisa disimpulkan dari hasil sekarang.

Dua ide paper yang berbeda: **Conditional History Replacement for Network Forecast Explanations** (replacement distribusional + validasi network kedua), dan **Numerical Reliability of Path Attributions in Nonnegative Forecasting** (clipping/unit output/integrasi, dengan kontribusi lebih jauh dari pengecekan completeness). Keduanya masih ide, belum hasil atau novelty yang terverifikasi penuh; jangan membagi tabel studi yang sama menjadi paper berulang.
