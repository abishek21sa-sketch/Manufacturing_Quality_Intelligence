from __future__ import annotations

import pandas as pd


def load_secom() -> tuple[pd.DataFrame, pd.Series]:
    """Load UCI SECOM through ucimlrepo (optional dependency, internet required)."""
    try:
        from ucimlrepo import fetch_ucirepo
    except ImportError as exc:
        raise RuntimeError("Install optional dependency with: pip install -e '.[uci]'") from exc
    ds = fetch_ucirepo(id=179)
    x = ds.data.features.copy()
    y_raw = ds.data.targets.iloc[:, 0]
    y = (pd.to_numeric(y_raw, errors="coerce") == 1).astype(int)
    return x, y
