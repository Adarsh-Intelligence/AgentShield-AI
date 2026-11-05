# AgentShield ML — Run Report
_Generated 2026-11-05T13:20:34+00:00 · seed 42 · model_version 0.1.0_

## Run status

| Component | State | Reason |
|---|---|---|
| prompt_injection_distilbert | **SKIPPED** | missing: torch, transformers, Hub access |
| semantic_similarity | **SKIPPED** | missing: sentence-transformers, Hub access, STS-B data |
| anomaly_detection | **PARTIAL** | trained and evaluated on SYNTHETIC telemetry only (no real telemetry exists yet) |
| prompt_injection | **PARTIAL** | baseline only; trained/evaluated on BIPIA only (stand-alone prompt datasets and DistilBERT unavailable in this run) |

Environment: python=3.12.3, platform=Linux-6.18.44-fc-v236-x86_64-with-glibc2.39, datasets=5.1.0, sklearn=1.9.1, numpy=2.5.4, pandas=3.0.6, device=cpu, amp=False, huggingface_hub_reachable=False

## Data sources

| Source | Status | Licence | Revision | Accessed (UTC) |
|---|---|---|---|---|
| bipia | loaded | MIT | `a004b69ec0dd` | 2026-11-05T13:20:15+00:00 |
| deepset_prompt_injections | blocked | — | `—` | 2026-11-05T13:20:15+00:00 |
| neuralchemy_prompt_injection | blocked | — | `—` | 2026-11-05T13:20:15+00:00 |
| glue_stsb | blocked | — | `—` | 2026-11-05T13:20:15+00:00 |

- bipia: WikiTableQuestions (table task contexts): CC BY-SA 4.0 — attribution + share-alike apply to derived data

- bipia: Email contexts come from OpenAI Evals and code contexts from Stack Exchange per the BIPIA README; their licences are NOT stated in the repo and were not verified here — confirm before redistributing any dataset derived from BIPIA.

## Prompt-injection dataset

| Split | SAFE | MALICIOUS | total |
|---|---:|---:|---:|
| train | 292 | 292 | 584 |
| val | 74 | 74 | 148 |
| test | 178 | 178 | 356 |

Cleaning log: `{"dropped_empty_or_corrupted_contexts": 0, "dropped_duplicate_contexts_within_split": 310, "dropped_train_contexts_also_in_test": 11, "dropped_train_contexts_near_duplicate_of_test": 18, "near_duplicate_threshold": 0.8, "dropped_train_attack_categories_also_in_test": ["text:Language Translation"]}`

Leakage checks (all must be 0): exact=`{"train&val": 0, "train&test": 0, "val&test": 0}`, groups=`{"train&val": 0, "train&test": 0, "val&test": 0}`, attack-category=`{"train&val": 0, "train&test": 0, "val&test": 0}`

### Prompt-injection results (test split, threshold chosen on validation)

| Model | F1 | Precision | Recall | FPR | FNR | ROC-AUC | mean latency ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| length_only_shortcut | 0.664 | 0.524 | 0.904 | 0.820 | 0.096 | 0.598 | n/a |
| tfidf_lr | 0.801 | 0.693 | 0.949 | 0.421 | 0.051 | 0.891 | 0.649 |
| distilbert | NOT RUN | | | | | | |

Leave-one-source-group-out (baseline):

| held-out | F1 | recall | FPR | ROC-AUC |
|---|---:|---:|---:|---:|
| bipia_code | 0.667 | 1.000 | 1.000 | 0.768 |
| bipia_text | 0.106 | 0.056 | 0.005 | 0.746 |

## Semantic similarity

**Not run in this execution** (see status table). No similarity metrics are reported.

## Anomaly detection

**Data origin: SYNTHETIC** — metrics below describe a pipeline check on injected anomalies, not real-world performance.

Test (n=900, 25 anomalies): precision 0.941, recall 0.640, F1 0.762, FPR 0.001, ROC-AUC 0.950, PR-AUC 0.808.
Stability over 5 refits: F1 0.780 ± 0.031, flagged-set Jaccard 0.836.

| Injected scenario | recall | n (test) |
|---|---:|---:|
| empty_response | 1.000 | 6 |
| high_latency | 0.000 | 3 |
| mild_latency | 0.000 | 4 |
| prompt_stuffing | 1.000 | 2 |
| token_explosion | 0.667 | 3 |
| tool_storm | 0.667 | 3 |
| unauthorized_tool | 1.000 | 4 |

Per-scenario counts are very small; treat per-scenario recall as anecdotal.

## Blockers recorded during this run

- [data:deepset_prompt_injections] blocked: huggingface.co not reachable from this environment
- [data:neuralchemy_prompt_injection] blocked: huggingface.co not reachable from this environment
- [data:glue_stsb] blocked: huggingface.co not reachable from this environment
- [prompt_injection_distilbert] SKIPPED: missing: torch, transformers, Hub access
- [semantic_similarity] SKIPPED: missing: sentence-transformers, Hub access, STS-B data
- [anomaly_detection] PARTIAL: trained and evaluated on SYNTHETIC telemetry only (no real telemetry exists yet)
- [prompt_injection] PARTIAL: baseline only; trained/evaluated on BIPIA only (stand-alone prompt datasets and DistilBERT unavailable in this run)

## Limitations (always apply)

- Model scores are rankings against a threshold, not probabilities of malicious intent; keep deterministic security checks alongside ML.
- Semantic similarity does not establish factual correctness.
- Isolation Forest flags *unusual* behaviour, not confirmed malicious activity.
- BIPIA labels are defined by construction (inserted instruction = MALICIOUS); results on BIPIA do not transfer automatically to other attack styles.
- BIPIA-derived data includes CC BY-SA 4.0 material; the processed data folder is git-ignored by default.

## Reproducibility

Seed 42; BIPIA pinned to `a004b69ec0dd446e0afd461d98cb5e96e120a5d0`; Hub revisions pinned in `datasets/metadata/sources_lock.json`; split manifest in `datasets/metadata/prompt_injection_split_manifest.json`. Run the notebook top to bottom (see `ml/README.md`).