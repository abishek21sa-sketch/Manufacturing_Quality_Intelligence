# Quality Engineering Methodology

The quality layer deliberately remains separate from AI. Statistical evidence can therefore trigger action even when a model is unavailable.

Implemented utilities include individuals control limits, p-chart limits, rule-1 special-cause detection, Cp/Cpk, a conservative acceptance-sampling helper, crossed Gage R&R approximation, PFMEA RPN ranking and two-level factorial DOE generation/main-effect estimation.

## Important engineering constraints

- Capability estimates are meaningful only after process stability has been evaluated.
- Gage R&R conclusions require a properly designed measurement study; the included implementation validates mechanics on balanced fixtures.
- Acceptance sampling is not process control and cannot substitute for process capability improvement.
- PFMEA ratings remain expert inputs; RPN is prioritization evidence, not automated causal truth.


## Industrial Engineering layer

The repository also computes first-pass yield, DPMO-style defect rate, cost of poor quality, defect Pareto prioritization and simple bottleneck/takt feasibility so quality decisions remain connected to production-system performance rather than isolated analytics.
