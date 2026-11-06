from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
 facts=json.loads((ROOT/'results/PILOT_FACTS.json').read_text());audit=json.loads((ROOT/'data/DATA_AUDIT.json').read_text());run=json.loads((ROOT/'results/run_metadata.json').read_text());validation=json.loads((ROOT/'results/VALIDATION.json').read_text());macro=pd.read_csv(ROOT/'results/clean_macro.csv');stress=pd.read_csv(ROOT/'results/stress_macro.csv')
 def table(columns,rows):return '| '+' | '.join(columns)+' |\n|'+'|'.join(['---']*len(columns))+'|\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)+'\n'
 ids=[v['id'] for v in audit['selected']]
 text=f'''# Pilot v2: hasil dan batas kesimpulan

5 November 2026. **Exploratory pilot selesai; studi konfirmatori dan paper final belum selesai.** Tujuan tahap ini mengecek kelayakan data/pipeline dan diagnostik dasar sebelum studi neural yang lebih mahal.

## Data yang benar-benar dipakai

CESNET-TimeSeries26 resmi ([Zenodo](https://zenodo.org/records/21945629)), lisensi CC BY 4.0. Arsip institusi {audit['archive']['bytes']:,} byte cocok dengan checksum publisher `{audit['archive']['checksum']}`. Pemilihan 12 institusi memakai statistik training saja; ID: {', '.join(map(str,ids))}.

Grid aktual: {audit['hourly_rows']:,} slot hourly dan {audit['native_10min_rows']:,} catatan 10 menit. Terdapat {audit['partial_or_absent_hours']:,} jam yang tidak mempunyai enam catatan 10 menit. Target/input clean pilot memakai jam lengkap, nilai yang tersedia, serta screening konservatif periode probe-loss yang terdokumentasi. Coverage bukan bukti bahwa setiap probe menangkap semua traffic.

Training 2024; validasi Januari 2025; pilot Februari–Maret 2025. Horizon 1 dan 6 jam berarti **volume pada endpoint jam tersebut**, bukan akumulasi enam jam. Periode April 2025–Juni 2026 belum diberi skor. Dua keluarga Ridge dipilih alpha-nya melalui validasi; pembanding persistence, daily dan weekly memakai origin yang sama.

## Forecast clean

Angka di bawah adalah rata-rata MASE per institusi dengan denominator seasonal-naive mingguan pada training. Nilai lebih kecil lebih baik; hasil ini bukan perbandingan neural final.

'''
 rows=[]
 for model in ['persistence','daily','weekly','ridge_clean','ridge_mask_aug']:
  rows.append([model]+[f"{macro[(macro.model==model)&(macro.horizon==h)].iloc[0].mase:.4f}" for h in [1,6]])
 text+=table(['Model','MASE 1h','MASE 6h'],rows)
 neg=macro[macro.model.str.startswith('ridge')].negative_fraction
 text+=f'\nKontrol Ridge tanpa clipping menghasilkan rata-rata per-institusi **{100*neg.min():.2f}–{100*neg.max():.2f}% prediksi negatif** pada evaluasi clean. Ini batas penting: konfigurasi tersebut belum layak menjadi forecaster volume operasional. Studi penuh perlu pembanding dengan output nonnegatif dan penjelasan yang sesuai fungsi akhirnya.\n'
 text+='''\n`ridge_mask_aug` menggunakan augmentation dan indikator missing sekaligus. Perbedaannya tidak mengisolasi manfaat mask; ablation tambahan diperlukan. Prediksi Ridge tidak di-clamp agar dekomposisi linear tetap eksak. Negative-output rate tersedia di clean_macro.csv.

## Dampak kehilangan enam jam input

Setiap skenario menahan target asli dan membandingkan input lengkap dengan input yang kehilangan pengukuran. Di bawah: kenaikan MAE dibagi standar deviasi training, dirata-ratakan per institusi, horizon 6 jam. Nilai negatif berarti skenario tersebut rata-rata memperkecil error dibandingkan input clean; jangan menghapus hasil seperti ini.

'''
 rows=[]
 for pattern in ['scattered','block','tail']:
  for repl in ['zero','ffill','profile']:
   vals=[]
   for model in ['ridge_clean','ridge_mask_aug']:
    f=stress[(stress.model==model)&(stress.horizon==6)&(stress.pattern==pattern)&(stress.replacement==repl)].iloc[0];vals.append(f'{f.incremental_error_sd:.5f}')
   rows.append([pattern,repl]+vals)
 text+=table(['Pattern','Replacement','Ridge clean Δerror/SD','Mask+aug Δerror/SD'],rows)
 wide=stress.pivot(index=['horizon','pattern','replacement'],columns='model',values='incremental_error_sd');worse=int((wide.ridge_mask_aug>wide.ridge_clean).sum())
 text+=f'\nDalam **{worse}/{len(wide)} kondisi agregat**, mask+augmentation mempunyai kenaikan error standar lebih besar daripada Ridge clean. Kondisi-kondisi ini saling bergantung dan hitungan tersebut bukan uji signifikansi; pilot tidak mendukung klaim bahwa konfigurasi mask-aware ini otomatis lebih robust.\n'
 text+=f'''\nSemua skenario/horizon tersedia dalam stress_macro.csv dan stress_by_institution.csv. Tiga seed menentukan lokasi random; pola tail deterministik dihitung satu kali dalam analisis. Bootstrap mingguan berpasangan bersifat deskriptif dan kondisional pada institusi yang dipilih, dengan dependensi satu jaringan dan multiple comparisons yang belum dikoreksi.

## Temuan kontrol penjelasan

Rekonstruksi atribusi linear maksimum meleset {facts['max_reconstruction_error_gb']:.3g} GB; identitas perubahan prediksi maksimum meleset {facts['max_shift_identity_error_gb']:.3g} GB. Ini meloloskan pemeriksaan aritmetika, tanpa membuktikan novelty atau kegunaan operasional.

Untuk Ridge clean dengan imputasi profil yang sama dengan reference explanation:

- Massa atribusi pada nilai imputasi maksimum: **{facts['profile_clean_ridge_max_imputed_mass_gb']:.3g} GB**.
- Proporsi pasangan dengan perubahan prediksi nonzero: **{100*facts['profile_clean_ridge_nonzero_shift_fraction']:.1f}%**.
- Proporsi pasangan dengan absolute error meningkat: **{100*facts['profile_clean_ridge_positive_incremental_error_fraction']:.1f}%**.

Atribusi relatif-reference tetap benar. Kesimpulan “massa atribusi imputasi nol berarti forecast aman” tidak didukung. Temuan ini mengilustrasikan konsekuensi definisi yang sudah dijelaskan **sebelum** fitting di INTERPRETATION_CONTRACT.md; jangan mengklaim menemukan teorema baru atau menyebut semua explanation salah.

## Apakah sudah worth sebagai paper konferensi?

**Layak diteruskan sebagai studi empiris terfokus; pilot ini sendiri belum cukup untuk submit.** Literatur sudah memiliki XAI forecasting, missingness bias, perturbation audits dan reference controls. Nilai paper harus muncul dari hasil yang konsisten dan berguna pada situasi operasional jaringan, bukan dari kombinasi istilah tersebut.

Pilot menyediakan dataset terverifikasi, kontrol eksak dan hasil awal yang dapat diulang. Ia belum menunjukkan bahwa XAI memberi diagnosis tambahan melebihi heuristic sederhana. Korelasi yang disimpan adalah asosiasi univariat; efek kondisional/incremental utility belum diuji. Semua skenario kehilangan enam jam, sehingga missing fraction konstan dan belum dapat menjadi pembanding diskriminasi yang berarti. Bukti belum mencakup neural models, severity berbeda, outage alami yang memiliki true demand tersembunyi, atau jaringan eksternal.

Lanjut studi penuh dengan severity-varying controls, augmentation/mask ablation, beberapa keluarga model, outcome reserved dan pembanding penelitian terdekat. Jika XAI tidak menambah manfaat, laporkan hasil negatif serta kondisi batasnya; jangan menjual sebuah risk score universal.

## Reproduksi dan status

Runtime fitting/perekaman: {run['runtime_seconds']:.1f} detik. Artifact validation: **{validation['status']}**. Prefit protocol/source hashes, hash data terpilih, prediksi checkpoint, semua MAE clean dan error stress diperiksa kembali. Skrip dan konfigurasi tersimpan; lihat README.md.

Titik pada grafik clean mewakili institusi; garis hitam menunjukkan median. Tabel di atas memakai mean per institusi.\n\n![Clean forecasting](figures/clean_mase.png)

Grafik stress menampilkan mean per institusi; skala sumbu y berbeda antar panel.\n\n![Telemetry loss stress test](figures/stress_error.png)
'''
 (ROOT/'PILOT_RESULTS_AND_VERDICT.md').write_text(text)
 print('Wrote pilot report')
if __name__=='__main__':main()
