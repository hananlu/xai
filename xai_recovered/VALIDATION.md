# Validation

- All 15 recovered source hashes match the recovery manifest.
- Training protocol and experiment source match their frozen hashes.
- All 19 forecast files use identical 5,806 test origins and correct observed labels.
- All 38 MAE/RMSE/WAPE records recompute from saved per-origin forecasts.
- All 15 checkpoints reproduce three saved forecasts each within 0.001 GB (max 0.00001279 GB).
- All six explanation runs and 17,280 per-origin perturbation records are present and finite.
- Compiled PDF and fully populated editable manuscript are present.
- Negative raw test predictions across all model/horizon records: 0. Predictions were not clipped.
- Scientific limitation: IG numerical completeness fails in some cases; IG-based conclusions are explicitly provisional. Artifact integrity checks do not establish IG convergence.

Visual PDF review is recorded separately in STATUS.md.
