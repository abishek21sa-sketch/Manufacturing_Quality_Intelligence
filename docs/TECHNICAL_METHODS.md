# Technical Methods

## A. Artificial Intelligence

### Temporal defect-risk model
- **Task:** binary defect-risk estimation for a process observation.
- **Model:** standardized, median-imputed logistic regression.
- **Features:** temperature (°C), pressure (bar), speed (m/min), vibration (mm/s), tool wear (%), material hardness, humidity (%), operator experience (years).
- **Target:** defect indicator (0/1).
- **Training data:** deterministic synthetic process stream for bundled validation; UCI SECOM is supported as an external benchmark adapter but is not claimed as bundled historical validation.
- **Validation:** time-ordered 70% train / 10% validation / 20% untouched test. Decision threshold is selected only on validation data.
- **Baseline:** logistic regression is intentionally the calibrated probability baseline because its probability feeds downstream simulation and optimization.
- **Metrics:** ROC-AUC, average precision, balanced accuracy, Brier score, observed defect rate vs mean predicted probability.
- **Uncertainty:** probability calibration is assessed with Brier score; the current model does not claim Bayesian posterior uncertainty.
- **Decision use:** predicted defect probability parameterizes expected escape cost, Monte Carlo defect exposure, inspection policy, and severity/action logic.
- **Implementation:** `src/mqi/ai/model.py`.
- **Limitations:** bundled performance is synthetic validation, not real-plant predictive accuracy.

### Anomaly and drift intelligence
Isolation-style anomaly scoring and PSI drift monitoring provide complementary evidence for unusual observations and distribution shift. They are monitoring signals, not causal root-cause proof. Implemented in `src/mqi/ai/anomaly.py` and `src/mqi/ai/monitoring.py`.

## B. Industrial Engineering

### Process capability
For two-sided specification limits:

`Cp = (USL - LSL) / (6σ)`

`Cpk = min((USL - μ)/(3σ), (μ - LSL)/(3σ))`

Units of μ and σ match the measured characteristic. Assumption: capability interpretation requires a sufficiently stable process. Implemented in `src/mqi/quality/spc.py`.

### Individuals SPC
The center line is the process mean. When sigma is not supplied, within-process sigma is estimated from the average moving range divided by 1.128; three-sigma limits are then applied. EWMA and CUSUM add small-shift sensitivity. Implemented in `src/mqi/quality/spc.py` and `advanced_spc.py`.

### Multivariate process monitoring
Hotelling T² evaluates correlated process variables jointly against a baseline covariance structure. It is used as a detection statistic, not as proof of causation. Implemented in `src/mqi/quality/advanced_spc.py`.

### Measurement System Analysis
Crossed Gage R&R decomposes repeatability/reproducibility contribution for a balanced part × operator study. Reported study variation is used to judge whether measurement noise is materially consuming process variation. Implemented in `src/mqi/quality/msa.py`.

### Quality economics and improvement
Yield, defect rates, COPQ, Pareto prioritization, takt/bottleneck utilities, PFMEA prioritization, acceptance sampling and factorial DOE utilities are executable quality/IE methods in `src/mqi/quality/`.

## C. Operations Research

### Multi-station inspection allocation MILP
**Decision variables:** binary `y[s,f] = 1` when station `s` receives inspection fraction `f` from a governed discrete policy set.

**Objective:** minimize expected inspection cost plus expected escaped-defect cost:

`min Σ_s Σ_f y[s,f] [V_s f C_i + V_s p_s (1 - f e) C_e]`

where `V_s` is station volume, `p_s` defect risk, `C_i` inspection cost/unit, `e` detection effectiveness, and `C_e` escape cost/defect.

**Constraints:**
1. `Σ_f y[s,f] = 1` for every station.
2. `Σ_s Σ_f V_s f y[s,f] ≤ inspection_capacity`.
3. `y[s,f] ∈ {0,1}`.

**Solver:** SciPy MILP interface using HiGHS. The formulation is solver-portable to Gurobi, but Gurobi is not required for this problem scale.

**Status handling:** OPTIMAL, LIMIT_REACHED, INFEASIBLE, UNBOUNDED and SOLVER_ERROR are interpreted explicitly. The returned result includes solver, status, capacity used and MIP gap where available.

**Validation/oracle:** `tests/test_or_milp.py` independently enumerates every policy combination for a small instance and verifies the MILP objective and feasibility against that exact oracle.

**Implementation:** `src/mqi/optimization/inspection.py`.

### Single-stream inspection policy
For one stream, the same expected-cost structure is evaluated over a small governed set of sampling fractions. This is exact finite policy optimization, not a heuristic ranking.

## Coupled decision architecture

`process data → SPC/multivariate state → defect probability → quality-cost consequence → inspection optimization → Monte Carlo stress test → corrective action`

AI estimates risk; IE methods establish quality state/economics; OR chooses a feasible inspection action; simulation quantifies stochastic exposure. Deterministic engineering remains functional without any LLM.
