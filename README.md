## AIRLINES-1.5× DEPTH CANDIDATE

Current release `MQI_FORTUNE50_AIRLINES15X_RC4` adds a live empirical/historical analysis layer, 26+ substantive workspaces, project-native domain diagnostics, external-source refresh/provenance, and AI decisions grounded in explicit evidence mode. See `docs/AIRLINES_15X_RELEASE.md`.

# Fortune-50 TENX analytical release

**Internal portfolio target:** Math 10/10 · UI 10/10 · AI 10/10, subject to the evidence boundaries below.

- Repository-authored algorithm: **GAGE-SHIELD-v1**
- Unique predictive-learning family: **Gradient-boosted decision-stump defect learning**
- Analytical AI role: **AI Quality Engineer**
- TENX workspaces: **20**
- Operational authority: **human-gated; autonomous execution blocked**

### Test the TENX layer on Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows_tenx_acceptance.ps1
.\scripts\start_tenx_workstation.ps1
```

The first command validates prediction → decision → counterfactual → OR escalation → user-aid behavior and a five-seed originality stress suite. The second opens the dedicated analytical workstation.

> **Evidence boundary:** TENX bundled metrics are synthetic/reference validation, not field deployment validation. Existing native Windows, Julia/Go/Rust/frontend, external-data, clinical, or production gates remain applicable where documented.

---


## Portfolio RC1 — ECON-SPC-P adaptive inspection

The product now integrates an MSA-aware finite-horizon inspection POMDP. Latent process-state belief, Gage R&R-derived observation quality, escape/correction economics, action cost, and shared inspection capacity jointly determine whether and where to inspect. This is a governed decision-support policy; it does not authorize plant inspection changes or claim realized savings.

# Manufacturing Quality Intelligence Platform

## Deployment

Deploy `src/mqi/service/static/` as the Vercel project root. Its `config.js`
routes browser API calls to the Render service declared in the root
`render.yaml`; override `window.__MQI_API_BASE__` for previews. Deploy the
repository root as a Render Blueprint, then verify `/health` and `/v1/evidence`
before opening the Vercel command center.

A production-structured manufacturing quality decision intelligence system implementing the governed loop **measure → detect → predict → diagnose → simulate → optimize → recommend**.

## Portfolio release 1.5.0

The repository combines Quality Engineering, Statistical Quality Control, AI, Operations Research, simulation and enterprise software engineering rather than treating them as isolated notebooks.

### Implemented capabilities

- Canonical manufacturing-quality data contract and deterministic process fixture generation
- Classical SPC: individuals limits, p-chart, rule-1 signals, Cp/Cpk and Six Sigma utilities
- Advanced SPC: **EWMA, CUSUM and multivariate Hotelling T²** monitoring
- MSA: crossed Gage R&R for balanced studies
- Quality methods: acceptance sampling, PFMEA prioritization and two-level factorial DOE utilities
- Industrial Engineering: yield/defect KPIs, COPQ, Pareto and takt/bottleneck utilities
- AI: temporal defect-risk model, anomaly detection and local coefficient contribution explanations
- Validation architecture: **70/10/20 temporal train/validation/test split**, with policy threshold selected only on the validation window
- Model/data monitoring: **Population Stability Index (PSI)** feature drift reporting
- Root-cause-to-corrective-action recommendation library
- Monte Carlo defect and quality-cost exposure simulation
- OR: cost-aware inspection optimization and constrained multi-station allocation
- Decision orchestration that converts risk + evidence + simulation + OR into an operational action
- **SQLite decision audit trail** with risk/severity/action history
- FastAPI REST service, interactive command-center frontend and machine-readable evidence endpoint
- Automated tests, Docker assets, CI workflow, validation artifacts and engineering documentation
- Optional **UCI SECOM** adapter for external semiconductor benchmark experiments

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
mqi bootstrap
pytest
uvicorn mqi.service.api:app --reload
```

Open `http://127.0.0.1:8000`. Interactive OpenAPI documentation is at `http://127.0.0.1:8000/docs`.

## Validation and evidence

`mqi bootstrap` creates a fixed-seed process stream, validates the canonical data contract, performs leakage-resistant temporal model validation, validates SPC/capability/MSA, evaluates advanced SPC and multivariate monitoring, checks PSI drift, runs Monte Carlo simulation, optimizes inspection and writes `artifacts/validation_report.json`.

The bundled numerical metrics are **engineering/reproducibility evidence on synthetic process data, not claims about an operating factory**. Real-plant external validation requires plant measurements and deployment access.

## Public benchmark adapter

The optional adapter `mqi.data.uci_secom.load_secom()` retrieves UCI SECOM when the `uci` extra and network access are available. Benchmark-specific fields are deliberately isolated from the canonical production domain model.

## Repository map

- `src/mqi/data` — contracts, fixtures and benchmark adapters
- `src/mqi/quality` — SPC, advanced SPC, MSA, PFMEA, DOE and IE-quality methods
- `src/mqi/ai` — defect prediction, anomaly detection, explainability and drift monitoring
- `src/mqi/simulation` — uncertainty and quality-cost simulation
- `src/mqi/optimization` — inspection and constrained resource allocation
- `src/mqi/decision` — operational recommendations and corrective-action mapping
- `src/mqi/persistence.py` — SQLite audit persistence
- `src/mqi/service` — REST API and command-center frontend
- `tests` — automated verification
- `docs` — architecture, methodology, work packages, validation and portfolio material
- `artifacts` — machine-readable reproducibility evidence

## Enterprise operability gate

This source release includes a governed decision-assurance layer, negative-path operability tests, hash-verifiable evidence, and a Windows enterprise acceptance gate. See `docs/ENTERPRISE_OPERABILITY.md`.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\\scripts\\windows_enterprise_acceptance.ps1
```


## Public Data Backbone
This release contains a structured public-data layer under `data/raw`, `data/processed`, `data/contracts`, `data/dictionaries`, `data/provenance`, and `data/snapshots`. Run `scripts\fetch_public_data_windows.ps1` when the primary public dataset is not bundled, then run `scripts\windows_real_data_acceptance.ps1`. `artifacts/data_backbone_status.json` records source state, row/feature counts, missingness, SHA-256, validation status, case-study state, claim boundary, model version, and the human decision authority.

The public-data case is `Steel Fault Risk and Measurement-Aware Inspection Allocation` and is wired into `GAGE-SHIELD-v1` review. Missing external raw data never silently falls back to a real-data claim; the dossier explicitly enters `REFERENCE_MODE_HOLD_FOR_REAL_DATA_CLAIM`.
