# Defect Risk Model Card

## Purpose
Estimate probability of a downstream defect from pre-disposition process/context signals and support quality decision prioritization.

## Validation design
Data is ordered by event time and split 80/20 so evaluation occurs on future observations rather than a random shuffled holdout. Metrics include ROC AUC, average precision, balanced accuracy and Brier score.

## Explainability
For the baseline logistic model, standardized feature values are multiplied by model coefficients to produce signed local contributions. These are **model contributions, not causal claims**.

## Limitations
Synthetic validation proves the software/analysis workflow, not real-world generalization. Deployment requires plant-specific sampling design, leakage review, calibration, drift monitoring, subgroup validation and human quality-engineer approval.
