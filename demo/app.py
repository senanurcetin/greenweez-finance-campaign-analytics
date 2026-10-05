"""Streamlit demo on top of the dbt marts (DuckDB).

Run `make demo` (builds the dbt project into target/demo.duckdb first), or:
    streamlit run demo/app.py
Set DEMO_DB to read a different DuckDB file.
"""
import os
from pathlib import Path

import altair as alt
import duckdb
import pandas as pd
import streamlit as st

DB_PATH = Path(os.environ.get("DEMO_DB", Path(__file__).resolve().parent.parent / "target" / "demo.duckdb"))

# Categorical slots 1-4 of the reference palette, assigned in fixed order.
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
SOURCE_COLORS = {"adwords": BLUE, "bing": ORANGE, "criteo": AQUA, "facebook": YELLOW}

st.set_page_config(page_title="Greenweez finance & campaigns", layout="wide")


@st.cache_data(show_spinner=False)
def load(sql: str, db_mtime: float) -> pd.DataFrame:
    # db_mtime is part of the cache key so a fresh `dbt build` invalidates the cache.
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        return con.sql(sql).df()
    finally:
        con.close()


def query(sql: str) -> pd.DataFrame:
    return load(sql, DB_PATH.stat().st_mtime)


if not DB_PATH.exists():
    st.error(f"{DB_PATH} not found. Run `make build` first (dbt seed + build on the demo target).")
    st.stop()

daily = query("select * from analytics_finance.finance_campaigns_day order by date")
monthly = query("select * from analytics_finance.finance_campaigns_month order by datemonth")
spend = query(
    """
    select date_trunc('month', date_date)::date as datemonth, paid_source, sum(ads_cost) as ads_cost
    from analytics.int_campaigns group by 1, 2 order by 1, 2
    """
)
daily["date"] = pd.to_datetime(daily["date"])

st.title("Greenweez: finance and campaign profitability")
st.caption(
    "Synthetic demo data served by the dbt marts `finance_campaigns_day` and `finance_campaigns_month`. "
    "Reporting logic, not marketing attribution."
)

lo, hi = daily["date"].min().date(), daily["date"].max().date()
start, end = st.date_input("Date range", value=(lo, hi), min_value=lo, max_value=hi)
view = daily[(daily["date"].dt.date >= start) & (daily["date"].dt.date <= end)]

orders = int(view["transactions"].sum())
revenue = view["revenue"].sum()
op_margin = view["operational_margin"].sum()
ads_cost = view["ads_cost"].sum()
ads_margin = view["ads_margin"].sum()
cols = st.columns(5)
cols[0].metric("Revenue", f"{revenue:,.0f}")
cols[1].metric("Operational margin", f"{op_margin:,.0f}")
cols[2].metric("Ad spend", f"{ads_cost:,.0f}")
cols[3].metric("Margin after ads", f"{ads_margin:,.0f}")
cols[4].metric("Average basket", f"{revenue / orders:,.2f}" if orders else "n/a")


def line(df: pd.DataFrame, y: str, title: str, color: str, zero_rule: bool = False) -> alt.Chart:
    base = alt.Chart(df, title=title).encode(
        x=alt.X("date:T", title=None, axis=alt.Axis(format="%b %d", tickCount=6)),
        y=alt.Y(f"{y}:Q", title=None),
        tooltip=[alt.Tooltip("date:T", title="Date"), alt.Tooltip(f"{y}:Q", format=",.2f", title=title)],
    )
    chart = base.mark_line(color=color, strokeWidth=2)
    if zero_rule:
        chart = chart + alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="#8a8a86", strokeDash=[3, 3]).encode(y="y:Q")
    return chart.resolve_scale(x="shared").properties(height=220)


# One measure per chart: revenue and ad spend have different scales, so no dual axis.
left, right = st.columns(2)
left.altair_chart(line(view, "revenue", "Daily revenue", BLUE), use_container_width=True)
right.altair_chart(line(view, "ads_cost", "Daily ad spend", ORANGE), use_container_width=True)
st.altair_chart(
    line(view, "ads_margin", "Daily margin after ads (negative on days with spend but no orders)", AQUA, True),
    use_container_width=True,
)

st.subheader("Monthly margin waterfall")
month = st.selectbox("Month", monthly["datemonth"].tolist(), index=len(monthly) - 1, format_func=lambda d: f"{d:%B %Y}")
m = monthly[monthly["datemonth"] == month].iloc[0]
steps = [
    ("Revenue", m["revenue"], "Total"),
    ("Purchase cost", -m["purchase_cost"], "Cost"),
    ("Shipping fees", m["shipping_fee"], "Income"),
    ("Logistics cost", -m["log_cost"], "Cost"),
    ("Shipping cost", -m["ship_cost"], "Cost"),
    ("Ad spend", -m["ads_cost"], "Cost"),
    ("Margin after ads", m["ads_margin"], "Total"),
]
rows, running = [], 0.0
for label, value, kind in steps:
    if kind == "Total":
        rows.append({"step": label, "start": 0.0, "end": float(value), "kind": kind})
        running = float(value)
    else:
        rows.append({"step": label, "start": running, "end": running + float(value), "kind": kind})
        running += float(value)
wf = pd.DataFrame(rows)
wf["delta"] = wf["end"] - wf["start"]
wf["top"] = wf[["start", "end"]].max(axis=1)
order = [s[0] for s in steps]
kind_scale = alt.Scale(domain=["Total", "Cost", "Income"], range=[BLUE, ORANGE, AQUA])
bars = (
    alt.Chart(wf)
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=36)
    .encode(
        x=alt.X("step:N", sort=order, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("start:Q", title=None),
        y2="end:Q",
        color=alt.Color("kind:N", scale=kind_scale, legend=alt.Legend(title=None, orient="top")),
        tooltip=[alt.Tooltip("step:N"), alt.Tooltip("delta:Q", format=",.0f", title="Change")],
    )
)
labels = (
    alt.Chart(wf)
    .mark_text(dy=-6, fontSize=11)
    .encode(x=alt.X("step:N", sort=order), y="top:Q", text=alt.Text("delta:Q", format=",.0f"))
)
st.altair_chart((bars + labels).properties(height=320), use_container_width=True)

st.subheader("Ad spend by source")
spend["datemonth"] = pd.to_datetime(spend["datemonth"])
spend_chart = (
    alt.Chart(spend)
    .mark_bar(stroke="white", strokeWidth=2)
    .encode(
        x=alt.X("yearmonth(datemonth):O", title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("ads_cost:Q", title=None),
        color=alt.Color(
            "paid_source:N",
            scale=alt.Scale(domain=list(SOURCE_COLORS), range=list(SOURCE_COLORS.values())),
            legend=alt.Legend(title=None, orient="top"),
        ),
        tooltip=[
            alt.Tooltip("yearmonth(datemonth):O", title="Month"),
            alt.Tooltip("paid_source:N", title="Source"),
            alt.Tooltip("ads_cost:Q", format=",.0f", title="Spend"),
        ],
    )
    .properties(height=260)
)
st.altair_chart(spend_chart, use_container_width=True)

with st.expander("Table view: finance_campaigns_month"):
    st.dataframe(monthly, use_container_width=True, hide_index=True)
