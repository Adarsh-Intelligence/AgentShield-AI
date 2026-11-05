# Models, training configuration, evaluation method, limitations

Metrics are **not** copied here. Each run writes `reports/evaluation/ML_REPORT.md` and `metrics.json`; cite those.

## 1. Prompt-injection detection
- **Baseline:** word 1-2gram TF-IDF (`min_df=2`, sublinear TF, <=200k features) + Logistic Regression (`class_weight=balanced`); `C` chosen by validation PR-AUC.
- **DistilBERT:** `distilbert-base-uncased`, plain PyTorch loop; max length 384; AdamW lr 2e-5, weight decay 0.01, linear warmup 10 %, 3 epochs; class-weighted cross-entropy; gradient clipping 1.0; mixed precision on CUDA only; batch 16 (GPU) / 8 (CPU); best epoch by validation PR-AUC; per-epoch checkpoint with resume. On CPU the training set is capped (default 2000 stratified samples) and the run is marked PARTIAL.
- **Threshold:** chosen on validation only (`max_f1`, or `recall_floor`: highest threshold with recall >= 0.95). The report lists both operating points.
- **Metrics:** accuracy, precision, recall, F1, FPR, FNR, confusion matrix, ROC-AUC, PR-AUC, single-item inference latency; by source/task/position; recall by unseen attack category; leave-one-source-group-out (baseline).
- **Output contract** (reference class in notebook 06.7): predicted class, `malicious_score`, `confidence`, configured threshold, model version. The score is **not a calibrated probability**.
- **Selection rule:** DistilBERT is selected only if its validation PR-AUC beats the baseline's.

## 2. Semantic similarity
`sentence-transformers/all-MiniLM-L6-v2`, pretrained, cosine of normalised embeddings. Threshold = max-F1 on STS-B train with gold >= 4.0 as "similar"; evaluation on GLUE validation: Pearson, Spearman, MSE/MAE (raw `5*clip(cos,0,1)` mapping and a linear calibration fitted on the calibration set), precision/recall at threshold. Twelve author-written project pairs are included as illustration only.
The report also evaluates the backend's current hard-coded 0.80 threshold on the same test data for comparison.

## 3. Anomaly detection
Isolation Forest on `latency_ms, prompt_tokens, completion_tokens, completion_prompt_ratio, tool_call_count, unauthorized_tool_count` (impute 0 -> log1p -> RobustScaler, fitted on train). `fit()` never sees labels; labels are used only to choose `n_estimators / max_samples / contamination` on validation (documented). Evaluation: P/R/F1/FPR, confusion matrix, ROC/PR-AUC of the score, per-scenario recall, 5-refit stability, manual-review tables.

## Limitations
- Scores are rankings; keep deterministic security checks alongside ML. Never treat a prediction as a guaranteed security decision.
- BIPIA-only training covers *indirect* injection in emails/tables/code. Without the Hub prompt datasets the classifier has never seen direct injections, jailbreaks or system-prompt-extraction prompts.
- Similarity != factual correctness. Overlap between MiniLM's pre-training data and STS-B cannot be excluded here.
- Isolation Forest flags unusual behaviour, not malicious behaviour. With **synthetic** telemetry its metrics only demonstrate the pipeline. A pooled model cannot see a 6x latency spike on a fast agent that looks like a normal slow agent — per-agent baselines are a recommended next step.
- Hub revisions are pinned on first access; deleting `sources_lock.json` re-pins to latest.
