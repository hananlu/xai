# Pilihan utama: cross-institution attribution reliability

Keputusan 5 November 2026, setelah pengguna meminta memilih satu arah terbaik. Dokumen ini menggantikan prioritas deadline-aware recovery pada RECOMMENDED_DIRECTION.md; proposal itu tetap disimpan sebagai alternatif. Eksperimen v1/v2 tidak diubah atau diklaim sebagai eksperimen transfer.

## Judul kerja yang dipilih

**Cross-Institution Reliability of Temporal Attributions in Network Traffic Forecasting**

Judul teknis dan deskriptif. “Temporal attributions” membatasi objek penelitian pada kontribusi kelompok lag terhadap output forecast, bukan semua bentuk explanation. Ini keputusan scope, bukan klaim bahwa judul atau keseluruhan topik belum pernah diteliti.

## Alasan dipilih

Arah ini memiliki keseimbangan terbaik untuk kondisi proyek: fokus forecasting + XAI tetap jelas; data multi-institusi resmi sudah tersedia; tidak perlu mengasumsikan adanya buffer retrieval, latency produksi atau deadline yang belum terukur; serta ada pertanyaan empiris yang dapat diuji dengan pemisahan institusi dan waktu.

Pemilihan ini bukan peringkat probabilitas diterima konferensi. Novelty terarahnya belum terkonfirmasi. Meneliti transfer forecasting atau penjelasan di bawah distribution shift secara umum sudah mempunyai prior art.

## Pertanyaan utama

**Ketika forecaster dipindahkan ke institusi yang tidak digunakan dalam training, apakah temporal attribution tetap merepresentasikan ketergantungan model secara andal, dan bagaimana hasil itu berbeda dari perubahan akurasi forecast?**

Dua hasil harus dibedakan:

1. **Forecast accuracy:** apakah prediksi mendekati volume yang terukur?
2. **Attribution fidelity:** apakah penjelasan sesuai pengaruh input pada fungsi model yang dinyatakan?

Model dapat salah memprediksi tetapi dijelaskan dengan tepat. Perubahan ranking antar institusi dapat masuk akal; ranking yang stabil juga dapat mengikuti ketergantungan model yang buruk. Karena itu, kesamaan heatmap, kestabilan ranking atau confidence saja tidak menjadi bukti penjelasan berkualitas. Tidak diasumsikan bahwa explanation pasti memburuk setelah transfer.

## Kontribusi empiris yang hendak dibuktikan

- Evaluasi transfer yang memisahkan **institusi baru** dari **periode baru**, dengan provenance dan coverage yang jelas.
- Pengukuran terpisah atas forecast error, fidelity atribusi, dan perubahan pola ketergantungan model, menggunakan kontrol linear eksak.
- Analisis sensitivitas terhadap reference source dan reference dari history target yang sudah tersedia; attribution dengan reference berbeda merupakan pertanyaan kontras yang berbeda dan tidak otomatis dapat dinilai salah hanya karena ranking berubah.
- Bukti tentang apakah adaptasi terbatas pada institusi target mengubah akurasi dan fidelity secara sejalan atau berbeda.

Benchmark dan temuan harus menambah pengetahuan di luar aplikasi metode yang sudah ada. Tidak ada “first”, algoritme baru, superiority atau kepastian publikasi yang diklaim sekarang.

## Pesaing dan batas research gap

| Sumber primer | Overlap yang harus dihormati | Fokus pembeda yang akan diperiksa |
|---|---|---|
| [TransMUSE, 2022](https://arxiv.org/abs/2203.02083) | Transfer prediktor traffic antar area/cohort sudah diteliti. Primary abstract dan uraian framework tersedia. | Evaluasi kualitas temporal attribution ketika prediktor ditransfer; transfer accuracy sendiri bukan novelty. |
| [AIChronoLens, 2025](https://dspace.networks.imdea.org/handle/20.500.12761/1917) | Penjelasan temporal dan diagnosis/koreksi error forecast jaringan sudah diteliti; bagian relevan full text diperiksa dalam audit sebelumnya. | Desain source/target institution yang disjoint, kontrol fidelity dan reference portability. |
| [TimeSAE, preprint 2026](https://arxiv.org/abs/2601.09776) | Faithful time-series explanation dan robustness di luar training support sudah menjadi topik langsung. Pemeriksaan saat pemilihan ini pada primary abstract/search-accessible manuscript; full-text comparison masih wajib. | Jangan mengklaim sebagai penelitian pertama explanation under shift. Perlu perbandingan konkret dengan eksperimen dan definisi fidelity mereka. |
| [Explanation audits under shift, 2026](https://link.springer.com/article/10.1007/s44163-026-02012-6) | Penjelasan dapat tetap stabil ketika model bergantung pada shortcut; audit shift dan ketidakselarasan accuracy/attribution sudah diteliti pada klasifikasi tabular. Bagian scope dan metode tersedia dalam full text HTML. | Evaluasi transfer institusi pada forecasting temporal, dengan perhatian pada dependensi waktu dan operator intervensi. Adaptasi domain saja belum cukup membuktikan novelty. |

Status gap: **kandidat empiris pada evaluasi deployment lintas institusi**, dengan overlap yang sudah diketahui. Pencarian terarah tidak membuktikan ketiadaan paper identik. Audit pesaing tersebut harus selesai sebelum eksperimen konfirmatori atau klaim novelty final.

## Rancangan pipeline yang diprioritaskan

Dataset: CESNET-TimeSeries26 resmi, n_bytes hourly dengan time mapping dan coverage 10 menit. Institusi CESNET berasal dari satu ISP; sebut generalisasi lintas institusi, bukan lintas operator jaringan independen. CESNET24 bertumpang tindih sehingga bukan replikasi jaringan eksternal.

1. **Development:** 12 institusi pilot yang sudah diperiksa dipakai untuk debugging/calibration. Hasil pilot lama tidak menjadi bukti transfer.
2. **Split institusi:** pilih source, validation dan target institution yang benar-benar disjoint melalui aturan training-only yang dibekukan. Ukuran awal yang direncanakan: 32 source, 8 validation dan 8 target baru, di luar 12 development jika memenuhi eligibility. Pemilihan ini belum dieksekusi; jumlah final mengikuti audit coverage dan komputasi, lalu dibekukan sebelum hasil target.
3. **Split waktu:** training source 2024; validation pada institusi validation memakai periode development yang ditetapkan; April 2025–Juni 2026 tetap unscored untuk evaluasi temporal berikutnya. Jangan memakai target evaluation period untuk memilih metode/reference/model.
4. **Model:** persistence/seasonal-naive, Ridge sebagai kontrol, DLinear dan GRU sebagai pembanding awal, tiga seed untuk model neural. Tambahkan patch model bila diperlukan untuk menjawab RQ. Forecaster operasional memakai output nonnegatif; fidelity harus sesuai fungsi akhirnya. Dekomposisi Ridge unclipped tetap kontrol terpisah.
5. **Deployment:** frozen source-trained forecaster pada source dan target institutions; lalu arm adaptasi terbatas dengan target past data yang dinyatakan. Zero-shot dan adaptation harus dilabeli terpisah. Normalisasi target hanya memakai history yang tersedia saat forecast, bukan statistik masa depan.
6. **Attribution:** kelompok lag dengan ukuran sama, kontrol linear eksak, IG dengan kriteria konvergensi, serta block occlusion/grouped Shapley sesuai budget. Jelaskan fungsi, reference, horizon dan preprocessing yang diterangkan.
7. **Evaluasi:** MAE/MASE; fidelity terhadap input interventions yang eksplisit; completeness/convergence; random/recency controls; ranking/reference sensitivity sebagai hasil deskriptif. Operator pembentuk ranking dan operator evaluasi tidak boleh hanya satu replacement identik. Large deletion effect saja bukan kebenaran kausal tentang demand.
8. **Analisis:** unit institusi dan blok waktu, matched origins, hasil per institusi, dependence satu ISP, serta interaksi source/target dengan metode. Jangan memperlakukan seed atau ribuan overlapping windows sebagai jaringan independen.

## Langkah berikutnya

Selesaikan perbandingan full text TransMUSE dan TimeSAE terhadap protokol di atas, tetapkan definisi fidelity dan pembandingnya, lalu lakukan feasibility run pada development institutions. Setelah itu bekukan protokol baru dan baru gunakan institusi/periode target. Tidak ada training transfer atau evaluasi target baru yang dilakukan hanya untuk memilih judul ini.

Jika gap ternyata sudah terjawab atau ukuran fidelity tidak mampu membedakan kualitas explanation dari sensitivitas model, revisi pertanyaan sebelum memperbesar eksperimen. Pilihan arah sekarang memungkinkan pekerjaan fokus sambil tetap menjaga keputusan ilmiah dapat dikoreksi oleh bukti.
