# Release 1.5.0 — Portfolio Completion Pass

This release closes the highest-value gaps between the initial v1.0 engineering build and a portfolio-grade final product.

## Material upgrades

1. Removed threshold-selection leakage by introducing a temporal 70/10/20 train/validation/test architecture.
2. Added EWMA and CUSUM for small-shift Statistical Process Control.
3. Added multivariate Hotelling T² monitoring for correlated process variables.
4. Added Population Stability Index monitoring and per-feature drift status.
5. Added SQLite persistence for operational decision auditing.
6. Added evidence and decision-history REST endpoints.
7. Upgraded the frontend from a single demo form into a quality operations command center.
8. Expanded automated validation coverage and machine-readable evidence.

## Intentionally not claimed

- Production deployment in a factory
- Validation against proprietary plant quality outcomes
- Production SSO/RBAC certification
- MES/QMS/SCADA connector certification
- Regulatory validation for a specific industry

Those are environment-specific deployment activities rather than repository-only engineering tasks.
