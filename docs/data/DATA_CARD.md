# Data Card

## Canonical demonstration data

The repository generates a fixed-seed synthetic manufacturing process stream with process settings, material/context variables, dimensional/surface outcomes and defect labels. It deliberately includes drift and nonlinear risk structure so monitoring and prediction can be tested reproducibly.

This dataset is **not represented as real plant data** and must not be used to claim industrial effect sizes.

## External benchmark

An optional adapter retrieves UCI SECOM (dataset id 179) for external pass/fail manufacturing benchmark work. External data stays behind an adapter because its anonymous sensor columns are not a production domain schema.

## Leakage controls

Model inputs exclude post-inspection quality outcomes (`dimension_error_mm`, `surface_roughness_ra`, `defect_type`) so prediction occurs from process/context variables available before final quality disposition.
