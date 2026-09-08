# ECON-SPC-P — Signature Algorithm Contract

This document is the project-native mathematical center required by the portfolio governance pack. The implementation alias is **GAGE-SHIELD inspection policy**.

## Operational decision

The module makes one operational decision: **choose which lines to inspect when inspection capacity is limited and escapes have asymmetric cost**.

## Mathematical center

- **Decision variables:** binary inspection action per line; prior defect probability and gage operating characteristics.
- **Objective:** minimize expected inspection cost plus expected escape cost.
- **Constraints and release gates:** inspection count <= capacity; sensitivity and specificity remain explicit inputs.
- **Determinism:** the reference contract is deterministic for a fixed candidate set, scenario, and seed.
- **Solver status:** the current reference is an executable enumerative/closed-form contract; production solver integration remains downstream of this gate.

## Baseline and counterfactual

The named baseline is **no-inspection risk-only policy**. The counterfactual is evaluated on the same inputs and scenario so that a claimed improvement cannot be caused by a changed data slice.

## Ablation

The declared ablation is to **replace the informative gage with a non-informative 0.5/0.5 gage**. It is executable through the module's `ablation(...)` function and is covered by the signature tests.

## Sensitivity

The sensitivity sweep is: **vary inspection capacity and gage sensitivity; report feasibility and expected-cost response**. Sensitivity output is evidence about robustness, not a claim of causal production impact.

## Evidence classes and authority

Evidence is kept separate as observed, simulated, optimized, shadow-mode, and realized. **observed quality data and public benchmark context; simulated decision scenarios; shadow-mode boundary for operational use** A human authority remains required before any operational action; autonomous execution is disabled.

## Implementation and acceptance

- Implementation: `src/mqi/optimization/signature_algorithm.py`
- Windows acceptance test: `tests/test_signature_algorithm.py`
- Required acceptance result: `4 tests, OK`, with invalid inputs and no-feasible cases controlled explicitly.

## Release boundary

This signature is release-ready only when this contract, the research-validation protocol, the machine-readable governance artifact, the existing Airlines 1.5x gates, and the final integrity/hash checks all pass together.
