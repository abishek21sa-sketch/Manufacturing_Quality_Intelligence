# Manufacturing Quality Intelligence — Airlines-1.5× Depth Candidate

Release: `MQI_FORTUNE50_AIRLINES15X_RC4`

## What changed

This release adds a provenance-aware empirical backbone, a live empirical API, project-native historical/entity diagnostics, a named empirical case study, external-source refresh/promotion workflow, live empirical charts, and a 26+ workspace contract in which each workspace has a distinct method/evidence/action definition.

## Current evidence mode

- Source: **Steel Plates Faults**
- Source URL: https://archive.ics.uci.edu/dataset/198/steel+plates+faults
- Mode: **offline_reference**
- Promotion state: **REFERENCE_ONLY**
- Local analyzable evidence: **250 rows / 16 fields**
- Workspaces: **26**

## Domain diagnostic

**quality escape stratification and inspection economics precursor**

Reference metrics:
```json
{
  "records": 250,
  "overall_defect_rate": 0.012,
  "high_wear_defect_rate": 0.0312,
  "lower_wear_defect_rate": 0.0054,
  "wear_q75": 27.169
}
```

Decision signal: Feed high-risk line/shift/factor evidence into defect prediction, then let GAGE-SHIELD and ECON-SPC-P allocate trustworthy inspection capacity.

## Analytical chain

source provenance → schema/data-quality checks → entity/factor drilldown → cohort/history comparison → diagnostic ranking → predictive model → original algorithm → OR/simulation escalation → counterfactual challenge → human decision

## Windows gates

Core/offline acceptance:
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows_airlines15x_acceptance.ps1
```

External-data promotion (internet required):
```powershell
.\scripts\windows_external_data_promotion.ps1
```

## Claim boundary

External-source results are claimed only when data_mode is refreshed_external or published_external_snapshot; offline_reference remains reference evidence.

The label “Airlines-1.5×” is an internal portfolio-depth target relative to the latest observable Airlines evidence, not an external company certification and not a claim that reference/synthetic data is real production evidence.
