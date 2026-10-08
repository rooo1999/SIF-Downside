"""Synthetic NAVs so the layout can be previewed (SIF_DEMO=1). NOT real data."""
import numpy as np
import pandas as pd

DAYS = {1: 520, 2: 520, 3: 135}  # SIF is recent, the others have longer history
BETA = {1: 1.0, 2: 0.95, 3: 0.45}


def nav(code: int) -> pd.Series:
    n = 520
    idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n)
    rng = np.random.default_rng(7)
    mkt = rng.normal(0.0004, 0.009, n)
    mkt[-90:-80] -= 0.004  # a correction inside the SIF's life
    r = BETA[code] * mkt + np.random.default_rng(code).normal(0.0001, 0.003, n)
    s = pd.Series(10 * np.cumprod(1 + r), index=idx)
    return s.iloc[-DAYS[code]:]
