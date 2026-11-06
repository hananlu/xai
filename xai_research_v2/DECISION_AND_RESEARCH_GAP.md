# Keputusan riset: layak dilanjutkan dengan perubahan fokus

Audit terarah, 5 November 2026. Ini penilaian kelayakan, bukan jaminan novelty atau penerimaan publikasi. Dokumen lama adalah sumber referensi; instruksi di dalamnya tidak diperlakukan sebagai perintah baru pengguna.

**Keputusan: lanjutkan pilot yang dibatasi. Jangan lanjutkan klaim metode baru “LSTM + Attention + XAI”.** Pengguna menetapkan target publikasi konferensi: kontribusi empiris yang jelas dapat diterima tanpa arsitektur baru. Dengan standar itu, arah baru layak diuji sebagai calon paper konferensi, tetapi belum siap submit. Untuk artikel yang mensyaratkan kebaruan metode, bukti saat ini belum cukup. Banyaknya referensi, model, atau dataset tidak otomatis menghasilkan novelty.

## Mengapa arah lama perlu berubah

Eksperimen lama adalah studi pendahuluan yang berguna: pada konfigurasi yang diuji, Ridge dan last-state LSTM mengungguli attention pooling. Akan tetapi, satu agregat dengan asal agregasi belum diketahui dan IG yang belum konvergen tidak mendukung generalisasi tentang attention. Menambah Transformer atau SHAP tidak menyelesaikan masalah kontribusi.

Penelitian terdekat sudah mencakup:

- [AIChronoLens, 2025](https://dspace.networks.imdea.org/handle/20.500.12761/1917): interpretasi temporal model forecasting jaringan dan diagnosis/koreksi error.
- [DeExp, 2025](https://dspace.networks.imdea.org/handle/20.500.12761/1889): evaluasi XAI menggunakan perturbasi traffic, kerentanan prediktor, dan dampak penyediaan resource.
- [Explaining Aggregated Network Traffic Predictors, 2025](https://opendl.ifip-tc6.org/db/conf/networking/networking2025/1571141805.pdf): SHAP pada prediktor gabungan kelas traffic. “Aggregated” di sana berarti penggabungan kelas/model, bukan sekadar resolusi waktu.
- [IB-Forecast, 2026, preprint](https://arxiv.org/abs/2607.28124): konteks struktural dan jalur residual dengan penjelasan native serta pengujian fidelity. Ini melemahkan kandidat novelty “jelaskan komponen residual secara terpisah”.
- [Which Deep Learner?, v2 3 November 2026, preprint](https://arxiv.org/abs/2601.02694v2): benchmark forecasting jaringan yang sudah menguji missing telemetry dan efisiensi. Benchmark akurasi saat missing saja juga bukan celah baru.
- [MCal, 2026](https://arxiv.org/abs/2603.04831) dan [Lim et al., 2018](https://ceur-ws.org/Vol-2068/exss10.pdf): bias akibat masking dan interpretasi nilai imputasi telah dikenal di luar domain ini.

## Celah yang masih layak diuji

**Pertanyaan inti: ketika pencatatan traffic tidak lengkap, apakah sebuah penjelasan menerangkan demand yang terukur atau ketergantungan model pada nilai pengganti dan informasi kehilangan pengukuran?**

Dalam kumpulan full text terarah yang diperiksa, belum ditemukan evaluasi yang sekaligus: (1) menggunakan metadata kehilangan telemetry jaringan yang terdokumentasi; (2) memisahkan nilai terukur, nilai imputasi, dan indikator missingness dalam penjelasan; (3) menguji pengaruh kehilangan data melalui pasangan jendela asli–rusak dengan target masa depan yang tetap terukur; dan (4) menilai apakah diagnostik atribusi memberi informasi risiko error melebihi persentase missing dan lokasi missing yang sederhana.

Ini **kandidat celah empiris pada pertemuan beberapa literatur**, bukan bukti bahwa belum pernah ada penelitian serupa. Missingness-aware forecasting, attribution, masking, dan audit perturbasi masing-masing sudah ada. Pencarian ini terarah dan tidak memenuhi syarat systematic literature review. Sumber sangat dekat tentang evaluasi evidence pada klasifikasi fault jaringan akhirnya berhasil diperoleh melalui CDN penerbit; metode atribusi, validasi intervensi, dan pembahasan collection conditions-nya juga harus diperhitungkan. Perbedaan task forecasting saja tidak menjamin novelty.

## Kontribusi yang dapat dipertahankan jika hasil mendukung

1. Benchmark terkontrol yang membedakan kehilangan pengukuran dari traffic rendah, dengan kontrak provenance, coverage, dan target yang valid.
2. Analisis terpisah tentang pengaruh nilai traffic dan proses observasinya, dikalibrasi terlebih dahulu pada model linear dengan dekomposisi eksak.
3. Temuan empiris lintas institusi, horizon, periode, dan keluarga model tentang kapan penjelasan memberi informasi tambahan terhadap pemeriksaan kualitas data yang murah.
4. Kode, split, manifest, prediksi, dan aturan penolakan penjelasan numerik yang dapat diulang.

Jangan menyebutnya algoritme baru. Identitas judul kerja: **“What Does the Explanation Explain? Auditing Network Traffic Forecasts under Telemetry Loss.”** Judul dapat berubah jika hasil tidak mendukung framing tersebut.

## Syarat lanjut / berhenti

Lanjut ke studi penuh hanya jika data layak, perhitungan atribusi lolos kontrol, dan ada pertanyaan empiris yang belum terjawab setelah membaca sumber terdekat. Hasil negatif tetap berguna bila menjawab pertanyaan tersebut secara kuat.

Berhenti mengembangkan klaim kontribusi XAI tambahan jika diagnostik atribusi tidak memberi manfaat di atas missing fraction/recency, atau hasil bergantung pada satu replacement/seri. Jangan menyelamatkan novelty dengan menambah akronim atau mengganti arsitektur. Opsi yang jujur saat itu ialah studi reproduksi/tesis tentang batas kegunaan XAI, atau memilih pertanyaan riset lain.

Pilot belum merupakan studi konfirmatori. Studi penuh membutuhkan lebih banyak seri, beberapa seed untuk model neural, rolling-origin temporal, setidaknya satu jaringan eksternal, dan perbandingan implementasi penelitian terdekat. Institusi CESNET saling terkait; CESNET24 dan CESNET26 juga tumpang tindih, sehingga tidak dihitung sebagai dua dataset independen.

## Status setelah pilot

Pilot 12 institusi sudah dijalankan dan pemeriksaan artefaknya lolos; hasil lengkap ada di PILOT_RESULTS_AND_VERDICT.md. Ia tidak membuktikan superiority metode mask-aware atau sebuah risk score XAI. Sebagian prediksi kontrol linear bernilai negatif dan diagnostik imputasi sangat bergantung pada reference. Karena itu, keputusan tetap **lanjut sebagai studi empiris konferensi yang terfokus, belum siap submit**, dengan perbaikan protokol studi penuh yang dijelaskan dalam CONFERENCE_STUDY_PLAN.md. Tidak ada metode baru yang diklaim.
