# Enterprise Readiness — Manufacturing Quality Intelligence

## Release status

**MQI_PORTFOLIO_RC1** is a portfolio release candidate, not a production deployment certification.

## Decision-system identity

Links measurement-system quality directly to adaptive shared-capacity inspection policy and modeled cost consequences.

**Signature core:** ECON-SPC-P MSA-aware finite-horizon inspection POMDP + quality economics

## Verified in this recovery build

- 33/33 Python regression tests verified
- Machine-readable validation evidence is included and hashed.
- Production writes/autonomous execution are blocked by release governance.
- Windows remains the primary local acceptance target.

## Evidence inventory

- `artifacts/portfolio_validation.json` — SHA-256 `a7589d4a2c9b397d22109f0ddf3ef74b7273afa599aa5bff66b5458ad4fdb86c`

## Gates still required before any production claim

- Windows PowerShell clean-environment acceptance
- Plant-specific MSA/escape/correction cost calibration
- External production-quality validation

## Claim boundary

This repository may be presented as a reproducible engineering/research decision system supported by its included model-based evidence. It must not be presented as real-world production improvement, certification, clinical effectiveness, vehicle certification, grid approval, or plant/fab performance unless that external validation is subsequently completed.
