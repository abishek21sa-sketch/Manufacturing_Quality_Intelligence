# Frontend Demo Flow — Manufacturing Quality Intelligence

This product keeps its own visual language: **SPC-metrology quality control room**. The shared contract is behavioral evidence, not a shared layout or theme.

## Native entrypoint

`src/mqi/service/static/index.html`

## Project-specific demo sequence

1. load a process observation
2. inspect SPC and gage evidence
3. compare inspection economics
4. review adaptive containment
5. approve quality action

## Evidence requirements

The screen must show the project-native inputs, objective, constraints, baseline/counterfactual, evidence class, signature decision, and human approval/hold state. The product must not imply autonomous actuation.

## API evidence surface

The read-only signature evidence endpoint is `/v1/governance/signature`. Its response is linked to `artifacts/fortune50_capability_benchmark.json` and exposes the current decision, baseline, sensitivity/counterfactual evidence, and human-gated status.
