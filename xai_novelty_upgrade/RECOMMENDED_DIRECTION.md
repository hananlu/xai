# Memperkuat novelty untuk paper konferensi

5 November 2026. Tanggapan terhadap permintaan novelty yang lebih aman. Dokumen ini memperbarui prioritas ide pada v2; hasil pilot v2 tetap berlaku dan tidak dimodifikasi. **Belum ada novelty atau efektivitas metode baru yang terkonfirmasi.**

## Keputusan

Jangan menjadikan konsekuensi matematis “atribusi imputasi nol” sebagai kontribusi utama. Gunakan pilot sebagai motivasi dan kontrol. Arah yang lebih konkret untuk dikembangkan ialah **benchmark dan evaluasi kebijakan pemulihan telemetry sebelum deadline forecast**, dengan informasi yang benar-benar tersedia saat keputusan dibuat dan biaya komputasi penjelasan yang turut dihitung.

Judul kerja: **Do Explanation-Guided Telemetry Queries Arrive in Time? A Deadline-Aware Benchmark for Network Traffic Forecasting.**

Ini rekomendasi pengembangan, bukan klaim bahwa deadline-aware acquisition baru ditemukan. Deadline, acquisition, dan XAI-guided ranking masing-masing mempunyai prior art. Kontribusi yang hendak dibangun adalah benchmark jaringan yang dapat diulang, pengukuran operasional, dan hasil tentang kapan biaya explanation mengubah manfaat pemulihan input. Memakai CESNET atau menambahkan kata “deadline” saja tidak mencukupi.

## Dua overlap penting yang baru ditemukan

1. [Zilli et al., Inferring Visibility of Internet Traffic Matrices Using eXplainable AI, NOMS 2024](https://iris.polito.it/handle/11583/2989589): XAI sudah digunakan untuk memilih input bagi rekonstruksi traffic matrix dan mengurangi kebutuhan telemetry. Ide umum “gunakan XAI untuk memilih telemetry” tidak boleh diklaim baru. Primary record dan ekstraksi web full text tersedia; unduhan PDF lokal pada pemeriksaan ini mengembalikan 403.
2. [Guney et al., Active Feature Acquisition Via Explainability-driven Ranking, ICML 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12661659/): sudah menggunakan explanation rankings untuk melatih kebijakan acquisition dari input yang tersedia. Bagian problem, metode dan dataset diperiksa melalui full text HTML. Tidak sah menyatakan semua AFA-XAI memerlukan nilai tersembunyi saat inference atau bahwa kita yang pertama menghindari oracle leakage.

Pembanding tambahan: [Acquisition Conditioned Oracle, ICML 2024](https://proceedings.mlr.press/v235/valancius24a.html), [Indexing for Time-Sensitive Prediction](https://people.eecs.berkeley.edu/~adityagp/papers/time.pdf), dan [Sequential Auditing of Connected Forecast Errors, 2026](https://arxiv.org/abs/2611.03928). Acquisition dengan biaya, prediction dengan batas latency, dan query outcome sudah ada. Halaman/abstract dua pembanding pertama diperiksa; pemeriksaan menyeluruh terhadap time-sensitive acquisition masih diperlukan. Pencarian ini tidak membuktikan ketiadaan studi yang identik.

## Pertanyaan riset yang lebih tajam

**Apakah kebijakan pemilihan telemetry berbasis XAI tetap memberi forecast yang lebih baik ketika latency query dan waktu menghitung explanation dimasukkan ke deadline, dibandingkan recency, biaya query, dan acquisition non-XAI?**

Contoh skenario yang akan diuji: sebagian history hilang dari collector pusat, tetapi masih tersimpan di buffer sumber dan dapat diminta ulang. Forecast harus keluar pada cutoff yang ditentukan. Data penting yang tiba terlambat tidak boleh dipakai untuk forecast tersebut. Pengukuran yang hilang permanen berada di luar skenario retrieval; gunakan fallback tanpa mengklaim bahwa data asli berhasil dipulihkan.

Jangan berasumsi query telemetry selalu mahal atau deadline selalu ketat. Ukur kondisi yang relevan. Jika overhead kecil dibandingkan slack forecast, deadline bukan pembeda yang berguna dan arah ini perlu diturunkan prioritasnya.

## Kontribusi yang perlu benar-benar dihasilkan

| Keluaran | Bukti yang diperlukan | Yang tidak diklaim baru |
|---|---|---|
| Benchmark replay telemetry | Kontrak timestamps, informasi yang terlihat pada setiap query, missingness, deadline, serta target terukur; manifest dan task release. | Dataset CESNET, missingness injection, dan chronological split. |
| Pengukuran waktu dan biaya end-to-end | Log request/response, preprocessing, explanation, pemilihan query dan forecast; sensitivitas deadline dan latency. | Ide umum menghitung biaya acquisition. |
| Kebijakan operasional dan ablation | Bandingkan varian dengan/tanpa informasi waktu dan dengan/tanpa XAI pada predictor dan initial observations yang sama. | Importance-per-cost, learned acquisition dan deadline constraints secara umum. |
| Temuan empiris yang bertahan | Error pada cutoff, budget bytes/requests, deadline misses dan manfaat marginal XAI di banyak seri/periode. | Klaim bahwa XAI pasti lebih baik atau bahwa metode baru sudah efektif. |

Benchmark baru bukan otomatis publikasi. Ia harus mengungkap perilaku, batas metode, atau kebutuhan sistem yang belum cukup ditunjukkan oleh benchmark terdekat.

## Pipeline yang disarankan

1. Gunakan 12 institusi CESNET26 yang sudah dipilih untuk development; periode final reserved tetap belum dibuka. Target dan konteks menggunakan definisi yang sama dengan pilot, ditambah forecaster nonnegatif untuk evaluasi operasional.
2. Buat replay API yang hanya mengembalikan nilai yang diminta setelah response tiba. Pisahkan jam event data, jam ketersediaan, dan jam keputusan. Jadwalkan latency yang dapat dikendalikan dan catat real wall-clock overhead.
3. Gunakan jumlah dan pola missing yang bervariasi, termasuk gap terbaru dan gap tersebar. Skenario retensi buffer harus eksplisit; jangan menambahkan asumsi TTL jika belum didukung eksperimen.
4. Pembanding minimum: tanpa retrieval dengan imputasi/fallback; random; newest-first; fastest-query-first; static importance; XAI-guided policy yang hanya memakai observasi tersedia; dan satu metode acquisition non-XAI yang kuat. Oracle dengan akses lengkap hanya batas atas terpisah.
5. Hitung biaya explanation, policy, query dan inference pada cutoff yang sama. Gunakan fallback jika tidak ada jawaban tepat waktu. Pembanding harus memakai initial mask dan trace latency yang berpasangan.
6. Mulai dari Ridge terkontrol dan satu GRU/patch model. Sesuaikan jumlah model setelah pertanyaan terbukti layak; jangan mengejar jumlah arsitektur.
7. Laporkan MAE/MASE pada cutoff, query/byte budget, deadline miss, dan latency. Biaya kapasitas/SLA hanya boleh ditambahkan jika action/cost model didefinisikan; CESNET tidak menyediakan ground-truth tarif SLA atau kapasitas link dalam seri pilot.
8. Setelah kelayakan teruji, bekukan protokol baru sebelum menggunakan reserved periods. Tambahkan jaringan eksternal atau nyatakan batas satu ISP. Jangan menggabungkan results v1/v2 sebagai confirmatory evidence untuk hipotesis baru.

## Data yang ada dan yang belum ada

**Sudah ada:** traffic CESNET26 terverifikasi, time mappings, metadata coverage/outage, selected institutions, kode pilot dan model kontrol.

**Belum ada:** timestamp kedatangan telemetry di collector, latency query riil, kondisi retensi perangkat, kapasitas link, atau biaya SLA nyata. CESNET adalah sumber nilai traffic dan timestamp pengukuran; metadata acquisition harus berasal dari testbed/replay dan diberi label sebagaimana adanya. Latency sintetis tidak boleh dilaporkan sebagai produksi CESNET.

Kekuatan kontribusi bertambah bila trace testbed dan benchmark dirilis. Kelayakan platform pengukuran perlu diperiksa; dokumen ini belum menjalankan testbed, membuat trace, atau melatih kebijakan acquisition.

## Gerbang lanjut sebelum eksperimen besar

- **Literatur:** baca pesaing acquisition yang paling dekat dan buat perbandingan explicit task/information/cost/evaluation. Bila mereka sudah menjawab pertanyaan yang sama pada telemetry forecasting, revisi arah.
- **Relevansi sistem:** tunjukkan bahwa query/explanation overhead dan deadline memang berinteraksi pada skenario yang masuk akal. Jika semua jawaban tiba jauh sebelum cutoff, jangan menciptakan deadline buatan untuk memperoleh kemenangan.
- **Kelayakan metode:** kebijakan tidak melihat future target atau unretrieved values; oracle dipisahkan. XAI diuji terhadap metode acquisition yang sudah mapan, bukan hanya random.
- **Nilai ilmiah:** ada hasil yang stabil atau failure mode operasional yang terukur, bukan sekadar ranking berubah pada satu deadline pilihan. Hasil negatif yang kuat dapat relevan; efek yang hanya muncul pada pengaturan buatan yang sempit melemahkan paper.

## Penilaian jujur

Dibandingkan audit atribusi dasar, arah ini memberi kontribusi yang lebih konkret untuk dibangun: benchmark, trace, evaluasi keputusan dan kemungkinan kebijakan sederhana. Risiko implementasinya lebih tinggi karena memerlukan lapisan replay/testbed dan baseline acquisition. **Ia belum dapat disebut “novelty aman”; saat ini yang lebih kuat adalah rencana pembuktian kontribusinya.**

Rekomendasi: prioritaskan feasibility check arah ini sebelum menambah model neural pada audit lama. Arah alternatif dengan kontribusi data baru ialah testbed berpasangan untuk membedakan perubahan demand dan gangguan capture, tetapi kebutuhan data/validasi lebih besar dan masih beririsan dengan literatur intervention-based network fault evidence. Jangan menganggap alternatif itu otomatis lebih baru.
