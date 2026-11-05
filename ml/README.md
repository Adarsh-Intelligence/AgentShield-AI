# AgentShield ML

One notebook, three models. See the [Root README](../README.md#%F0%9F%A7%A0-machine-learning-subsystem-agentshield-ml) and the PRD for the full spec; this file is the operating manual.

```
ml/
  notebooks/AgentShield_ML.ipynb      <- the single notebook (Sections 01-12)
  datasets/{raw,processed,metadata}/  <- raw/processed are git-ignored; metadata is committed
  artifacts/                          <- exported models (+ manifest.json with SHA-256 of every file)
  reports/{evaluation,visualizations}/
  docs/                               <- AUDIT.md, DATASETS.md, MODELS.md
  requirements-ml.txt
```

## Run it
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r ml/requirements-ml.txt        # for an NVIDIA GPU install the matching CUDA torch build first (pytorch.org)
export HF_TOKEN=...                          # only if a dataset is gated; never commit it
export AGENTSHIELD_DB_URL=postgresql://...   # optional: read REAL telemetry (read-only SELECT on test_results)
jupyter lab ml/notebooks/AgentShield_ML.ipynb   # Run All
# or headless:  jupyter nbconvert --to notebook --execute ml/notebooks/AgentShield_ML.ipynb --inplace
```
Device selection is automatic (CUDA with mixed precision, otherwise CPU). On CPU, DistilBERT trains on a capped subset and is marked PARTIAL.
Training is resumable: re-running continues from `artifacts/prompt_injection/checkpoints/ckpt_last.pt` if the configuration is unchanged.

## What to read after a run
`reports/evaluation/ML_REPORT.md` — **start with the "Run status" table.** A component marked SKIPPED/PARTIAL did not complete in that environment, and the report says why. The notebook never substitutes a stand-in for a skipped model.

## Export / integrate
Section 11 writes `artifacts/{prompt_injection,semantic_similarity,anomaly_detection}/` with a `config.json` each (thresholds, versions, warnings). Backend integration is **Phase 3** and has not started; the backend must *load* these artifacts, never run the notebook.

## Safety notes
Secrets only via environment variables. BIPIA-derived data includes CC BY-SA 4.0 material — don't commit/redistribute `datasets/processed/` without review. Exported anomaly artifacts are marked `production_ready: false` while trained on synthetic telemetry.
