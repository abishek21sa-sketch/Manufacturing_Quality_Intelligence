# Research Validation Protocol — Manufacturing Quality Intelligence

This protocol implements the attached Research Validation & Benchmarking standard for **ECON-SPC-P**.

## Null hypothesis (H0)

H0: ECON-SPC-P does not reduce expected cost or change the policy relative to no inspection.

The null is not rejected by narrative alone. It is evaluated on a fixed reference scenario and declared seed set `[17, 29, 43]`.

## Baseline, metrics, and ablation

- **Baseline:** no-inspection risk-only policy.
- **Primary metrics:** objective value, feasibility, decision change versus baseline, constraint violations, runtime, and reproducibility.
- **Ablation:** replace the informative gage with a non-informative 0.5/0.5 gage.
- **Sensitivity grid:** vary inspection capacity and gage sensitivity; report feasibility and expected-cost response.
- **Expected reporting:** include solver status, selected decision, objective components, scenario/seed, baseline comparison, and any no-feasible result.

## Evidence separation

Observed data are used for context and predictive inputs; simulated data are used for controlled scenario testing; optimized outputs are decisions produced by the signature; shadow-mode results are recommendations without actuation; realized outcomes require a separately identified operational intervention. These classes must not be merged into a single production-performance claim.

## Failure and sensitivity checks

The acceptance suite covers invalid shapes or bounds, an ordinary feasible scenario, the declared ablation, and a deterministic sensitivity call. Any infeasible scenario must return a controlled no-feasible result or a documented validation error rather than silently relaxing a constraint.

## Scalability and external validation boundary

Record candidate/scenario count, runtime, solver status, and optimality gap when a solver is used. Public or synthetic evidence supports analytical validation only. Domain/field validation, prospective shadow mode, and realized intervention outcomes remain separate required stages.
