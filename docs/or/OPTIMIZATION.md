# Inspection Optimization

The optimization layer chooses inspection fractions by minimizing:

`inspection cost + expected escaped-defect cost`

subject to optional inspection capacity. A multi-station allocator performs an explicit finite search over allowed inspection fractions under a shared capacity constraint. The finite policy set makes the result deterministic, auditable and easy to validate.

Production extensions may add MILP/stochastic optimization for inspectors, stations, shifts, lots, risk classes, destructive-test constraints, service levels and robust uncertainty sets.
