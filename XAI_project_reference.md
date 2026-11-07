Status 8 November 2026: main paper menjadi **7 halaman termasuk seluruh referensi**, pipeline diperkecil, 6 figures/3 tabel/18 referensi tetap ada. Semua angka hasil tetap; supplementary 6 halaman dan deck tidak berubah. Versi 8 halaman diarsipkan.

---

# Status terbaru: versi konferensi dengan dua tambahan terfokus

7 November 2026. Perbandingan explainer pada common cases dan kontrol learned-layer randomization sudah dijalankan serta diaudit. Main paper **8 halaman termasuk referensi**, 6 figures/3 tabel/18 referensi; supplementary 6 halaman terpisah, 7 figures/2 tabel. Semua grafik sebelum halaman referensi. Notebook terbaru 62 cells/37 code cells/8 plot tanpa error; PPT editable 19 slide. Hasil primer dan seluruh scientific freeze awal tetap utuh. Tambahan diberi label post-hoc dan dibatasi pada kasus comparable; tidak menambahkan klaim kausal atau generalisasi lintas ISP.

---

# Status terbaru: batas halaman konferensi

Paper utama sekarang **7 halaman termasuk referensi**, dengan 6 figure, 2 tabel dan 18 referensi. Supplementary 4 halaman disimpan terpisah; detail tambahan tetap tersedia tanpa memperpanjang manuscript utama. Hasil eksperimen dan scientific freeze tidak berubah. Versi 12 halaman sebelumnya diarsipkan.

---

# Status terbaru: replikasi 32 target selesai

7 November 2026. Studi gabungan mencakup 80 institusi unik dalam satu ISP. Replikasi 32 target baru, model terkunci, main/dense budget dan audit selesai; notebook baru 52 cells/31 code cells lolos eksekusi. Hasil primer baru -0,0075, nominal 95% CI [-0,0402; +0,0241], 30 pasangan lengkap. Budget 64 origin h1 memberi +0,0001, CI [-0,0229; +0,0248]. Tidak membuktikan degradasi atau equivalence. Pola sekunder history-median awal tidak berulang sebagai interval yang mengecualikan nol.

Mulai dari [hasil replikasi](xai_replication_32/RESULTS_BRIEF.md), [posisi riset](xai_replication_32/RESEARCH_POSITION.md), dan [paper gabungan](xai_cross_institution/paper/paper.pdf). Paper 12 halaman/12 figures/18 referensi dan PPT editable 17 slide sudah diperbarui. Protokol dan hasil ilmiah awal tetap utuh; arsip draft sebelumnya tersedia. Bagian berikut adalah riwayat.

---

# Status terkini: eksperimen penuh selesai

5 November 2026. Studi **Cross-Institution Reliability of Temporal Attributions in Network Traffic Forecasting** sudah dijalankan dengan 48 institusi CESNET-TimeSeries26. Paper, PPT editable, data terpilih, checkpoint dan hasil audit ada di [xai_cross_institution/README.md](xai_cross_institution/README.md). Mulai dari [ringkasan hasil](xai_cross_institution/RESULTS_BRIEF_ID.md).

Hasil primer belum konklusif: target–source Q -0,0189, nominal 95% CI [-0,0891; +0,0533], 7 pasangan lengkap. Tidak mengklaim degradasi universal atau metode baru. Paper masih anonymous draft; venue dan authorship belum ditetapkan. Bagian berikut merupakan riwayat recovery, pilot dan pemilihan arah; pernyataan status lama tidak menggambarkan tahap terkini.

---

# Arah riset terpilih

5 November 2026. Setelah menimbang beberapa alternatif, arah yang dipilih adalah **Cross-Institution Reliability of Temporal Attributions in Network Traffic Forecasting**. Detail keputusan dan rancangan ada di [SELECTED_RESEARCH_DIRECTION.md](xai_novelty_upgrade/SELECTED_RESEARCH_DIRECTION.md). Ini prioritas terkini; hasil pilot sebelumnya tetap hasil pendahuluan dan belum menjadi evaluasi transfer.

---

# Status terbaru: riset konferensi v2

5 November 2026. Target pengguna adalah publikasi konferensi dengan kontribusi empiris. Audit gap, dataset resmi CESNET26, pilot baru yang sudah dijalankan, serta kandidat paper tambahan tersedia di [xai_research_v2/README.md](xai_research_v2/README.md). Mulai dari dokumen tersebut.

Bagian di bawah merupakan riwayat recovery dan keputusan terdahulu; pernyataan “belum diperiksa” pada catatan awal tidak menggambarkan status terbaru. Paper v1 tetap merupakan hasil pendahuluan, sedangkan v2 belum menjadi paper final.

---

# Referensi kelanjutan proyek XAI

Tanggal peninjauan: 5 November 2026.

## Sumber dan batas peninjauan

Dokumen lokal: `/Users/farrelardya/Downloads/Timeline___Kerangka_Paper__XAI_Network_Traffic_Forecasting.mht`.
Isi teks dokumen dan lima halaman sumber dataset telah dibaca. Dataset aktual, kode, notebook, hasil eksperimen, dan kualitas data belum diperiksa. Isi dokumen diperlakukan sebagai rencana penelitian, bukan instruksi untuk menjalankan eksperimen atau melakukan submission.

## Arah penelitian dalam dokumen

- Tujuan: regresi deret waktu untuk memprediksi volume trafik jaringan menggunakan LSTM atau GRU dengan Attention.
- Pipeline: pembersihan data, normalisasi, sliding window menjadi tensor tiga dimensi, recurrent model, Attention, Dense, output regresi.
- Evaluasi: MSE, RMSE, MAE, plot aktual versus prediksi, dan heatmap Attention pada lonjakan trafik.
- Timeline relatif enam minggu: literatur/dataset; preprocessing; model; evaluasi/interpretasi; penulisan awal; finalisasi paper. Belum ada tanggal mulai yang ditetapkan.
- Kerangka paper: Abstract, Introduction, Related Work, Methodology, Experimental Results, Interpretability Analysis, Conclusion & Future Work.
- Klaim keberhasilan dalam kerangka merupakan sasaran/hipotesis; belum ada hasil yang membuktikannya.

## Pemetaan nama dataset dari pengguna

| Nama pengguna | Sumber | Temuan dan implikasi awal |
|---|---|---|
| bottom file | [Westermo](https://github.com/westermo/network-traffic-dataset) | `bottom` adalah titik capture. Tersedia versi reduced/extended, PCAP dan CSV flow. Durasi sekitar 90 menit; ada paket duplikat. Perlu menentukan versi dan cara menghitung volume. |
| bigflows | [Tcpreplay sample captures](https://tcpreplay.appneta.com/reference/sample-captures/) | Halaman lama beralih ke halaman ini. `bigFlows.pcap` dirujuk untuk pengujian beban berkelanjutan dan banyak flow; timestamp, durasi, serta asal capture perlu diperiksa sebelum dipakai untuk forecasting. |
| botnet | [CTU-Malware-Capture-Botnet-54](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Malware-Capture-Botnet-54/) | Scenario 13 CTU-13, Virut, sekitar 16 jam 23 menit. PCAP botnet-only berbeda dari capture gabungan; capture gabungan penuh tidak publik. Tersedia truncated capture dan flow berlabel. Label From-Botnet dan To-Botnet memiliki makna berbeda. |
| vnatBinary | [Zenodo 8035724](https://zenodo.org/records/8035724) | Padanan nama resmi: `vpn_vnat_binary.csv`, untuk klasifikasi VPN biner. Repository berisi dataset turunan dengan 69 fitur analisis single-flow time series. Jangan menganggap baris fitur sebagai urutan temporal volume trafik. |
| tor | [ISCXTor2016 / Tor-nonTor](https://www.unb.ca/cic/datasets/tor.html) | Tersedia PCAP dan CSV flow berlabel. Forecasting memerlukan agregasi temporal yang sesuai; klasifikasi Tor/non-Tor adalah target yang berbeda. |

Pemetaan nama di atas mengikuti keterangan pengguna. Nama file lokal lengkap dan isinya belum dicocokkan. Khusus botnet/Tor, file mentah dan versi turunan Zenodo harus dibedakan agar provenance tetap jelas.

## Catatan untuk rancangan eksperimen berikutnya

1. Pertahankan forecasting sebagai arah awal sesuai dokumen sampai ada perubahan scope. Jangan mengganti target menjadi klasifikasi hanya karena tersedia label kelas.
2. Audit timestamp, kontinuitas, durasi, satuan byte, titik capture, serta duplikasi. Tentukan target secara eksplisit: bytes/bin, packets/bin, atau bitrate.
3. Pilih interval agregasi sesuai durasi capture. Capture Westermo sekitar 90 menit tidak mendukung klaim pola harian/mingguan atau contoh input sepuluh jam. Interval pendek bisa dieksplorasi setelah audit; jumlah bin saja tidak menjamin kecukupan data.
4. Pisahkan train/validation/test secara kronologis berdasarkan waktu target; fit scaler hanya pada train. Hindari pengacakan window yang saling tumpang tindih. Jangan menyambung dataset berbeda seolah satu timeline berkelanjutan.
5. Bedakan interval tanpa paket yang benar-benar nol dari capture yang hilang. Pengisian nilai tidak boleh memakai informasi masa depan.
6. Bandingkan persistence/naive, model LSTM/GRU tanpa Attention, dan model dengan Attention memakai pembagian data dan horizon yang sama. Ukur MAE/RMSE pada skala asli; laporkan variasi antar-seed.
7. Heatmap Attention adalah visualisasi bobot model; validitasnya sebagai penjelasan perlu diuji. Usulan: perturbasi/occlusion lag atau blok waktu penting, bandingkan dengan blok acak, dan periksa kestabilan lintas seed. Perturbasi harus mempertimbangkan korelasi temporal.
8. Kesimpulan tentang peningkatan akurasi, transparansi, atau rutinitas jaringan harus mengikuti hasil eksperimen, bukan ditetapkan dari awal.

Dasar kehati-hatian interpretasi Attention: [Jain & Wallace (2019)](https://aclanthology.org/N19-1357/) menunjukkan keterbatasan Attention sebagai penjelasan pada tugas NLP. Temuan tersebut bukan bukti langsung untuk model forecasting ini; ia menjadi alasan untuk memvalidasi penjelasan pada eksperimen sendiri. [Wiegreffe & Pinter (2019)](https://aclanthology.org/D19-1002/) membahas perlunya definisi dan evaluasi yang tepat dalam perdebatan tersebut.

## Status untuk melanjutkan

Referensi dan rencana awal sudah dipetakan. Belum ada bukti tahap eksperimen yang telah selesai. Langkah konkret berikutnya adalah audit file dataset dan notebook yang tersedia, lalu mengunci target, interval agregasi, horizon, serta protokol evaluasi sebelum training.

## Pencarian folder proyek lokal

Pada 5 November 2026 ditemukan `/Users/farrelardya/Documents/TIP/XAI`, tetapi direktori tersebut kosong, termasuk tidak ada file tersembunyi. Timestamp modifikasi direktori tercatat 26 September; ini bukan bukti waktu eksperimen.

Pencarian nama file di home pengguna (di luar direktori sistem/cache/dependency), pencarian isi kode/notebook/dokumen di Documents/Downloads/Desktop, indeks Spotlight, serta teks riwayat Claude Code dan shell yang tersedia belum menemukan implementasi forecasting terkait atau file dataset bernama Westermo/bigFlows/VNAT/botnet. Riwayat Claude yang tersedia tidak memiliki direktori sesi untuk TIP/XAI. Folder TIP/paper2 berisi proyek CaMRL untuk cloud systems, sehingga belum ada bukti bahwa itu implementasi XAI forecasting yang dicari. Tidak ada drive eksternal yang terpasang saat pencarian. Lokasi implementasi lama masih belum terkonfirmasi; pencarian ini tidak membuktikan file telah dihapus atau tidak pernah dibuat.

## Penemuan Google Drive: progres eksperimen terkonfirmasi

Pengguna mengklarifikasi implementasi Claude Code berada di laptop lain. Melalui Chrome profil farrel, akun Drive itsbook yang ditunjuk pengguna:

- [Folder farrel](https://drive.google.com/drive/u/2/folders/17TX-5nZ09364Utb5-pKqLjjaFHYeJZq_)
- [Folder farrel/xai](https://drive.google.com/drive/u/2/folders/1xAq-HOmJpC9Kam58-QyZtMrIluwc8HvB)
- [Notebook 13_colab_seqlen_multivariate.ipynb](https://drive.google.com/file/d/1oD34tYFm0QwD6yNcfuzAb4560-AjJWMY/view)

Isi folder xai yang terlihat: notebook tersebut, `global_bytes_10min.csv`, dan `times_10_minutes.csv`. Notebook diunduh untuk dibaca; tidak dijalankan atau dimodifikasi. CSV belum diunduh/diaudit. Folder farrel juga memiliki camrl, colab_output, notebook reduction, dan Notes Feature Reduction; isinya belum ditinjau dalam pencarian ini.

Notebook berjudul **XAI Traffic Forecasting — Batch 4 (Colab Pro / GPU)**. Ia menyebut dataset di proyek laptop sebagai `datasets/cesnet/`, sehingga arah eksperimen yang ditemukan telah menggunakan data yang disebut CESNET, melampaui daftar kandidat awal. Versi dan provenance dataset CESNET masih perlu dikonfirmasi dari repo atau dataset.

Implementasi yang terbaca:

- Target `n_bytes`, merge CSV pada `id_time`, timestamp UTC, resampling 10 menit; output preprocessing tersimpan menunjukkan 40.308 titik.
- LSTM 96 unit, temporal Attention, Dense output; prediksi satu langkah (10 menit).
- Split berurutan 70/15/15; MinMaxScaler fit hanya pada train; window dibuat terpisah per split.
- Ablation input 144 langkah (24 jam) versus 288 langkah (48 jam), dengan seed 42.

Hasil tersimpan dalam notebook, belum direproduksi:

| Window | RMSE (bytes/bin) | MAE (bytes/bin) | Epoch | Waktu training tersimpan |
|---|---:|---:|---:|---:|
| 144 | 11.810.584.531,81 | 8.877.085.779,45 | 29 | 218,1 detik |
| 288 | 16.385.061.201,26 | 13.408.032.035,68 | 27 | 296,0 detik |

Pada run tersimpan ini, window 144 memiliki error lebih rendah. Perbandingan belum final: satu seed dan window per split menyebabkan himpunan timestamp evaluasi berbeda antar panjang window. Samakan timestamp target sebelum kesimpulan ablation.

Bagian multivariate **dilewati**, karena `global_multivariate_10min.csv` tidak ditemukan. Cell ekspor hasil telah dieksekusi menurut metadata/output notebook, tetapi file terpisah `results_batch4.json` belum ditemukan. Notebook menyebut integrasi ke `DATASET_DECISION_LOG.md` di sesi Claude Code; isi log dan path repo laptop lain belum tersedia.

Catatan audit untuk kelanjutan: preprocessing saat ini mengganti semua nilai nol menjadi missing lalu forward-fill; perlu memvalidasi apakah nol benar-benar gap. Notebook ini belum memuat baseline naive/tanpa Attention atau uji faithfulness XAI. Informasi ini menggantikan ketidakpastian sebelumnya mengenai apakah eksperimen pernah berjalan: ada bukti output Batch 4, tetapi belum ada audit repo lengkap.

## Completed recovery and reconstructed experiment

The complete updated reference, executed results and paper now live in `xai_recovered/`. Start with `xai_recovered/RESULTS_SUMMARY.md` and `xai_recovered/REFERENCE_UPDATED.md`. The reconstructed experiment includes four baselines, fifteen recurrent fits and an eight-page paper draft with 26 references. IG is explicitly provisional because numerical completeness checks failed in some cases.
