"""Downside-protection maths. Everything is computed on the window that starts when
the SIF starts, using only dates on which all three series have a NAV."""
import numpy as np
import pandas as pd

KEYS = ["SIF", "MF", "BM"]


def align(sif: pd.Series, mf: pd.Series, bm: pd.Series) -> pd.DataFrame:
    """Common-date NAV frame starting at the SIF's first NAV (its inception)."""
    df = pd.concat([sif, mf, bm], axis=1, keys=KEYS, join="inner").dropna()
    df = df[(df > 0).all(axis=1)]  # a zero/negative NAV is bad data and would break returns
    return df[df.index >= sif.index.min()]


def rebase(nav: pd.DataFrame) -> pd.DataFrame:
    return nav / nav.iloc[0] * 100


def drawdown(reb: pd.DataFrame) -> pd.DataFrame:
    return reb / reb.cummax() - 1


def compound(r: pd.Series) -> float:
    return (1 + r).prod() - 1


def worst_days(rets: pd.DataFrame, n: int) -> pd.DataFrame:
    return rets.nsmallest(n, "BM")


def capture(r: pd.Series, bm: pd.Series, down: bool) -> float:
    """Average daily fund return / average daily benchmark return, on days the benchmark fell (down)
    or rose (up). Consistent with the 'average return on market-down days' row of the scorecard."""
    m = bm < 0 if down else bm > 0
    if m.sum() == 0 or bm[m].mean() == 0:
        return np.nan
    return r[m].mean() / bm[m].mean() * 100


def _ratio(up: float, down: float) -> float:
    """Up-capture / down-capture; only meaningful when the fund still lost on market-down days."""
    return up / down if down > 0 and not np.isnan(up) else np.nan


def scorecard(reb: pd.DataFrame, rets: pd.DataFrame, dd: pd.DataFrame) -> pd.DataFrame:
    bm, down = rets["BM"], rets["BM"] < 0
    rows = {}
    for c in KEYS:
        r = rets[c]
        rows[c] = dict(
            ret=reb[c].iloc[-1] - 100,
            mdd=dd[c].min() * 100,
            cur=dd[c].iloc[-1] * 100,
            worst=r.min() * 100,
            avgdown=r[down].mean() * 100 if down.any() else np.nan,
            dcap=capture(r, bm, True),
            ucap=capture(r, bm, False),
            hit=(r[down] > bm[down]).mean() * 100 if down.any() and c != "BM" else np.nan,
            vol=r.std(ddof=1) * np.sqrt(252) * 100 if len(r) > 2 else np.nan,
            avgup=r[bm > 0].mean() * 100 if (bm > 0).any() else np.nan,
            best=r.max() * 100,
            posdays=(r > 0).mean() * 100,
            udratio=_ratio(capture(r, bm, False), capture(r, bm, True)),
        )
    return pd.DataFrame(rows)


def episodes(bm_nav: pd.Series, thr: float):
    """Benchmark peak-to-trough falls of at least `thr` (e.g. 0.03) -> [(peak_i, trough_i)]."""
    v, out = bm_nav.values, []
    peak = trough = v[0]
    pi = ti = 0
    for i in range(1, len(v)):
        if v[i] >= peak:
            if trough / peak - 1 <= -thr:
                out.append((pi, ti))
            peak = trough = v[i]
            pi = ti = i
        elif v[i] < trough:
            trough, ti = v[i], i
    if trough / peak - 1 <= -thr:
        out.append((pi, ti))
    return out


def episode_table(nav: pd.DataFrame, thr: float) -> pd.DataFrame:
    rows = []
    for p, t in episodes(nav["BM"], thr):
        row = {"Peak": nav.index[p], "Trough": nav.index[t], "Days": t - p}
        for c in KEYS:
            row[c] = (nav[c].iloc[t] / nav[c].iloc[p] - 1) * 100
        rows.append(row)
    return pd.DataFrame(rows)


def inr(x: float) -> str:
    s = str(int(round(x)))
    if len(s) <= 3:
        return "₹" + s
    head, tail, parts = s[:-3], s[-3:], []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return "₹" + ",".join(parts + [tail])
