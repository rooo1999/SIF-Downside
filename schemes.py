"""Dropdown options. Format: {"Name shown in dropdown": scheme_code}.
SIFS are pre-filled (by ISIN). Add your MUTUAL_FUNDS and BENCHMARKS as finapi scheme codes (Growth option).
Benchmark = the scheme you want to treat as the market (e.g. a Nifty index fund / ETF)."""

SIFS = {  # copied from SIF Tracker's FUND_LIST + FUND_ISIN_MAP; scheme codes are looked up from the ISIN automatically
    "Altiva Equity Ex- Top 100 Long - Short Fund - Regular Plan - Growth": "INF754K30136",
    "Altiva Hybrid Long-Short Fund - Regular Plan - Growth": "INF754K30052",
    "Apex Hybrid Long-Short Fund - Regular - Growth": "INF209K30040",
    "Arthaya Equity Long Short Fund - Regular Plan - Growth Option": "INF582M30012",
    "Arudha Equity Long-Short Fund-Regular Plan-Growth": "INF194K30358",
    "Arudha Hybrid Long-Short Fund-Regular Plan-Growth": "INF194K30010",
    "Diviniti Equity Long Short Fund - Regular Plan Growth Option": "INF00XX30019",
    "DynaSIF Active Asset Allocator Long-Short Fund - Regular Plan - Growth Option": "INF579M30075",
    "DynaSIF Equity Ex-Top 100 Long - Short Fund - Regular Plan - Growth Option": "INF579M30133",
    "DynaSIF Equity Long - Short Fund - Regular Plan - Growth Option": "INF579M30018",
    "Sapphire Equity Long-Short SIF - Growth": "INF090I30014",
    "RedHex Hybrid Long-Short Fund - Regular - Growth": "INF336L30015",
    "Summit Equity Long-Short Fund - Regular Plan - Growth": "INF205K30014",
    "iSIF Active Asset Allocator Long-Short Fund - Growth": "INF109K30059",
    "iSIF Equity Ex-Top 100 Long-Short Fund - Growth": "INF109K30034",
    "iSIF Equity Long-Short Fund - Growth": "INF109K30075",
    "iSIF Hybrid Long-Short Fund - Growth": "INF109K30018",
    "Prism Hybrid Long-Short Fund - Regular Plan- Growth Option": "INF22M030019",
    "INFINITY HYBRID LONG-SHORT FUND-REGULAR - GROWTH": "INF174K30046",
    "Magnum Hybrid Long Short Fund - Regular Plan - Growth": "INF200K30015",
    "Platinum Hybrid Long-Short Fund - Regular Plan - Growth": "INF769K30019",
    "qsif Active Asset Allocator Long-Short Fund - Growth Option - Regular Plan": "INF966L30217",
    "qsif Equity Ex-Top 100 Long-Short Fund - Growth Option - Regular Plan": "INF966L30183",
    "qsif Equity Long Short Fund - Growth Option - Regular Plan": "INF966L30027",
    "qsif Hybrid Long-Short Fund - Growth Option - Regular Plan": "INF966L30084",
    "qsif Sector Rotation Long-Short Fund - Growth Option - RegularPlan": "INF966L30308",
    "WSIF Equity Ex-Top 100 Long-Short Fund - Regular Growth": "INF2F0030015",
    "WSIF Equity Long-Short Fund - Regular Growth": "INF2F0030072",
    "Titanium Equity Long-Short Fund Regular Growth": "INF277K30070",
    "Titanium Hybrid Long-Short Fund Regular Plan Growth": "INF277K30013",
}
MUTUAL_FUNDS = {
    "ICICI BAF": 104685,
    "HDFC BAF": 100119,
    "ICICI Con Hyb": 133051,
    "ICICI Agg Hyb": 100356,
    "PPFAS Flexi": 122640,
    "Invesco Flexi": 149766,
    "HDFC Flexi": 101762,
    "HDFC Mid": 105758,
    "Bandhan Small": 147944,
}
BENCHMARKS = {
    "NI N50": 113296,
    "MO N500": 147626,
    "NI Mid150": 148723,
    "NI SC250": 148518,
}
