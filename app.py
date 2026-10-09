"""SIF Downside Protection Dashboard — SIF vs Mutual Fund vs Benchmark (data: finapi.upvaly.com).
Run:  streamlit run app.py      (preview with fake data:  SIF_DEMO=1 streamlit run app.py)"""
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import analytics as an
import finapi_client as api
import schemes

st.set_page_config(page_title="SIF Downside Protection", page_icon="🛡️", layout="wide")

DEMO = os.environ.get("SIF_DEMO") == "1"
if DEMO:
    schemes.SIFS = {"Demo SIF": 3}
    schemes.MUTUAL_FUNDS = {"Demo Mutual Fund": 2}
    schemes.BENCHMARKS = {"Demo Benchmark": 1}

BG, CARD, ALT, BORDER = "#0B1220", "#131B2E", "#161F36", "#242D42"
TEXT, BODY, MUTED = "#F1F4F8", "#C9D1DD", "#8B95A5"
GOLD, POS, NEG, AMBER = "#D4AF37", "#3ECF8E", "#FF6B6B", "#F5B041"
COL = {"SIF": GOLD, "MF": "#4FD1C5", "BM": "#8B95A5"}
LBL = {"SIF": "SIF", "MF": "Mutual fund", "BM": "Benchmark"}

st.markdown(
    f"""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
#MainMenu, footer, [data-testid="stHeader"] {{visibility:hidden;}}
html, body, .stApp {{background:{BG}; font-family:'Inter',sans-serif;}}
.block-container {{padding-top:1.6rem; max-width:1300px;}}
.title {{font-family:'Playfair Display',serif; font-size:2.2rem; font-weight:700; color:{GOLD};}}
.sub {{color:{MUTED}; margin-bottom:1.2rem;}}
.meta {{color:{MUTED}; font-size:.82rem; margin:.6rem 0 1rem;}}
.cap {{color:{MUTED}; font-size:.85rem; line-height:1.5; margin-bottom:.8rem;}}
h4 {{font-family:'Playfair Display',serif; color:{TEXT};}}
[data-testid="stPlotlyChart"], .tbl, .kpi {{background:{CARD}; border:1px solid {BORDER}; border-radius:12px;
  box-shadow:0 8px 28px rgba(0,0,0,.4);}}
[data-testid="stPlotlyChart"] {{padding:12px;}}
div[data-baseweb="select"] > div {{background:{ALT}!important; border-color:{BORDER}!important; border-radius:6px!important;}}
.pick {{font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; font-weight:600; margin-bottom:-.4rem;}}
.hero {{border-radius:12px; padding:18px 22px; margin-bottom:1.2rem; border:1px solid {BORDER}; border-left:4px solid var(--c);
  background:linear-gradient(90deg, rgba(212,175,55,.08), {CARD});}}
.hero b.h {{font-family:'Playfair Display',serif; font-size:1.25rem; color:{TEXT}; font-weight:600;}}
.hero div {{color:{BODY}; font-size:.9rem; margin-top:6px;}}
.kpi {{padding:16px 18px; height:100%; border-top:3px solid var(--c);}}
.kpi .t {{font-size:.7rem; letter-spacing:.1em; text-transform:uppercase; color:var(--c); font-weight:600;}}
.kpi .n {{color:{MUTED}; font-size:.78rem; min-height:2.3em; margin:2px 0 6px;}}
.kpi .big {{font-size:2rem; font-weight:700; color:{TEXT}; font-variant-numeric:tabular-nums;}}
.kpi .inv {{color:{MUTED}; font-size:.78rem; margin-bottom:10px;}}
.kpi .r {{display:flex; justify-content:space-between; border-top:1px solid {BORDER}; padding:7px 0; font-size:.84rem; color:{BODY};}}
.kpi .r b {{color:{TEXT}; font-variant-numeric:tabular-nums;}}
.tbl {{padding:6px; overflow-x:auto; margin-bottom:.6rem;}}
.tbl table {{width:100%; border-collapse:collapse;}}
.tbl th {{background:{ALT}; color:{GOLD}; text-transform:uppercase; letter-spacing:.06em; font-size:.72rem; padding:12px 16px; text-align:right; border-bottom:1px solid {BORDER};}}
.tbl td {{padding:10px 16px; text-align:right; color:{BODY}; font-size:.88rem; border-bottom:1px solid {BORDER}; font-variant-numeric:tabular-nums;}}
.tbl th:first-child, .tbl td:first-child {{text-align:left; color:{TEXT};}}
.tbl tr:last-child td {{border-bottom:none;}}
.tbl td.pos {{color:{POS}; font-weight:600;}} .tbl td.neg {{color:{NEG}; font-weight:600;}}
.tbl td.best {{color:{POS}; font-weight:700; background:rgba(62,207,142,.10);}}
.tbl th, .tbl td {{border-left:none!important; border-right:none!important; border-top:none!important;}}
.stTabs [data-baseweb="tab"] {{font-weight:600;}}
</style>""",
    unsafe_allow_html=True,
)

st.markdown('<div class="title">How SIFs protect on the way down</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">A Specialised Investment Fund compared with a mutual fund and the benchmark — '
            'from the day the SIF launched.</div>', unsafe_allow_html=True)

if DEMO:
    st.warning("DEMO MODE — all numbers below are synthetic and for layout preview only.")
if not (schemes.SIFS and schemes.MUTUAL_FUNDS and schemes.BENCHMARKS):
    st.info("Add your scheme codes to `schemes.py` (SIFS, MUTUAL_FUNDS, BENCHMARKS) and reload.")
    st.stop()

# ---- three dropdowns -------------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="pick" style="color:{COL["SIF"]}">SIF</div>', unsafe_allow_html=True)
    sif_name = st.selectbox("SIF", list(schemes.SIFS), label_visibility="collapsed")
with c2:
    st.markdown(f'<div class="pick" style="color:{COL["MF"]}">Mutual fund</div>', unsafe_allow_html=True)
    mf_name = st.selectbox("Mutual fund", list(schemes.MUTUAL_FUNDS), label_visibility="collapsed")
with c3:
    st.markdown(f'<div class="pick" style="color:{COL["BM"]}">Benchmark</div>', unsafe_allow_html=True)
    bm_name = st.selectbox("Benchmark", list(schemes.BENCHMARKS), label_visibility="collapsed")
NAMES = {"SIF": sif_name, "MF": mf_name, "BM": bm_name}

with st.sidebar:
    st.markdown("### Settings")
    n_worst = st.slider("Market's worst days to show", 3, 20, 10)
    thr = st.slider("Count a market fall when benchmark drops at least (%)", 1.0, 10.0, 3.0, 0.5) / 100
    amount = st.number_input("Illustrative investment (₹)", 10000, 100000000, 1000000, 100000)
    if st.button("Refresh data"):
        st.cache_data.clear()


@st.cache_data(ttl=3600, show_spinner=False)
def load(code: int) -> pd.Series:
    return api.get_nav(code)


try:
    with st.spinner("Fetching NAV history..."):
        raw = {k: load(code) for k, code in
               [("SIF", schemes.SIFS[sif_name]), ("MF", schemes.MUTUAL_FUNDS[mf_name]), ("BM", schemes.BENCHMARKS[bm_name])]}
except Exception as e:  # noqa: BLE001
    st.error(f"Couldn't load NAV data from finapi right now ({e}). Please try again shortly.")
    st.stop()

nav = an.align(raw["SIF"], raw["MF"], raw["BM"])
if len(nav) < 5:
    st.error("These three schemes don't have enough overlapping NAV history yet.")
    st.stop()

reb, dd = an.rebase(nav), an.drawdown(an.rebase(nav))
rets = nav.pct_change().dropna()
sc = an.scorecard(reb, rets, dd)
n_worst = min(n_worst, int((rets["BM"] < 0).sum()))
worst = an.worst_days(rets, n_worst)
ep = an.episode_table(nav, thr)
start, end = nav.index[0], nav.index[-1]
n_down = int((rets["BM"] < 0).sum())
if n_down == 0:
    st.info("The benchmark has had no down days since the SIF launched, so there is nothing to compare yet.")
    st.stop()

st.markdown(
    f'<div class="meta">Comparison window: <b>{start:%d %b %Y}</b> (SIF launch) → <b>{end:%d %b %Y}</b> · '
    f'{len(rets)} trading days · {n_down} days the market fell. All three are rebased to 100 on the SIF\'s launch date.</div>',
    unsafe_allow_html=True,
)
if len(rets) < 60:
    st.warning(f"The SIF has only {len(rets)} trading days of history — treat these results as early indications.")

if (rets.abs().max() > 0.10).any():
    bad = ", ".join(LBL[k] for k in an.KEYS if rets[k].abs().max() > 0.10)
    st.warning(f"Data check: a single-day move above 10% appears in: {bad}. Please verify those NAVs before sharing.")

# ---- headline --------------------------------------------------------------
cum = {k: an.compound(worst[k]) * 100 for k in an.KEYS}
fewer = int((worst["SIF"] > worst["BM"]).sum())
if cum["SIF"] > max(cum["MF"], cum["BM"]):
    colr, head = POS, "The SIF cushioned the fall better than both the mutual fund and the benchmark."
elif cum["SIF"] > cum["BM"]:
    colr, head = GOLD, "The SIF fell less than the benchmark, though the mutual fund held up better."
else:
    colr, head = AMBER, "On the market's worst days, the SIF did not fall less than the benchmark."
st.markdown(
    f'<div class="hero" style="--c:{colr}"><b class="h">{head}</b>'
    f'<div>On the market\'s {n_worst} worst days, the benchmark returned <b>{cum["BM"]:.1f}%</b>, the mutual fund '
    f'<b>{cum["MF"]:.1f}%</b> and the SIF <b>{cum["SIF"]:.1f}%</b> (those days\' returns compounded). The SIF fell less than the '
    f'benchmark on <b>{fewer} of those {n_worst}</b> days. Deepest fall from a peak: SIF <b>{sc.loc["mdd","SIF"]:.1f}%</b> · '
    f'mutual fund <b>{sc.loc["mdd","MF"]:.1f}%</b> · benchmark <b>{sc.loc["mdd","BM"]:.1f}%</b>.</div></div>',
    unsafe_allow_html=True,
)

# ---- KPI cards -------------------------------------------------------------
def card(k):
    s = sc[k]
    dc = "—" if np.isnan(s["dcap"]) else f'{s["dcap"]:.0f}%'
    return (f'<div class="kpi" style="--c:{COL[k]}"><div class="t">{LBL[k]}</div><div class="n">{NAMES[k]}</div>'
            f'<div class="big">{s["ret"]:+.1f}%</div><div class="inv">{an.inr(amount)} → {an.inr(amount * reb[k].iloc[-1] / 100)}</div>'
            f'<div class="r"><span>Maximum fall from peak</span><b>{s["mdd"]:.1f}%</b></div>'
            f'<div class="r"><span>Worst single day</span><b>{s["worst"]:.2f}%</b></div>'
            f'<div class="r"><span>Down-capture</span><b>{dc}</b></div></div>')


for col, k in zip(st.columns(3), an.KEYS):
    col.markdown(card(k), unsafe_allow_html=True)
st.write("")


# ---- chart helpers ---------------------------------------------------------
def style(fig, h=420, y=None, pct=False):
    fig.update_layout(height=h, plot_bgcolor=CARD, paper_bgcolor="rgba(0,0,0,0)", hovermode="x unified",
                      font=dict(color=BODY, family="Inter, sans-serif"), margin=dict(t=30, b=10, l=10, r=30),
                      legend=dict(orientation="h", y=1.1, x=1, xanchor="right"), yaxis_title=y, barmode="group", bargap=0.35)
    fig.update_xaxes(gridcolor=BORDER, zeroline=False)
    fig.update_yaxes(gridcolor=BORDER, zeroline=False, ticksuffix="%" if pct else "")
    return fig


def show(fig):
    st.plotly_chart(fig, width="stretch")


def table(headers, rows):
    h = "".join(f"<th>{x}</th>" for x in headers)
    b = "".join("<tr>" + "".join(f"<td{(' class=' + c) if c else ''}>{v}</td>" for v, c in r) + "</tr>" for r in rows)
    st.markdown(f'<div class="tbl"><table><tr>{h}</tr>{b}</table></div>', unsafe_allow_html=True)


def signed(v, dec=2):
    return (f"{v:+.{dec}f}%", "pos" if v > 0 else "neg" if v < 0 else "")


tab1, tab2, tab3, tab4 = st.tabs(["Since launch", "The market's worst days", "Market falls", "Scorecard"])

with tab1:
    st.markdown("#### Growth of 100 since the SIF launched")
    fig = go.Figure()
    for k in ["BM", "MF", "SIF"]:
        fig.add_trace(go.Scatter(x=reb.index, y=reb[k], name=LBL[k], mode="lines",
                                 line=dict(color=COL[k], width=3 if k == "SIF" else 2, dash="dash" if k == "BM" else "solid")))
    fig.add_trace(go.Scatter(x=worst.index, y=reb.loc[worst.index, "BM"], mode="markers", name="Market's worst days",
                             marker=dict(symbol="triangle-down", size=10, color=NEG), hoverinfo="skip"))
    show(style(fig, 460, "Indexed (launch = 100)"))
    st.markdown("#### How far each fell from its own peak")
    st.markdown('<div class="cap">Zero means at an all-time high. Shallower dips = better downside protection.</div>', unsafe_allow_html=True)
    fig = go.Figure()
    for k in ["BM", "MF", "SIF"]:
        fig.add_trace(go.Scatter(x=dd.index, y=dd[k] * 100, name=LBL[k], mode="lines", line=dict(color=COL[k], width=2),
                                 fill="tozeroy" if k == "SIF" else None, fillcolor="rgba(212,175,55,.15)"))
    show(style(fig, 360, pct=True))

with tab2:
    st.markdown(f"#### The {n_worst} worst days for the market — and what happened to each")
    st.markdown('<div class="cap">Days are picked by the benchmark\'s fall (worst first). A shorter bar means a smaller loss that day.</div>', unsafe_allow_html=True)
    lab = [f"{d:%d %b %y}" for d in worst.index]
    fig = go.Figure()
    for k in ["BM", "MF", "SIF"]:
        fig.add_trace(go.Bar(x=lab, y=worst[k] * 100, name=LBL[k], marker_color=COL[k]))
    fig.update_xaxes(type="category")
    show(style(fig, 400, pct=True))
    rows = [[(f"{d:%d %b %Y}", "")] + [signed(r[k] * 100) for k in ["BM", "MF", "SIF"]] +
            [("Yes", "pos") if r["SIF"] > r["BM"] else ("No", "neg")] for d, r in worst.iterrows()]
    rows.append([("Compounded", "")] + [signed(cum[k]) for k in ["BM", "MF", "SIF"]] + [(f"{fewer}/{n_worst}", "")])
    table(["Date", "Benchmark", "Mutual fund", "SIF", "SIF fell less than benchmark"], rows)

with tab3:
    st.markdown(f"#### Every time the benchmark fell {thr * 100:.1f}% or more from a peak")
    if ep.empty:
        st.info("The benchmark hasn't had a fall of that size since the SIF launched. Lower the threshold in the sidebar.")
    else:
        st.markdown('<div class="cap">Each bar group is one market decline, measured from the benchmark\'s peak to its trough '
                    'and applied to all three over the same dates.</div>', unsafe_allow_html=True)
        lab = [f"{p:%d %b} → {t:%d %b}" for p, t in zip(ep["Peak"], ep["Trough"])]
        fig = go.Figure()
        for k in ["BM", "MF", "SIF"]:
            fig.add_trace(go.Bar(x=lab, y=ep[k], name=LBL[k], marker_color=COL[k]))
        fig.update_xaxes(type="category")
        show(style(fig, 380, pct=True))
        rows = []
        for _, r in ep.iterrows():
            rows.append([(f"{r.Peak:%d %b %Y} → {r.Trough:%d %b %Y}", ""), (f"{int(r.Days)}", "")] +
                        [signed(r[k]) for k in ["BM", "MF", "SIF"]] + [signed(r.SIF - r.BM)])
        table(["Decline", "Trading days", "Benchmark", "Mutual fund", "SIF", "SIF vs benchmark (pp)"], rows)

with tab4:
    st.markdown("#### Downside scorecard")
    st.markdown('<div class="cap">Best value in each row is highlighted (up-capture is shown for context, not ranked). Capture ratios are measured against the benchmark: '
                'down-capture is the fund\'s average daily return on market-down days divided by the benchmark\'s; below 100% means it lost less; '
                'a negative figure means it gained on average when the market fell.</div>', unsafe_allow_html=True)
    spec = [("Return since SIF launch", "ret", "%", 1, 1), ("Maximum fall from peak", "mdd", "%", 1, 1),
            ("Currently below peak by", "cur", "%", 1, 1), ("Worst single day", "worst", "%", 2, 1),
            ("Average return on market-down days", "avgdown", "%", 2, 1), ("Down-capture", "dcap", "%", 0, -1),
            ("Up-capture", "ucap", "%", 0, 0), ("Down days fund fell less than market", "hit", "%", 0, 1),
            ("Volatility (annualised)", "vol", "%", 1, -1)]
    rows = []
    for name, key, unit, dec, sign in spec:
        vals = sc.loc[key, an.KEYS] * sign
        best = vals.idxmax() if sign and vals.notna().any() else None
        rows.append([(name, "")] + [("—", "") if np.isnan(sc.loc[key, k]) else
                                    (f"{sc.loc[key, k]:.{dec}f}{unit}", "best" if k == best else "")
                                    for k in an.KEYS])
    table(["Metric", "SIF", "Mutual fund", "Benchmark"], rows)

with st.expander("Methodology & important notes"):
    st.markdown(
        """
- **Launch-date alignment:** SIFs launched on different dates, so the comparison always starts on the selected SIF's first NAV date. The mutual fund and benchmark are rebased to 100 on that same day.
- **Common days only:** returns use dates on which all three schemes published a NAV, so every daily comparison is like-for-like.
- **Worst days:** the days with the largest daily fall in the benchmark since SIF launch; the SIF and mutual fund returns are shown for the same dates.
- **Market falls:** benchmark peak-to-trough declines of at least the chosen size; the SIF and mutual fund are measured between the same two dates.
- **Down/up-capture:** average daily fund return ÷ average daily benchmark return on the days the benchmark fell/rose.
- **Volatility:** standard deviation of daily returns × √252.
- **Worst-days figure:** the returns of those days multiplied together (the days are not consecutive).
- **Data:** daily NAVs from finapi.upvaly.com. Growth-option NAVs, so returns include reinvested income and are net of expenses.
- **Short history:** SIFs are new; a short track record can't show how a fund behaves across a full market cycle.
        """
    )
st.caption("Mutual fund investments and SIFs are subject to market risks. Past performance may or may not be sustained in the future. "
           "This is for information only and is not investment advice.")
