from pathlib import Path
import ast, json, textwrap, hashlib
import nbformat as nbf
R=Path(__file__).resolve().parents[1]
cells=[]
def md(x):cells.append(nbf.v4.new_markdown_cell(textwrap.dedent(x).strip()))
def c(x):cells.append(nbf.v4.new_code_cell(textwrap.dedent(x).strip()))
def inline(file,*names,rename=None):
 tree=ast.parse((R/'src'/file).read_text());nodes=[]
 class Fix(ast.NodeTransformer):
  def visit_Name(self,node):
   if node.id=='__file__':return ast.copy_location(ast.Name(id='NOTEBOOK_PATH',ctx=node.ctx),node)
   return node
 for node in tree.body:
  if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names:
   node=Fix().visit(node)
   if rename and node.name in rename:node.name=rename[node.name]
   nodes.append(node)
 assert len(nodes)==len(names),(file,names)
 c(ast.unparse(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[]))))
md('''
# Cross-Institution XAI for Network Traffic Forecasting
## Complete experimental notebook — data, models, training, forecasts and temporal explanations

**Versi 6 November 2026.** Pendamping studi *Cross-Institution Reliability of Temporal Attributions in Network Traffic Forecasting*.

Notebook ini memperlihatkan implementasi inti langsung di dalam sel: eligibility windows, Ridge/DLinear/GRU, training loop, inference, exact group Shapley, occlusion, IG, controlled operators, dan paired bootstrap. Tidak perlu membuka script eksternal untuk memahami algoritmanya. Dataset/checkpoint/hasil tetap berada dalam paket proyek agar ukuran notebook wajar.

**Cara memakai:** ekstrak paket lengkap; pilih kernel Python dengan `requirements-full.txt` dan Jupyter/ipykernel; jalankan dari atas. Mode default melakukan EDA, refit Ridge sebagai pemeriksaan reproduksi, inference dari checkpoint, penghitungan atribusi kasus nyata dan bootstrap ulang. Full neural retraining dan batch evaluation tersedia di bagian akhir dengan flag eksplisit dan menulis ke salinan baru.

**Referensi struktur:** [hananlu/xai — XAI_Network_Traffic.ipynb](https://github.com/hananlu/xai/blob/master/XAI_Network_Traffic.ipynb), diakses 6 November 2026. Susunan EDA → preprocessing → modeling → global/local XAI → agreement/stability/latency → robustness menginspirasi penyajian. Implementasi forecasting di sini memakai kode studi kita; tidak menyalin pipeline klasifikasi, random split, label encoding, atau target klasifikasinya.
''')
md('''
## 1. Research question dan batas klaim

**RQ primer:** pada frozen GRU, horizon 1 jam, source-calendar Shapley, apakah ranking alignment berubah ketika model dipakai pada institusi yang tidak masuk fitting?

Tiga objek pengukuran dipisahkan:

| Objek | Pertanyaan | Ukuran |
|---|---|---|
| Forecast | Seberapa dekat prediksi dengan volume berikutnya? | MAE, RMSE, MASE |
| Numerik atribusi | Apakah perhitungan memenuhi game/path dan toleransi yang ditetapkan? | Shapley efficiency; IG completeness + refinement |
| Ranking alignment | Apakah ranking mendahulukan hari dengan respons besar di bawah operator? | Q relatif random dan response oracle |

Q bukan probabilitas salah, bukan causal demand attribution dan bukan universal explanation correctness. Semua target sudah pernah dievaluasi; notebook ini mereproduksi dan memperjelas studi, bukan membuka holdout baru. Analisis agreement, latency, visual EDA dan kasus lokal adalah deskriptif tambahan, tidak mengganti endpoint paper.
''')
md('''
## 2. Konfigurasi dan dependensi

Python 3.11 digunakan dalam run asli. Di environment baru instal `requirements-full.txt`, ditambah `jupyterlab` dan `ipykernel`, lalu pilih kernel tersebut. Tidak ada pemasangan paket, mounting Drive, download besar atau compute cloud otomatis.

Di Colab, upload dan ekstrak ZIP proyek, lalu isi `PROJECT_DIR`; kompatibilitas Colab belum diuji dalam run lokal ini. Jangan hanya upload notebook tanpa folder data/checkpoint. Full retraining CPU membutuhkan beberapa menit; default notebook lebih ringan.
''')
c('''
from pathlib import Path
import sys, json, time, copy, hashlib, itertools, shutil, gc
from math import factorial
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.polynomial.legendre import leggauss
from scipy.stats import kendalltau
from sklearn.linear_model import Ridge
import torch
from torch import nn
from IPython.display import display, Markdown

PROJECT_DIR = None  # Contoh: "/content/xai_cross_institution"
candidates = [Path(PROJECT_DIR).expanduser()] if PROJECT_DIR else [
    Path.cwd(), Path.cwd()/"xai_cross_institution", Path.cwd()/"outputs/xai_cross_institution"
]
ROOT = next((p.resolve() for p in candidates if (p/"results/NUMERIC_CLAIMS.json").is_file()), None)
if ROOT is None:
    raise FileNotFoundError("Ekstrak paket lengkap dan isi PROJECT_DIR dengan folder xai_cross_institution.")
SOURCE_ROOT = ROOT
NOTEBOOK_PATH = SOURCE_ROOT / "XAI_Complete_Experiment.ipynb"
SEED = 42
HORIZONS = [1, 6]
YEARS = [2025, 2026]
DAY_NAMES = [f"Day {i+1}" for i in range(7)]  # oldest -> newest
RUN_RIDGE_REPRO_CHECK = True
RUN_FULL_TRAINING = False
RUN_FULL_EVALUATION = False
EXPORT_EXPLORATORY = False
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.set_num_threads(4)
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_rows", 30)
plt.rcParams.update({"figure.dpi":110, "axes.spines.top":False, "axes.spines.right":False})
print("Project:", ROOT.name)
print("Python:",sys.version.split()[0], "Torch:",torch.__version__)
''')
md('''
### 2.1 Artefak dan pembekuan protokol

Hash lokal melindungi jejak kode dan protokol yang ada sebelum target dibuka; ini bukan public preregistration. Field `target_outcomes_scored:false` pada manifest freeze adalah status historis. Status saat ini ada di `STUDY_COMPLETE.json`.
''')
c('''
split = pd.read_csv(ROOT/"INSTITUTION_SPLIT.csv")
pairs = pd.read_csv(ROOT/"MATCHED_PAIRS.csv")
claims = json.loads((ROOT/"results/NUMERIC_CLAIMS.json").read_text())
training_record = json.loads((ROOT/"results/TRAINING_COMPLETE.json").read_text())
manifest = json.loads((ROOT/"data/MANIFEST.json").read_text())
hash_audit = []
for fname in ["FULL_PREFIT_HASHES.json", "FULL_PREEVALUATION_HASHES.json"]:
    record = json.loads((ROOT/"results"/fname).read_text())
    for rel, expected in record["files"].items():
        actual = hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
        hash_audit.append({"manifest":fname,"file":rel,"match":actual==expected})
assert all(x["match"] for x in hash_audit)
print("Frozen code/protocol checks passed:",len(hash_audit))
print("Dataset:",manifest["dataset"], "License:",manifest["license"])
print("Training target institutions fitted:",training_record["target_institutions_fitted"])
display(split.groupby("role").size().rename("institutions").to_frame())
display(pairs)
''')
md('''
## 3. Membaca dataset dan memeriksa schema

**CESNET-TimeSeries26**: official institutional hourly `n_bytes`, dikonversi ke decimal GB = bytes/1e9. Sumber [Zenodo](https://doi.org/10.5281/zenodo.21945629), CC BY 4.0, Josef Koumar, Karel Hynek, Kamil Jeřábek, Pavel Šiška (2026). Institusi berasal dari satu ISP/research-network ecosystem.

`complete_hour` berasal dari cakupan enam native 10-minute timestamps; keberadaan nilai institusi tetap diperiksa terpisah. `conservative_artifact_flag` adalah screening global dengan scope institusi yang tidak pasti. Nilai nol teramati dipertahankan; missing bukan nol.
''')
c('''
example_id = int(split.query("role == 'source'").id.iloc[0])
example_df = pd.read_csv(ROOT/f"data/institution_{example_id}.csv.gz")
print("Schema:")
print(example_df.dtypes)
print("Shape:",example_df.shape)
display(example_df.head())
''')
c('''
quality_rows=[]
for item in manifest["files"]:
    path = ROOT/"data"/item["file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest()==item["sha256"]
    d=pd.read_csv(path)
    y=d.n_bytes.to_numpy(float)/1e9
    finite=np.isfinite(y)
    complete=d.complete_hour.to_numpy(bool)
    flagged=d.conservative_artifact_flag.to_numpy(bool)
    quality_rows.append(dict(id=item["id"],role=item["role"],hours=len(d),
        missing=int((~finite).sum()),observed_zero=int(((y==0)&finite).sum()),
        negative=int(((y<0)&finite).sum()),duplicate_time=int(d.time.duplicated().sum()),
        complete_native=int(complete.sum()),
        usable_hours=int((finite&(y>=0)&complete&~flagged).sum()),
        median_gb=float(np.nanmedian(y))))
quality_df=pd.DataFrame(quality_rows)
assert quality_df.duplicate_time.sum()==0
print("All 48 derived file hashes passed.")
display(quality_df.groupby("role").agg(institutions=("id","size"),
    recorded_grid_hours=("hours","sum"),missing=("missing","sum"),
    observed_zero=("observed_zero","sum"),negative=("negative","sum"),
    usable_hours=("usable_hours","sum")))
display(quality_df.sort_values("missing",ascending=False).head(10))
''')
md('''
### 3.1 Coverage per institusi

Plot coverage menjelaskan selection pressure dari complete-history rule. Ini data availability, bukan skor model. Tidak membuang institusi setelah melihat error.
''')
c('''
z=quality_df.sort_values(["role","id"]).reset_index(drop=True)
fig,ax=plt.subplots(figsize=(13,4),constrained_layout=True)
colors=z.role.map({"source":"#2365a0","validation":"#0d9488","target":"#c16b24"})
ax.bar(np.arange(len(z)),z.usable_hours/z.hours,color=colors)
ax.set_xticks(np.arange(len(z)),[f"{r.id}" for r in z.itertuples()],rotation=90)
ax.set_ylim(0,1.05);ax.set_ylabel("Fraction of usable hours")
ax.set_xlabel("Institution ID; blue=source, green=validation, orange=target")
ax.set_title("Coverage before requiring a complete 168-hour history")
plt.show()
''')
md('''
### 3.2 Time-series dan pola kalender

Pilih satu institusi per role berdasarkan urutan membership, bukan performa. Garis log1p hanya untuk visualisasi; gap tidak diisi. Heatmap kalender memakai **source 2024 saja**, bukan target atau tahun evaluasi.
''')
c('''
fig,axes=plt.subplots(3,1,figsize=(13,7),sharex=True,constrained_layout=True)
for ax,role in zip(axes,["source","validation","target"]):
    ident=int(split.query("role==@role").id.iloc[0])
    d=pd.read_csv(ROOT/f"data/institution_{ident}.csv.gz")
    t=pd.to_datetime(d.time,utc=True)
    ax.plot(t,np.log1p(d.n_bytes/1e9),lw=.6)
    ax.set_ylabel("log1p(GB)");ax.set_title(f"{role}: institution {ident}")
axes[-1].set_xlabel("UTC timestamp")
plt.show()
profile=np.load(ROOT/"models/source_profile.npy")
fig,ax=plt.subplots(figsize=(11,3),constrained_layout=True)
im=ax.imshow(np.log1p(profile.reshape(7,24)),aspect="auto",cmap="viridis")
ax.set_yticks(range(7),["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
ax.set_xticks(range(0,24,3));ax.set_xlabel("UTC hour");ax.set_title("Source-only 2024 hour-of-week median profile")
fig.colorbar(im,ax=ax,label="log1p(GB)");plt.show()
''')
md('''
## 4. Sampling, institution split dan pencegahan leakage

32 source / 8 validation / 8 target, di luar 12 institusi development terdahulu. Membership menggunakan saved 2024 coverage/volume metadata, empat volume strata dan deterministic hashing. Pair matching memakai 2024 median volume dan coefficient of variation; matching tidak menghilangkan confounding.

Training target timestamps: 2024. Validation: institusi validation, Jan–Mar 2025. Evaluation: eligible endpoints Apr 8–Jul 1 pada 2025 dan 2026, origin UTC hour divisible by 6. Tidak ada random row split lintas waktu. Metadata target 2024 dipakai untuk selection/matching/metric scaling, **bukan** gradient fitting; ini bukan berarti target sama sekali tidak pernah dipakai untuk metadata.
''')
c('''
roles={role:set(split.query("role==@role").id) for role in split.role.unique()}
assert split.id.is_unique
assert not (roles["source"] & roles["validation"])
assert not (roles["source"] & roles["target"])
assert not (roles["validation"] & roles["target"])
assert set(pairs.source)<=roles["source"] and set(pairs.target)==roles["target"]
fig,ax=plt.subplots(figsize=(7,3),constrained_layout=True)
for role,color in [("source","#2365a0"),("validation","#0d9488"),("target","#c16b24")]:
    vals=quality_df.query("role==@role").median_gb
    ax.scatter(np.full(len(vals),role),np.log1p(vals),label=role,color=color,alpha=.8)
ax.set_ylabel("log1p(median observed GB)");ax.set_title("Volume heterogeneity; plot is descriptive")
plt.show()
''')
md('''
## 5. Preprocessing dan pembentukan supervised windows — kode inti

Setiap example memakai 168 jam sampai origin o. Label adalah y[o+1] dan y[o+6], bukan seluruh lintasan enam jam. Seluruh history dan kedua endpoint harus usable. Interval periode ditentukan oleh target timestamps; history boleh berada sebelum awal interval.
''')
inline('data_common.py','windows','period')
c('''
selection=pd.read_csv(ROOT/"results/explanation_selection.csv")
# Case dipilih dengan metadata tetap, tanpa mencari error/quality tertentu.
case=selection.query("pair==3 and year==2025 and cohort=='target'").sort_values("origin").iloc[0]
case_id=int(case.id)
case_v=windows(ROOT/f"data/institution_{case_id}.csv.gz")
case_o=int(case_v["t"].get_loc(pd.Timestamp(case.origin)))
case_ix=int(np.flatnonzero(case_v["o"]==case_o)[0])
x_case=case_v["X"][case_ix]
y_case=case_v["Y"][case_ix]
assert x_case.shape==(168,) and y_case.shape==(2,)
assert np.all(np.isfinite(x_case)) and np.all(x_case>=0)
assert np.all(case_v["valid"][case_o-167:case_o+1])
assert all(case_v["t"][case_o+h]>case_v["t"][case_o] for h in HORIZONS)
print("Case metadata:",case[["pair","id","cohort","year","origin"]].to_dict())
print("X shape",x_case.shape,"Y shape",y_case.shape)
print("Observed endpoint GB:",dict(zip(HORIZONS,y_case)))
''')
c('''
fig,ax=plt.subplots(figsize=(12,3.5),constrained_layout=True)
ax.plot(np.arange(-167,1),x_case,label="168h observed history",lw=1)
ax.scatter(HORIZONS,y_case,c="#c16b24",label="Observed future endpoints",zorder=5)
ax.axvline(0,c="gray",ls="--");ax.set_xlabel("Hours relative to origin")
ax.set_ylabel("GB");ax.set_title(f"Institution {case_id}, {case.origin}")
ax.legend();plt.show()
''')
md('''
### 5.1 Memuat data fitting dan normalization source-only

Array log1p float32 sama dengan training asli; Ridge difit dalam float64 dari array tersebut. Validation loss dirata-rata per institusi, bukan didominasi institusi yang punya banyak windows. Tidak memuat target ke array fitting. Cell ini merekonstruksi input fitting, tanpa neural retraining.
''')
c('''
source_arrays=[]; validation_arrays=[]; fit_count_rows=[]
for row in split.itertuples():
    if row.role=="target":
        continue
    v=windows(ROOT/f"data/institution_{row.id}.csv.gz")
    mask=period(v,"2024-01-01","2025-01-01") if row.role=="source" else period(v,"2025-01-01","2025-04-01")
    xx=np.log1p(v["X"][mask]).astype("float32")
    yy=np.log1p(v["Y"][mask]).astype("float32")
    assert len(xx)>0
    (source_arrays if row.role=="source" else validation_arrays).append((int(row.id),xx,yy))
    fit_count_rows.append(dict(id=int(row.id),role=row.role,windows=len(xx)))
    del v
X_source=np.concatenate([a for _,a,_ in source_arrays])
Y_source=np.concatenate([b for _,_,b in source_arrays])
source_mean=float(X_source.mean());source_std=float(X_source.std())
assert len(X_source)==training_record["source_windows"]
assert abs(source_mean-training_record["normalization_mean"])<1e-8
assert abs(source_std-training_record["normalization_std"])<1e-8
assert {i for i,_,_ in source_arrays}<=roles["source"]
assert {i for i,_,_ in validation_arrays}<=roles["validation"]
print("Source arrays:",X_source.shape,Y_source.shape)
print("Source-only mean/std:",source_mean,source_std)
display(pd.DataFrame(fit_count_rows).groupby("role").agg(institutions=("id","size"),windows=("windows","sum")))
''')
md('''
## 6. Ridge: fit langsung dan pemeriksaan checkpoint

Hyperparameter yang sudah dipilih adalah alpha=0.1 per horizon. Sel berikut **benar-benar memfit ulang** Ridge pada source 2024 dengan setting yang dibekukan, lalu membandingkan koefisien dengan checkpoint. Tidak mencari hyperparameter baru dari target. Set `RUN_RIDGE_REPRO_CHECK=False` untuk melewatinya.
''')
c('''
ridge_checkpoint=np.load(ROOT/"models/ridge_0.npz")
if RUN_RIDGE_REPRO_CHECK:
    ridge_refits=[]
    t0=time.perf_counter()
    for k,h in enumerate(HORIZONS):
        model=Ridge(alpha=.1,solver="cholesky").fit(X_source.astype("float64"),Y_source[:,k].astype("float64"))
        ridge_refits.append(model)
        diff=np.max(np.abs(model.coef_-ridge_checkpoint["coef"][k]))
        assert np.allclose(model.coef_,ridge_checkpoint["coef"][k],rtol=1e-7,atol=1e-9)
        val_loss=np.mean([np.mean(np.abs(model.predict(a)-b[:,k])) for _,a,b in validation_arrays])
        print(f"h={h}: alpha=.1, validation macro log-MAE={val_loss:.6f}, max coef difference={diff:.3g}")
    print(f"Ridge refit check: {time.perf_counter()-t0:.2f}s")
else:
    print("Ridge refit check disabled; using delivered checkpoint.")
''')
md('''
## 7. DLinear dan GRU — arsitektur dan fungsi yang diatribusikan

DLinear: moving average 25 jam dengan endpoint replication, trend/seasonal heads 168→2. GRU: satu layer, 32 hidden units, correction terhadap last log input; head awal nol. Output GB = expm1(max(0,predicted_log)). Preprocessing dan clipping termasuk dalam fungsi atribusi; IG tidak berhenti di latent/log output.
''')
inline('neural_feasibility.py','Forecaster')
c('''
architecture_rows=[]
for kind in ["dlinear","gru"]:
    checkpoint=torch.load(ROOT/f"models/{kind}_42.pt",map_location="cpu",weights_only=True)
    model=Forecaster(kind,checkpoint["mean"],checkpoint["std"])
    model.load_state_dict(checkpoint["state"]);model.double().eval()
    with torch.no_grad():pred=model(torch.tensor(x_case[None,:],dtype=torch.float64)).numpy()
    architecture_rows.append(dict(model=kind,trainable_parameters=sum(p.numel() for p in model.parameters()),
                                  input_hours=168,output_endpoints=2,prediction_h1=float(pred[0,0]),prediction_h6=float(pred[0,1])))
    print(kind,model)
display(pd.DataFrame(architecture_rows))
''')
md('''
### 7.1 Training loop lengkap — implementasi inline

Kode di bawah memuat fitting Ridge grid, balanced institution sampling, Adam, log-MSE, gradient clipping, validation per institusi, patience, pemilihan learning rate memakai seed 42, dan training seeds 123/2026. Definisi tidak otomatis melatih model. Bagian akhir mengaktifkannya hanya pada salinan baru.

Konfigurasi fixed: batch 256 (32×1024 examples/epoch dibagi 128 batches), maksimum 30 epochs, patience 5; LR {0.001,0.0003}. Pemilihan LR tidak diulang memakai target. `source_sha256` pada inline rerun menunjuk hash notebook yang dijalankan, bukan mengklaim file script historis dieksekusi.
''')
inline('train_full.py','save_model')
inline('train_full.py','main',rename={'main':'train_all_models_inline'})
md('''
### 7.2 Learning curves dan pilihan model tersimpan

Kurva seed/LR adalah jejak training asli, bukan kurva yang dipilih setelah target dibuka. Epoch terakhir bukan otomatis checkpoint terbaik; lihat metadata selected epoch.
''')
c('''
history=pd.read_csv(ROOT/"results/training_history.csv")
model_selection=pd.DataFrame(json.loads((ROOT/"results/MODEL_SELECTION.json").read_text()))
display(model_selection[model_selection.get("phase",pd.Series(index=model_selection.index,dtype=str)).eq("selected") |
                        model_selection.kind.eq("ridge_selected")])
fig,axes=plt.subplots(1,2,figsize=(12,4),constrained_layout=True)
for ax,kind in zip(axes,["dlinear","gru"]):
    for (seed,lr),g in history.query("kind==@kind").groupby(["seed","lr"]):
        ax.plot(g.epoch,g.validation_macro_log_mae,label=f"seed={seed}, lr={lr:g}")
    ax.set_title(kind);ax.set_xlabel("Epoch");ax.set_ylabel("Validation macro log-MAE");ax.legend(fontsize=8)
plt.show()
''')
md('''
## 8. Inference wrapper, naive baselines dan calibration — kode inti

Wrapper mengembalikan dua endpoint sekaligus dan memuat checkpoint tanpa target-specific normalization. Calibration adalah offset median log-residual dari eligible Apr 1–8 dengan minimal 24 examples; bukan neural fine-tuning dan bukan arm zero-shot.
''')
inline('benchmark_common.py','RidgeModule','Predictor')
inline('evaluate_forecasts.py','denominator','naive','calibration')
c('''
predictors={kind:Predictor(kind,0 if kind=="ridge" else 42) for kind in ["ridge","dlinear","gru"]}
case_predictions=[]
for kind,model in predictors.items():
    pred=model(x_case)
    assert pred.shape==(2,) and np.isfinite(pred).all() and (pred>=0).all()
    for k,h in enumerate(HORIZONS):case_predictions.append(dict(model=kind,horizon=h,observed_gb=y_case[k],predicted_gb=pred[k],absolute_error_gb=abs(pred[k]-y_case[k])))
display(pd.DataFrame(case_predictions))
''')
md('''
## 9. Forecast metrics: per-cell, institution dan macro

MASE denominator adalah observed eligible 2024 weekly absolute difference per institusi, floored 1e-9 GB. Raw GB errors tidak menghilangkan perbedaan volume. Angka headline adalah mean available institution-year cells setelah seed averaging (15 target cells), bukan balanced panel. Semua per-origin predictions disediakan agar metrics dapat dihitung ulang.
''')
c('''
metrics=pd.read_csv(ROOT/"results/forecast_metrics.csv")
metric_cols=["mae_gb","rmse_gb","mase"]
metric_cells=metrics.groupby(["model","id","role","year","arm","horizon"])[metric_cols].mean().reset_index()
macro=metric_cells.groupby(["model","role","arm","horizon"])[metric_cols].mean().reset_index()
target_macro=macro.query("role=='target' and arm=='frozen'")
display(target_macro.round(6))
print("Target institution-year cells:",len(metric_cells.query("model=='ridge' and role=='target' and arm=='frozen' and horizon==1")))
''')
c('''
names=["persistence","daily","weekly","ridge","dlinear","gru"]
fig,axes=plt.subplots(1,2,figsize=(12,4),constrained_layout=True)
for ax,h in zip(axes,HORIZONS):
    z=target_macro.query("horizon==@h").set_index("model").reindex(names)
    ax.bar(names,z.mase,color=["#94a3b8"]*3+["#2365a0","#0d9488","#c16b24"])
    ax.set_title(f"Target frozen: {h}h endpoint");ax.set_ylabel("Macro MASE")
    ax.tick_params(axis="x",rotation=30);ax.grid(axis="y",alpha=.2)
plt.show()
''')
c('''
fig,axes=plt.subplots(1,2,figsize=(12,4),constrained_layout=True)
for ax,h in zip(axes,HORIZONS):
    z=metric_cells.query("role=='target' and arm=='frozen' and horizon==@h")
    vals=[z.query("model==@kind").mase.values for kind in names]
    ax.boxplot(vals,tick_labels=names,showfliers=True)
    ax.tick_params(axis="x",rotation=30);ax.set_ylabel("Institution-year MASE")
    ax.set_title(f"Heterogeneity: {h}h endpoint")
plt.show()
''')
md('''
### 9.1 Error analysis dan prediksi kronologis

Contoh institusi/case dipilih sebelumnya melalui metadata. Scatter dan residual menggunakan GRU seed 42; bukan ensemble tiga seed dan bukan hasil pemilihan kasus dengan error tertentu.
''')
c('''
gru_predictions=pd.read_csv(ROOT/"predictions/gru_42.csv.gz")
case_forecasts=gru_predictions.query("id==@case_id and year==2025 and arm=='frozen' and horizon==1").copy()
assert len(case_forecasts)>0
case_forecasts["origin"]=pd.to_datetime(case_forecasts.origin,utc=True)
residual=case_forecasts.prediction_gb-case_forecasts.target_gb
fig,axes=plt.subplots(1,3,figsize=(14,3.5),constrained_layout=True)
axes[0].plot(case_forecasts.origin,case_forecasts.target_gb,label="Observed",lw=1)
axes[0].plot(case_forecasts.origin,case_forecasts.prediction_gb,label="Forecast",lw=1,alpha=.8)
axes[0].tick_params(axis="x",rotation=35);axes[0].set_ylabel("GB");axes[0].legend()
axes[1].scatter(np.log1p(case_forecasts.target_gb),np.log1p(case_forecasts.prediction_gb),s=10,alpha=.6)
axes[1].set_xlabel("Observed log1p(GB)");axes[1].set_ylabel("Forecast log1p(GB)")
axes[2].hist(residual,bins=25,color="#2365a0");axes[2].axvline(0,c="gray")
axes[2].set_xlabel("Forecast − observed GB");axes[2].set_ylabel("Count")
fig.suptitle(f"Institution {case_id}, 2025, frozen GRU seed 42, h1")
plt.show()
''')
c('''
# Recompute a full stored institution/year/arm/horizon cell from per-origin predictions.
saved=metrics.query("model=='gru' and seed==42 and id==@case_id and year==2025 and arm=='frozen' and horizon==1").iloc[0]
recomputed={"mae_gb":float(abs(residual).mean()),"rmse_gb":float(np.sqrt(np.mean(residual**2))),
            "mase":float(abs(residual).mean()/saved.mase_denominator_gb)}
for key,value in recomputed.items():assert np.isclose(value,saved[key],rtol=1e-10,atol=1e-12)
print("Per-origin metric recalculation passed:",recomputed)
''')
md('''
## 10. Dua reference atribusi

**Source calendar:** profile median pooled source training 2024 menurut hour of week. **History hour median:** median tujuh hari pada jam yang sama, diulang sepanjang history. Keduanya menjelaskan kontras F(x)−F(r) yang berbeda. Mengganti reference bukan otomatis memperbaiki penjelasan.
''')
c('''
history_times=case_v["t"][case_o-167:case_o+1]
how=history_times.day_of_week.to_numpy()*24+history_times.hour.to_numpy()
references={"source_calendar":profile[how],
            "history_hour_median":np.tile(np.median(x_case.reshape(7,24),axis=0),7)}
fig,ax=plt.subplots(figsize=(12,4),constrained_layout=True)
ax.plot(x_case,label="Observed history",c="black",lw=1)
for name,r in references.items():ax.plot(r,label=name,alpha=.8)
ax.set_xlabel("History hour (oldest → newest)");ax.set_ylabel("GB");ax.legend();plt.show()
contrast_rows=[]
for kind,model in predictors.items():
    for name,r in references.items():
        for k,h in enumerate(HORIZONS):contrast_rows.append(dict(model=kind,reference=name,horizon=h,
            prediction_gb=float(model(x_case)[k]),reference_prediction_gb=float(model(r)[k]),contrast_gb=float(model(x_case)[k]-model(r)[k])))
display(pd.DataFrame(contrast_rows))
''')
md('''
## 11. Exact seven-group Shapley dan occlusion — kode inti

Setiap grup adalah 24 jam berturut-turut, oldest→newest. Semua 128 retained-group coalitions dievaluasi; ini exact Shapley untuk game/reference itu, bukan conditional Shapley terhadap distribusi traffic. Occlusion memakai absolute single-group prediction response. Ranking Shapley memakai absolute signed sum per hari, sehingga cancellation di dalam hari masih mungkin.
''')
c('''
MASKS=((np.arange(128)[:,None]>>np.arange(7))&1).astype(float)
PERMUTATIONS=np.array(list(itertools.permutations(range(7))),dtype=int)
REMOVED=np.column_stack([np.zeros(5040,dtype=int),np.cumsum(1<<PERMUTATIONS,axis=1)])
SHAPLEY_WEIGHTS=[]
for j in range(7):
    ix=np.where(MASKS[:,j]==0)[0]
    size=MASKS[ix].sum(1).astype(int)
    weights=np.array([factorial(k)*factorial(6-k)/factorial(7) for k in size])
    SHAPLEY_WEIGHTS.append((ix,weights))
print("Coalitions:",MASKS.shape,"Rankings:",PERMUTATIONS.shape)
''')
inline('benchmark_common.py','games','order')
c('''
local_attributions={}; local_rows=[]
for kind,model in predictors.items():
    for ref,r in references.items():
        phi,occ,coalition_values,efficiency_error=games(model,x_case,r)
        local_attributions[(kind,ref)]={"shapley":phi,"occlusion":occ,"game":coalition_values}
        for k,h in enumerate(HORIZONS):
            local_rows.append(dict(model=kind,reference=ref,horizon=h,sum_phi_gb=float(phi[k].sum()),
                                  contrast_gb=float(model(x_case)[k]-model(r)[k]),efficiency_error_gb=float(efficiency_error[k])))
local_numerics=pd.DataFrame(local_rows)
display(local_numerics)
assert local_numerics.efficiency_error_gb.max()<1e-9
''')
md('''
### 11.1 Penjelasan lokal: nilai bertanda dan ranking

Panel pertama menjelaskan arah kredit relatif reference. Panel kedua menampilkan magnitude occlusion, yang tidak memiliki semantik kredit bertanda yang sama. Tidak membandingkan tinggi kedua panel sebagai estimator kuantitas identik.
''')
c('''
fig,axes=plt.subplots(2,3,figsize=(14,6),constrained_layout=True)
for col,kind in enumerate(["ridge","dlinear","gru"]):
    phi=local_attributions[(kind,"source_calendar")]["shapley"][0]
    occ=local_attributions[(kind,"source_calendar")]["occlusion"][0]
    axes[0,col].bar(DAY_NAMES,phi,color=np.where(phi>=0,"#2365a0","#c16b24"))
    axes[0,col].axhline(0,c="gray",lw=.7);axes[0,col].set_title(f"{kind}: signed Shapley, h1")
    axes[1,col].bar(DAY_NAMES,occ,color="#0d9488");axes[1,col].set_title("Absolute single-day occlusion response")
    for row in [0,1]:axes[row,col].tick_params(axis="x",rotation=40);axes[row,col].set_ylabel("GB")
plt.show()
''')
md('''
### 11.2 Independent permutation identity check

Untuk satu game nonlinear GRU, hitung rata-rata marginal contribution di seluruh 7! permutations secara terpisah dari subset-weight formula. Pemeriksaan ini memvalidasi aritmetika game; efficiency saja tidak membuktikan semantik atau usefulness.
''')
c('''
phi=local_attributions[("gru","source_calendar")]["shapley"]
v=local_attributions[("gru","source_calendar")]["game"]
permutation_phi=np.zeros((2,7))
for permutation in PERMUTATIONS:
    mask=0
    for j in permutation:
        permutation_phi[:,j]+=v[mask+(1<<j)]-v[mask]
        mask+=1<<j
permutation_phi/=len(PERMUTATIONS)
assert np.allclose(phi,permutation_phi,rtol=1e-8,atol=1e-10)
print("Max independent Shapley difference:",float(abs(phi-permutation_phi).max()))
''')
md('''
## 12. Integrated Gradients: integrasi full GB function

Gauss–Legendre 32,64,128,256,512 nodes. Accept hanya jika completeness ≤1e-8 +1e-3×|contrast| dan successive L1 change ≤1e-8 +1e-3×L1 credits. Failed attribution tetap direkam dan tidak dipakai untuk quality score. Ini numerical acceptance, bukan jaminan straight path berada pada distribusi traffic alami.
''')
c('''
NODES={n:leggauss(n) for n in [32,64,128,256,512]}
''')
inline('benchmark_common.py','integrated_gradients')
c('''
local_ig={}; ig_case_rows=[]
for kind,model in predictors.items():
    for ref,r in references.items():
        credits,accepted,nodes,errors,changes=integrated_gradients(model,x_case,r)
        local_ig[(kind,ref)]={"credits":credits,"accepted":accepted}
        for k,h in enumerate(HORIZONS):ig_case_rows.append(dict(model=kind,reference=ref,horizon=h,
            accepted=bool(accepted[k]),nodes=int(nodes[k]),completeness_error_gb=float(errors[k]),l1_refinement_gb=float(changes[k])))
local_ig_audit=pd.DataFrame(ig_case_rows)
display(local_ig_audit)
''')
c('''
# Compare signed local credits only on accepted IG cases; no forced agreement assertion.
fig,axes=plt.subplots(1,3,figsize=(14,3.6),constrained_layout=True)
for ax,kind in zip(axes,["ridge","dlinear","gru"]):
    a=local_attributions[(kind,"source_calendar")]["shapley"][0]
    igcase=local_ig[(kind,"source_calendar")]
    positions=np.arange(7)
    ax.bar(positions-.18,a,width=.36,label="Shapley")
    if igcase["accepted"][0]:
        ax.bar(positions+.18,igcase["credits"][0],width=.36,label="Accepted IG")
    else:
        ax.text(.05,.93,"IG rejected numerically",transform=ax.transAxes,color="#c16b24",va="top")
    ax.set_xticks(positions,DAY_NAMES,rotation=45);ax.axhline(0,c="gray",lw=.7)
    ax.set_ylabel("Signed daily credit, GB");ax.set_title(kind);ax.legend(fontsize=8)
plt.show()
''')
md('''
## 13. Controlled replacement operators — berbeda dari attribution references

Interpolation mengganti internal shape suatu hari dengan garis antara first/last value; endpoint information tetap ada. Rotation memakai cyclic shift satu hari dari observed week. Keduanya tanpa future labels tetapi dapat menghasilkan history yang tidak alami. Kita tidak menyebutnya causal interventions atau conditional-distribution samples.
''')
inline('benchmark_common.py','templates','response_game','quality')
c('''
operator_templates=templates(x_case)
fig,axes=plt.subplots(2,1,figsize=(12,5),sharex=True,constrained_layout=True)
for ax,(name,t) in zip(axes,operator_templates.items()):
    ax.plot(x_case,c="black",lw=1,label="Original")
    ax.plot(t,c="#c16b24",lw=1,label=name)
    for boundary in range(24,168,24):ax.axvline(boundary,c="gray",alpha=.2)
    shift=np.sqrt(np.mean((np.log1p(t)-np.log1p(x_case))**2))
    ax.set_title(f"{name}; log-input RMS shift={shift:.4f}");ax.set_ylabel("GB");ax.legend()
axes[-1].set_xlabel("History hour");plt.show()
''')
md('''
## 14. Menghitung Q langsung untuk satu kasus

Untuk ranking π, cumulative prediction difference Ck menjumlahkan **absolute sequential** changes ketika first k groups diganti. Utility U = mean(C1,C2,C4). Dari semua 5040 orderings, R adalah exact mean utility dan O adalah maximum response utility. Q=(U−R)/(O−R), undefined jika gap ≤1e-9 GB. Negative Q boleh; O bukan oracle forecast accuracy.
''')
c('''
local_quality_rows=[]; response_cache={}
model=predictors["gru"]
phi=local_attributions[("gru","source_calendar")]["shapley"]
occ=local_attributions[("gru","source_calendar")]["occlusion"]
igcase=local_ig[("gru","source_calendar")]
for op,t in operator_templates.items():
    values,random_mean,oracle=response_game(model,x_case,t)
    response_cache[op]=(values,random_mean,oracle)
    for k,h in enumerate(HORIZONS):
        key=f"{case_id}:{case.origin}:{h}"
        rankings={"shapley":order(abs(phi[k]),key),"occlusion":order(abs(occ[k]),key),"recency":np.arange(6,-1,-1)}
        if igcase["accepted"][k]:rankings["ig"]=order(abs(igcase["credits"][k]),key)
        for method,rank in rankings.items():
            utility,q,gap=quality(values,rank,random_mean,oracle)
            local_quality_rows.append(dict(operator=op,method=method,horizon=h,utility_gb=float(utility[k]),
                random_gb=float(random_mean[k]),oracle_gb=float(oracle[k]),gap_gb=float(gap[k]),quality_q=float(q[k])))
local_quality=pd.DataFrame(local_quality_rows)
display(local_quality)
''')
c('''
fig,axes=plt.subplots(1,2,figsize=(12,4),constrained_layout=True)
for ax,(op,(values,random_mean,oracle)) in zip(axes,response_cache.items()):
    sequential=abs(values[REMOVED[:,1:],0]-values[REMOVED[:,:-1],0])
    utilities=np.cumsum(sequential,axis=1)[:,[0,1,3]].mean(1)
    ax.hist(utilities,bins=30,color="#94a3b8",label="All 5040 orderings")
    ax.axvline(random_mean[0],c="#2365a0",label="Random mean")
    ax.axvline(oracle[0],c="#c16b24",label="Response oracle")
    ax.set_title(f"{op}, GRU h1");ax.set_xlabel("Utility GB");ax.legend(fontsize=8)
plt.show()
''')
c('''
fig,axes=plt.subplots(1,2,figsize=(12,4),constrained_layout=True)
for ax,(op,(values,random_mean,oracle)) in zip(axes,response_cache.items()):
    for method,rank in {"shapley":order(abs(phi[0]),f"{case_id}:{case.origin}:1"),
                        "occlusion":order(abs(occ[0]),f"{case_id}:{case.origin}:1"),
                        "recency":np.arange(6,-1,-1)}.items():
        masks=np.r_[0,np.cumsum(1<<rank)]
        cpd=np.r_[0,np.cumsum(abs(values[masks[1:],0]-values[masks[:-1],0]))]
        ax.plot(range(8),cpd,marker="o",label=method)
    ax.set_xlabel("Number of sequentially replaced day groups");ax.set_ylabel("Cumulative absolute response GB")
    ax.set_title(op);ax.legend()
plt.show()
''')
md('''
### 14.1 Cocokkan recomputation dengan hasil tersimpan

Pilih kasus yang sama, model/seed/horizon/reference/operator sama, dan shared tie key. Tidak cukup membandingkan average berbeda subjek. Kasus undefined tetap undefined.
''')
c('''
saved_case_quality=pd.read_csv(ROOT/"results/quality_gru_42.csv.gz")
z=saved_case_quality[(saved_case_quality.id==case_id)&(saved_case_quality.origin==case.origin)&
    (saved_case_quality.arm=="frozen")&(saved_case_quality.reference=="source_calendar")]
checks=[]
for row in local_quality.itertuples():
    saved=z[(z.operator==row.operator)&(z.method==row.method)&(z.horizon==row.horizon)].iloc[0]
    ok=np.isclose(row.quality_q,saved.quality_q,rtol=1e-8,atol=1e-10,equal_nan=True)
    checks.append(dict(method=row.method,horizon=row.horizon,operator=row.operator,match=bool(ok)))
assert all(r["match"] for r in checks)
display(pd.DataFrame(checks))
''')
md('''
## 15. Global attribution: pola per grup, cohort dan reference

Global importance dihitung dari mean absolute group credit, lalu equal institution-year means. Ini descriptive importance **pada sampled eligible origins**, bukan population causal effect. Tidak mencampur signed Shapley credits dengan occlusion magnitudes sebagai besaran yang identik.
''')
c('''
allocation_files=sorted((ROOT/"results").glob("allocations_*.csv.gz"))
allocations=pd.concat([pd.read_csv(p) for p in allocation_files],ignore_index=True)
score_cols=[f"score_{i}" for i in range(7)]
alloc=allocations.query("model=='gru' and arm=='frozen' and horizon==1 and method=='shapley'").copy()
alloc[score_cols]=alloc[score_cols].abs()
institution_importance=alloc.groupby(["id","cohort","year","reference"])[score_cols].mean().reset_index()
global_importance=institution_importance.groupby(["cohort","reference"])[score_cols].mean()
display(global_importance)
fig,axes=plt.subplots(1,2,figsize=(12,4),constrained_layout=True)
for ax,ref in zip(axes,["source_calendar","history_hour_median"]):
    pos=np.arange(7)
    for cohort,dx,col in [("source",-.18,"#2365a0"),("target",.18,"#c16b24")]:
        values=global_importance.loc[(cohort,ref)].to_numpy()
        ax.bar(pos+dx,values,width=.36,label=cohort,color=col)
    ax.set_xticks(pos,DAY_NAMES,rotation=45);ax.set_ylabel("Mean absolute group credit GB")
    ax.set_title(ref);ax.legend()
plt.show()
''')
md('''
## 16. Agreement metode dan kestabilan antar-training-seed

Top-3 Jaccard dan Kendall τ-b berikut membandingkan rankings untuk case/reference/horizon yang sama. High agreement tidak membuktikan faithfulness; methods bisa sepakat karena alasan yang salah. Antar-training-seed mengukur variasi model training, bukan stochastic rerun instability LIME (LIME tidak digunakan di studi ini).
''')
c('''
def ranking_agreement(a,b,key,top_k=3):
    ra=order(abs(np.asarray(a)),key);rb=order(abs(np.asarray(b)),key)
    ta=set(ra[:top_k]);tb=set(rb[:top_k])
    jaccard=len(ta&tb)/len(ta|tb)
    # Average ties in magnitude are kept for tau-b; deterministic tie keys only serve top-k.
    tau=float(kendalltau(abs(np.asarray(a)),abs(np.asarray(b))).statistic)
    return jaccard,tau

agreement_rows=[]
sub=allocations.query("model=='gru' and arm=='frozen' and horizon==1 and reference=='source_calendar'")
for key,g in sub.groupby(["id","seed","year","origin","cohort"]):
    bymethod={r.method:np.array([getattr(r,col) for col in score_cols]) for r in g.itertuples()}
    if "shapley" not in bymethod or "occlusion" not in bymethod:continue
    tie=f"{key[0]}:{key[3]}:1"
    j,t=ranking_agreement(bymethod["shapley"],bymethod["occlusion"],tie)
    agreement_rows.append(dict(id=key[0],seed=key[1],year=key[2],cohort=key[4],jaccard_top3=j,kendall_tau=t))
agreement_df=pd.DataFrame(agreement_rows)
# Average within institution-year before summary; counts are descriptive, not inferential N.
agreement_macro=agreement_df.groupby(["id","year","cohort"])[["jaccard_top3","kendall_tau"]].mean()
display(agreement_macro.groupby("cohort").mean())
''')
c('''
seed_agreement_rows=[]
for key,g in sub.query("method=='shapley'").groupby(["id","year","origin","cohort"]):
    byseed={int(r.seed):np.array([getattr(r,col) for col in score_cols]) for r in g.itertuples()}
    if set(byseed)!={42,123,2026}:continue
    for a,b in [(42,123),(42,2026),(123,2026)]:
        j,t=ranking_agreement(byseed[a],byseed[b],f"{key[0]}:{key[2]}:1")
        seed_agreement_rows.append(dict(id=key[0],year=key[1],cohort=key[3],seed_pair=f"{a}/{b}",jaccard_top3=j,kendall_tau=t))
seed_agreement_df=pd.DataFrame(seed_agreement_rows)
seed_macro=seed_agreement_df.groupby(["id","year","cohort","seed_pair"])[["jaccard_top3","kendall_tau"]].mean().reset_index()
display(seed_macro.groupby(["cohort","seed_pair"])[["jaccard_top3","kendall_tau"]].mean())
fig,ax=plt.subplots(figsize=(8,4),constrained_layout=True)
cohorts=["source","target"]
ax.boxplot([seed_macro.query("cohort==@cohort").jaccard_top3 for cohort in cohorts],tick_labels=cohorts)
ax.set_ylabel("Mean top-3 Jaccard across seed-pair rankings")
ax.set_title("Model-seed stability: descriptive institution-year summaries")
plt.show()
''')
md('''
## 17. Full numerical acceptance dan common-case comparisons

Jangan mengadu all-case Shapley dengan IG hanya pada subset yang lolos. Untuk plot komparatif berikut, pasangan metode memakai **intersection cases dengan Q defined untuk kedua metode**. Common-case plot bersifat eksploratori dan tidak mengganti primary all-case Shapley analysis.
''')
c('''
quality_paths=sorted((ROOT/"results").glob("quality_*.csv.gz"))
quality_all=pd.concat([pd.read_csv(p) for p in quality_paths],ignore_index=True)
numerics=pd.concat([pd.read_csv(p).assign(model=p.stem.split("_")[2],seed=int(p.stem.split("_")[-1]))
                   for p in sorted((ROOT/"results").glob("ig_numerics_*.csv"))],ignore_index=True)
ig_totals=numerics.groupby("model").agg(cases=("accepted","size"),accepted=("accepted","sum"))
ig_totals["failed"]=ig_totals.cases-ig_totals.accepted
ig_totals["acceptance_rate"]=ig_totals.accepted/ig_totals.cases
display(ig_totals)
assert (~numerics.accepted).sum()==claims["ig_failed"]
assert quality_all.query("method=='ig' and not accepted").quality_q.isna().all()
fig,ax=plt.subplots(figsize=(7,3.5),constrained_layout=True)
ax.bar(ig_totals.index,ig_totals.acceptance_rate,color="#0d9488")
ax.set_ylim(0,1.05);ax.set_ylabel("Numerical acceptance fraction")
ax.set_title("Fixed completeness + L1-refinement criteria")
plt.show()
''')
c('''
compare=quality_all.query("model=='gru' and arm=='frozen' and horizon==1 and reference=='source_calendar' and method in ['shapley','ig']")
common_keys=["id","seed","year","origin","cohort","operator"]
common=compare.pivot_table(index=common_keys,columns="method",values="quality_q").dropna(subset=["shapley","ig"]).reset_index()
common_seed_keys=["id","year","origin","cohort","operator"]
seed_counts=common.groupby(common_seed_keys)["seed"].transform("nunique")
common=common[seed_counts==3].copy()
common_seed_average=common.groupby(common_seed_keys)[["shapley","ig"]].mean().reset_index()
common_macro=common_seed_average.groupby(["id","year","cohort"])[["shapley","ig"]].mean().reset_index()
print("Matched operator/seed cases (complete 3-seed sets):",len(common),"; available institution-year cells:",len(common_macro))
display(common_macro.groupby("cohort")[["shapley","ig"]].mean())
fig,ax=plt.subplots(figsize=(6,4),constrained_layout=True)
for cohort,color in [("source","#2365a0"),("target","#c16b24")]:
    z=common_macro.query("cohort==@cohort")
    ax.scatter(z.shapley,z.ig,color=color,label=cohort)
lo=min(common_macro.shapley.min(),common_macro.ig.min());hi=max(common_macro.shapley.max(),common_macro.ig.max())
ax.plot([lo,hi],[lo,hi],c="gray",ls="--");ax.set_xlabel("Shapley mean Q on common cases")
ax.set_ylabel("IG mean Q on common cases");ax.legend();plt.show()
''')
md('''
## 18. Primary paired estimate: seed completeness dan exact aggregation

Semua tiga neural seeds harus memiliki defined Q; Ridge cukup satu. Pasangan source/target harus punya timestamp yang sama. Empat cells (dua tahun × dua operators) harus tersedia untuk pair-level primary contribution. Data yang tidak lengkap disimpan, tidak diganti pasangan yang memberi hasil lebih menarik.
''')
c('''
seed_keys=["model","id","pair","cohort","year","arm","horizon","origin","reference","method","operator","ig_subset"]
seed_average=quality_all.groupby(seed_keys,dropna=False).quality_q.agg(["mean","count"]).reset_index()
seed_average["expected"]=np.where(seed_average.model.eq("ridge"),1,3)
seed_average.loc[seed_average["count"]!=seed_average.expected,"mean"]=np.nan
seed_average=seed_average.rename(columns={"mean":"quality_q"})
pair_keys=["model","pair","year","arm","horizon","origin","reference","method","operator","ig_subset"]
paired_quality=seed_average.pivot_table(index=pair_keys,columns="cohort",values="quality_q").reset_index()
paired_quality=paired_quality.dropna(subset=["source","target"])
paired_quality["delta"]=paired_quality.target-paired_quality.source
primary=paired_quality.query("model=='gru' and arm=='frozen' and horizon==1 and reference=='source_calendar' and method=='shapley'").copy()
cell_means=primary.groupby(["pair","year","operator"])[["source","target","delta"]].mean()
complete_pairs=cell_means.delta.unstack(["year","operator"]).dropna().index
primary_complete=primary[primary["pair"].isin(complete_pairs)]
point=cell_means.loc[complete_pairs].groupby("pair").mean().mean()
print("Paired origin/operator records before complete-pair restriction:",len(primary))
print("Records after complete-pair restriction:",len(primary_complete))
print("Complete pair IDs:",complete_pairs.tolist())
display(point.rename("equal-cell/equal-pair mean").to_frame())
assert np.isclose(point.delta,claims["primary"]["mean"],atol=1e-12)
''')
md('''
### 18.1 Paired institution/14-day-block bootstrap — kode dan penghitungan ulang

Resample pairs, lalu observed 14-day blocks dalam pair/year. Source/target/operator dibawa bersama. Draw dengan operator cell kosong dianggap invalid. Interval hanya jika ≥4 complete pairs dan ≥1000 valid dari 2000 attempts. Seeds dan banyak model queries bukan penambahan independent sample size. Seven related pairs membatasi kepastian interval.
''')
inline('analyze_full.py','bootstrap')
c('''
bootstrap_result=bootstrap(primary,B=2000)
print(json.dumps(bootstrap_result,indent=2))
for key in ["mean","ci_low","ci_high"]:
    assert np.isclose(bootstrap_result[key],claims["primary"][key],atol=1e-12)
assert bootstrap_result["bootstrap_valid"]==claims["primary"]["bootstrap_valid"]
print("Frozen primary bootstrap reproduced.")
''')
c('''
fig,axes=plt.subplots(1,2,figsize=(12,4),constrained_layout=True)
z=cell_means.loc[complete_pairs].groupby(["pair","operator"]).mean().reset_index()
for op,dx,marker in [("interpolation",-.08,"o"),("rotation",.08,"s")]:
    q=z.query("operator==@op")
    axes[0].scatter(q["pair"]+dx,q.delta,marker=marker,label=op)
axes[0].axhline(0,c="gray");axes[0].set_xticks(complete_pairs)
axes[0].set_xlabel("Complete institution pair");axes[0].set_ylabel("Target − source Q");axes[0].legend()
mean=bootstrap_result["mean"];low=bootstrap_result["ci_low"];high=bootstrap_result["ci_high"]
axes[1].errorbar([mean],[0],xerr=[[mean-low],[high-mean]],fmt="o",capsize=7)
axes[1].axvline(0,c="gray",ls="--");axes[1].set_yticks([0],["Primary GRU h1"])
axes[1].set_xlabel("Target − source Q; nominal 95% interval")
plt.show()
''')
md('''
## 19. Secondary reference/horizon sensitivity

Plot di bawah menunjukkan nominal exploratory intervals, tanpa multiplicity correction. Hasil history-median yang lebih negatif tidak dipromosikan sebagai primary setelah melihat outcome. Reference berbeda juga berarti explanatory contrast berbeda.
''')
c('''
secondary=pd.read_csv(ROOT/"results/secondary_quality_contrasts.csv")
display(secondary.round(6))
fig,axes=plt.subplots(1,2,figsize=(12,4),constrained_layout=True)
for ax,ref in zip(axes,["source_calendar","history_hour_median"]):
    z=secondary.query("reference==@ref").sort_values(["model","horizon"]).reset_index(drop=True)
    y=np.arange(len(z))
    ax.errorbar(z["mean"],y,xerr=np.vstack([z["mean"]-z.ci_low,z.ci_high-z["mean"]]),fmt="o",capsize=3)
    ax.set_yticks(y,[f"{r.model} {r.horizon}h" for r in z.itertuples()])
    ax.axvline(0,c="gray",ls="--");ax.set_title(ref);ax.set_xlabel("Exploratory target − source Q")
plt.show()
''')
md('''
## 20. Bias calibration dan robustness

Calibration menggunakan data lokal; arm ini bukan zero-shot. Perubahan MASE dan Q bukan kuantitas yang sama. Tidak menyimpulkan kausalitas antara membaiknya forecast dan membaiknya explanation dari dua descriptive averages.
''')
c('''
calibration_offsets=pd.read_csv(ROOT/"results/calibration_offsets.csv")
calibrated_table=macro.query("role=='target' and model in ['ridge','dlinear','gru']").pivot_table(index=["model","horizon"],columns="arm",values="mase")
calibrated_table["calibrated_minus_frozen"]=calibrated_table.calibrated-calibrated_table.frozen
display(calibrated_table.round(6))
display(calibration_offsets.groupby(["model","status"]).size().rename("offset_records").to_frame())
cal_q=pd.read_csv(ROOT/"results/calibration_quality_changes.csv.gz")
cal_q_summary=cal_q.query("cohort=='target' and horizon==1 and reference=='source_calendar'").groupby(["model","id","year"]).delta.mean().groupby("model").mean()
display(cal_q_summary.rename("Exploratory target calibration ΔQ").to_frame())
''')
md('''
## 21. Explanation latency — benchmark lokal tambahan

Bandingkan satu history/reference yang sama, dua endpoint sekaligus, CPU empat threads. Shapley menghitung 128 coalitions; occlusion hanya membutuhkan full + tujuh single-group replacement; IG memakai adaptive node budget yang sama. Angka ini microbenchmark deskriptif, bukan hasil general latency study atau angka yang diam-diam ditambahkan ke paper.
''')
c('''
def occlusion_only(model,x,r):
    inputs=np.repeat(x[None,:],8,axis=0)
    for j in range(7):inputs[j+1,j*24:(j+1)*24]=r[j*24:(j+1)*24]
    pred=model(inputs)
    return abs(pred[0]-pred[1:]).T

latency_rows=[]
latency_model=predictors["gru"];latency_ref=references["source_calendar"]
assert np.allclose(occlusion_only(latency_model,x_case,latency_ref),local_attributions[("gru","source_calendar")]["occlusion"])
for method,fn in [("Exact 7-group Shapley",lambda:games(latency_model,x_case,latency_ref)),
                  ("Single-group occlusion",lambda:occlusion_only(latency_model,x_case,latency_ref)),
                  ("Adaptive IG",lambda:integrated_gradients(latency_model,x_case,latency_ref))]:
    fn()  # warm-up excluded
    for repeat in range(3):
        t0=time.perf_counter();fn();elapsed=time.perf_counter()-t0
        latency_rows.append(dict(method=method,repeat=repeat,seconds=elapsed))
latency_df=pd.DataFrame(latency_rows)
display(latency_df.groupby("method").seconds.agg(["median","min","max"]))
fig,ax=plt.subplots(figsize=(9,3),constrained_layout=True)
z=latency_df.groupby("method").seconds.median()
ax.barh(z.index,z.values,color="#2365a0");ax.set_xlabel("Median seconds / case (both endpoints)")
plt.show()
''')
md('''
## 22. Full pipeline evaluation — implementasi inline untuk rerun

Tiga fungsi di bawah adalah mirror kode batch canonical: forecast metrics, attribution evaluation, dan statistical analysis. Mereka tidak dieksekusi pada mode default. Kode tampak penuh dan menggunakan fungsi yang sudah didefinisikan di notebook, bukan memanggil subprocess script. Bagian berikut mengarahkan penulisan ke clone baru.

Fungsi analysis menyimpan beberapa historical descriptive figures; untuk primary panel yang benar gunakan aggregation complete pairs pada Bagian 18. Local added analyses tetap exploratory.
''')
inline('evaluate_forecasts.py','main',rename={'main':'evaluate_forecasts_inline'})
inline('evaluate_attributions.py','main',rename={'main':'evaluate_attributions_inline'})
inline('analyze_full.py','main',rename={'main':'analyze_results_inline'})
md('''
### 22.1 Jalankan reproduksi penuh pada clone baru

Aktifkan `RUN_FULL_TRAINING` dan/atau `RUN_FULL_EVALUATION` di konfigurasi, lalu jalankan kembali sel ini. Training-only tidak otomatis menghasilkan target metrics baru. Evaluation-only menggunakan checkpoint yang disertakan. Clone menyimpan artifacts lama sebagai pembanding yang akan ditimpa per tahap; `NOTEBOOK_RERUN_CONTEXT.json` mencatat tahap yang benar-benar dijalankan agar hasil lama tidak dianggap hasil rerun.

Ini bukan eksperimen baru atau hasil confirmatory baru. Jangan mengedit frozen split/hyperparameters hanya untuk mencari target result yang lebih kuat. ROOT dikembalikan ke original setelah selesai, termasuk ketika terjadi error.
''')
c('''
if RUN_FULL_TRAINING or RUN_FULL_EVALUATION:
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    run_root=SOURCE_ROOT.parent/"work"/"xai_notebook_reruns"/stamp
    shutil.copytree(SOURCE_ROOT,run_root,ignore=shutil.ignore_patterns("__pycache__","*.aux","*.log","*.out"))
    context={"status":"running","implementation":"inline notebook mirror","fresh_holdout":False,
             "training_requested":RUN_FULL_TRAINING,"evaluation_requested":RUN_FULL_EVALUATION,"completed_steps":[],
             "warning":"Clone contains baseline artifacts; only completed_steps are recomputed."}
    ROOT=run_root
    try:
        (ROOT/"results/NOTEBOOK_RERUN_CONTEXT.json").write_text(json.dumps(context,indent=2))
        steps=([("training",train_all_models_inline)] if RUN_FULL_TRAINING else [])
        if RUN_FULL_EVALUATION:
            steps += [("forecasts",evaluate_forecasts_inline),("attributions",evaluate_attributions_inline),("analysis",analyze_results_inline)]
        for name,fn in steps:
            print("Running inline:",name,flush=True);fn();context["completed_steps"].append(name)
            (ROOT/"results/NOTEBOOK_RERUN_CONTEXT.json").write_text(json.dumps(context,indent=2))
        context["status"]="completed"
    except Exception:
        context["status"]="failed";raise
    finally:
        (ROOT/"results/NOTEBOOK_RERUN_CONTEXT.json").write_text(json.dumps(context,indent=2))
        ROOT=SOURCE_ROOT
    print("Clone saved:",run_root)
else:
    print("Full training and batch evaluation disabled; original artifacts unchanged.")
''')
md('''
## 23. Export analisis notebook dan konsistensi ilmiah

Export optional menulis hanya local/exploratory notebook derivatives ke folder kerja baru. Tidak mengganti main study result files. Latency, agreement, dan kasus lokal tidak dipromosikan menjadi hasil primer.
''')
c('''
if EXPORT_EXPLORATORY:
    output_dir=SOURCE_ROOT.parent/"work"/"xai_notebook_exports"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    output_dir.mkdir(parents=True,exist_ok=False)
    for name,frame in {"local_attribution_numerics":local_numerics,"local_ig_audit":local_ig_audit,
                       "local_quality":local_quality,"method_agreement":agreement_df,
                       "seed_agreement":seed_agreement_df,"local_latency":latency_df}.items():
        frame.to_csv(output_dir/f"{name}.csv",index=False)
    print("Exploratory exports:",output_dir)
else:
    print("Exploratory export disabled; outputs are embedded in notebook.")

# Read-only post-run consistency guards.
for item in training_record["models"]:
    assert hashlib.sha256((SOURCE_ROOT/"models"/item["file"]).read_bytes()).hexdigest()==item["sha256"]
assert json.loads((SOURCE_ROOT/"results/NUMERIC_CLAIMS.json").read_text())["primary"]==claims["primary"]
assert len(complete_pairs)==7 and len(primary)==369
assert int((~numerics.accepted).sum())==210
print("Original checkpoints and primary result preserved; notebook checks passed.")
''')
md('''
## 24. Interpretasi, gap, dan artefak paper

**Yang didukung:** primary target−source Q sekitar −0.019 dengan nominal 95% interval yang mencakup nol; model linear kompetitif pada forecasting; reference/operator memberi hasil berbeda; finite-budget IG rejection perlu dilaporkan.

**Yang belum didukung:** degradasi universal, equivalence/non-inferiority, causal demand explanation, klaim pertama explanation transfer, superiority terhadap specialized explainers yang tidak diimplementasikan, atau generalisasi lintas ISP.

Transfer forecasting sudah dibahas [TransMUSE](https://doi.org/10.1016/j.comnet.2022.109518), temporal network explanations oleh [AIChronoLens](https://doi.org/10.1109/TMC.2025.3554035), explanation generalization oleh [TimeSAE, ICML 2026](https://arxiv.org/abs/2601.09776v2), dan temporal evaluation oleh [TIMING](https://proceedings.mlr.press/v267/jang25a.html). Kontribusi kita adalah empirical reliability audit dengan setting/control yang eksplisit, bukan algoritma baru.

- [Paper PDF](paper/paper.pdf), [LaTeX](paper/paper.tex), [PPT editable](presentation/XAI_Research_Results_v2.pptx).
- [Protocol](FULL_PROTOCOL.md), [analysis clarifications](ANALYSIS_CLARIFICATIONS.md), [literature matrix](LITERATURE_AND_GAP.md).
- [Results brief Indonesia](RESULTS_BRIEF_ID.md), [data attribution](DATA_ATTRIBUTION.md), [validation notes](VALIDATION_NOTES.md).

## 25. Pemeriksaan sebelum memakai hasil untuk submission

1. Pastikan kernel/environment, file hashes dan chronological split sesuai.
2. Pisahkan default notebook recomputations, full rerun stages, dan original paper artifacts.
3. Laporkan missing pair-year, denominator failures, failed IG dan common-case restrictions.
4. Pertahankan primary endpoint, jangan memilih reference/model signifikan setelah target dibuka.
5. Sesuaikan venue, authorship/afiliasi dan disclosure. Belum ada submission.

Notebook referensi hananlu/xai dipakai sebagai inspirasi kedalaman penyajian; task, dataset, statistical unit dan klaim ilmiah proyek ini tetap forecasting institusi.
''')
nb=nbf.v4.new_notebook(cells=cells,metadata={"kernelspec":{"display_name":"Python 3 (XAI)","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.11"},"xai_notebook":{"reference":"https://github.com/hananlu/xai/blob/master/XAI_Network_Traffic.ipynb","reference_role":"structural inspiration; no classification code copied","default_mode":"inspect_recompute","full_retraining_default":False}})
nbf.validate(nb)
path=R/'XAI_Complete_Experiment.ipynb';nbf.write(nb,path)
print(json.dumps({"path":str(path),"cells":len(cells),"code_cells":sum(c.cell_type=='code' for c in cells),"code_lines":sum(len(c.source.splitlines()) for c in cells if c.cell_type=='code')},indent=2))
