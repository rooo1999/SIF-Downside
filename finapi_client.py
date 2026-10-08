"""NAV history from finapi.upvaly.com (same endpoint, response shape and incremental
disk cache as the upvaly_client in the original SIF Tracker). Covers SIFs and mutual funds."""
import datetime as dt
import json
import os
import time
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://finapi.upvaly.com"
CACHE_DIR = Path(__file__).parent / "nav_cache"
CACHE_DIR.mkdir(exist_ok=True)
FLOOR_DATE = dt.date(2020, 1, 1)

_session = requests.Session()
_session.headers.update({"User-Agent": "Mozilla/5.0 (sif-downside-dashboard/1.0)"})
_key = os.environ.get("UPVALY_API_KEY")  # optional, only if you have a paid key / hit rate limits
if _key:
    _session.headers.update({"X-API-Key": _key})

DATE_KEYS = ["date", "navDate", "nav_date", "asOfDate", "as_of_date"]
NAV_KEYS = ["nav", "navValue", "nav_value", "value", "netAssetValue"]
WRAP_KEYS = ["navHistory", "nav_history", "history", "navs", "data", "result", "nav"]


def _first(d, keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            return d[k]
    return None


def _unwrap(obj):
    if isinstance(obj, dict):
        for k in WRAP_KEYS:
            if k in obj:
                return obj[k]
    return obj


def _get(url, params, retries=3):
    err = None
    for i in range(retries):
        try:
            r = _session.get(url, params=params, timeout=20)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:  # 4xx/5xx: retrying won't help
            raise RuntimeError(f"HTTP {e.response.status_code}: {e.response.text[:200]}") from None
        except Exception as e:  # noqa: BLE001 - network/timeout: retry
            err = e
            time.sleep(0.4 * (i + 1))
    raise RuntimeError(f"request failed: {err}")


def _parse(raw) -> pd.DataFrame:
    entries = _unwrap(raw)
    if isinstance(entries, dict):
        entries = _unwrap(entries)
    rows = [{"date": _first(e, DATE_KEYS), "nav": _first(e, NAV_KEYS)} for e in entries if isinstance(e, dict)] \
        if isinstance(entries, list) else []
    df = pd.DataFrame(rows, columns=["date", "nav"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    return df.dropna().drop_duplicates("date").sort_values("date")


ISIN_CACHE = CACHE_DIR / "isin_to_code.json"


def resolve_isin(isin: str):
    """ISIN -> finapi scheme code via /api/mf/isin/{isin}, cached on disk."""
    cached = json.loads(ISIN_CACHE.read_text()) if ISIN_CACHE.exists() else {}
    if isin not in cached:
        raw = _get(f"{BASE_URL}/api/mf/isin/{isin}", None)
        if isinstance(raw, dict) and raw.get("status") not in (None, "success"):
            raise RuntimeError(f"ISIN {isin}: API status={raw.get('status')}: {raw.get('message')}")
        payload = raw.get("data", raw) if isinstance(raw, dict) else raw
        if isinstance(payload, list) and payload:
            payload = payload[0]
        code = _first(payload, ["schemeCode", "scheme_code", "code", "id", "schemeId"])
        if code is None:
            raise RuntimeError(f"ISIN {isin}: no scheme code in API response")
        cached[isin] = code
        ISIN_CACHE.write_text(json.dumps(cached))
    return cached[isin]


def get_nav(code) -> pd.Series:
    """Daily NAV as a date-indexed Series, oldest first. `code` is a scheme code, or an ISIN
    string (INF...) which is resolved to one. Only fetches what the cache is missing."""
    if isinstance(code, str) and code.startswith("INF"):
        code = resolve_isin(code)
    if os.environ.get("SIF_DEMO") == "1":
        import demo_data
        return demo_data.nav(code)

    cache = CACHE_DIR / f"scheme_{code}.csv"
    df = pd.read_csv(cache, parse_dates=["date"]) if cache.exists() else pd.DataFrame(columns=["date", "nav"])
    start = FLOOR_DATE if df.empty else (df["date"].max() + pd.Timedelta(days=1)).date()
    today = dt.date.today()
    if start <= today:
        try:
            raw = _get(f"{BASE_URL}/api/mf/scheme-code/{code}/nav",
                       {"startDate": start.isoformat(), "endDate": today.isoformat()})
            if isinstance(raw, dict) and raw.get("status") not in (None, "success"):
                raise RuntimeError(f"API status={raw.get('status')}: {raw.get('message')}")
            new = _parse(raw)
            if not new.empty:
                df = pd.concat([df, new]).drop_duplicates("date").sort_values("date")
                df.to_csv(cache, index=False)
        except Exception:
            if df.empty:
                raise
    if df.empty:
        raise ValueError(f"no NAV data returned for scheme code {code}")
    return df.set_index("date")["nav"].astype(float)
