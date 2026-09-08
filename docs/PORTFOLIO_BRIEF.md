# Portfolio Brief — Manufacturing Quality Intelligence Platform

## Positioning

A manufacturing quality decision intelligence platform that moves beyond defect reporting by integrating Statistical Process Control, Measurement System Analysis, predictive AI, explainable root-cause evidence, Monte Carlo quality-risk simulation and inspection optimization into one operational decision loop.

## Engineering depth demonstrated

- **Quality Engineering:** SPC, Cp/Cpk, EWMA, CUSUM, Hotelling T², Gage R&R, acceptance sampling, PFMEA and DOE utilities.
- **Industrial Engineering:** quality-cost reasoning, yield/defect metrics, Pareto/bottleneck utilities and operational action design.
- **Artificial Intelligence:** temporally validated defect-risk prediction, anomaly detection, feature-contribution explanations and drift monitoring.
- **Operations Research:** cost-aware inspection policy optimization and capacity-constrained multi-station inspection allocation.
- **Simulation:** Monte Carlo propagation of defect probability into defect-count and cost exposure.
- **Enterprise Software:** modular package architecture, REST APIs, persistent decision audit trail, frontend, CI, Docker, tests and machine-readable evidence.

## Reproducible evidence in release 1.5.0

The fixed-seed validation run uses a leakage-resistant temporal 70/10/20 train/validation/test design. Current untouched-test metrics include ROC AUC approximately 0.756 and Brier score approximately 0.103. The quality validation also produces Cpk approximately 0.807 and Gage R&R study variation approximately 4.4%. These are synthetic-system engineering results and are not represented as real-factory performance.

The automated repository test suite contains **27 passing tests** and the API smoke evidence demonstrates model loading, decision generation, SQLite decision persistence, validation-evidence retrieval and advanced-SPC endpoints.

## Portfolio-safe description

> Built an enterprise-oriented manufacturing quality decision intelligence platform integrating SPC/MSA, temporally validated defect-risk AI, multivariate and drift monitoring, Monte Carlo quality-cost simulation, and inspection optimization; exposed recommendations through FastAPI with a persistent audit trail, automated tests, Docker/CI assets, and reproducible validation evidence.

## Remaining production-deployment boundary

The repository intentionally does not claim real-plant validation, MES/QMS/SCADA certification, enterprise identity integration or production cloud observability. Those require access to the target manufacturing environment and are distinct from repository-level portfolio engineering.
