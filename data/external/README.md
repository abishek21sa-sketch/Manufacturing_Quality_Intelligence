# External data backbone

**Provider:** UCI Machine Learning Repository  
**Dataset:** Steel Plates Faults  
**Source:** https://archive.ics.uci.edu/dataset/198/steel+plates+faults  
**DOI/reference:** 10.24432/C5J88N  
**License/terms:** CC BY 4.0

Advertised source scale: 1,941 steel-plate observations × 27 measurements with seven fault classes.

The release includes a downloaded UCI snapshot at `data/external/uci_198.zip`, canonicalized into `data/raw/uci_steel/features.csv` and `targets.csv` for offline reproducibility. The source remains refreshable with `./data/external/fetch_public_data.ps1`; the current snapshot hash and acquisition date are recorded in `empirical/source_manifest.json`. Offline acceptance uses this public snapshot and never relabels synthetic fixtures as external observations.
