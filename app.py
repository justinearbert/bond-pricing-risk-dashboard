"""Run with: streamlit run app.py"""
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from bond_math import Bond, price, yield_to_maturity, risk_metrics, scenarios

st.set_page_config(page_title="Bond Pricing & Risk Dashboard", page_icon="📈", layout="wide")
st.title("Bond Pricing & Risk Dashboard")
st.caption("Educational fixed-coupon bond analytics | Pricing, YTM, Duration, Convexity & DV01")

with st.sidebar:
    st.header("Bond assumptions")
    face = st.number_input("Face value (€)", min_value=100.0, value=1000.0, step=100.0)
    coupon_pct = st.number_input("Annual coupon (%)", min_value=0.0, max_value=30.0, value=4.0, step=0.25)
    maturity = st.number_input("Maturity (years)", min_value=1, max_value=40, value=5, step=1)
    frequency = st.selectbox("Coupon payments per year", [1, 2, 4, 12], index=1)
    yield_pct = st.number_input("Annual yield to maturity (%)", min_value=-10.0, max_value=40.0, value=4.5, step=0.25)

bond = Bond(face=face, coupon_rate=coupon_pct / 100, maturity_years=float(maturity), payments_per_year=frequency)
yt = yield_pct / 100
metrics = risk_metrics(bond, yt)

st.subheader("1 · Bond valuation and interest-rate risk")
cols = st.columns(4)
cols[0].metric("Theoretical price", f"€{metrics['price']:,.2f}")
cols[1].metric("Modified duration", f"{metrics['modified_duration']:.2f} years")
cols[2].metric("Convexity", f"{metrics['convexity']:.2f}")
cols[3].metric("DV01 (per €1bp)", f"€{metrics['dv01']:.4f}")

with st.expander("Calculate YTM from an observed market price"):
    market_price = st.number_input("Observed bond price (€)", min_value=0.01, value=float(round(metrics['price'], 2)), step=1.0)
    st.write(f"**Implied YTM:** {100 * yield_to_maturity(bond, market_price):.4f}%")

st.subheader("2 · Rate-shock scenarios")
df = pd.DataFrame(scenarios(bond, yt))
st.dataframe(df.style.format({"New yield (%)": "{:.2f}", "Bond price": "€{:,.2f}", "P&L": "€{:+,.2f}", "Return (%)": "{:+.2f}%"}), use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(df["Rate shock (bp)"].astype(str), df["P&L"])
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_xlabel("Parallel change in yield (basis points)")
    ax.set_ylabel("Price change (€)")
    ax.set_title("Bond P&L under rate shocks")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
with right:
    grid_yields = np.linspace(max(-0.05, yt - 0.04), yt + 0.04, 150)
    prices = [price(bond, y) for y in grid_yields]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(grid_yields * 100, prices)
    ax.scatter([yield_pct], [metrics["price"]], zorder=3)
    ax.set_xlabel("Yield to maturity (%)")
    ax.set_ylabel("Price (€)")
    ax.set_title("Price–yield relationship")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.info("**Sales interpretation:** a higher required yield lowers this fixed-rate bond's price. "
        f"Near the base yield, a +1 bp move implies about €{metrics['dv01']:.4f} of price loss "
        "per bond of the selected face value (DV01).")
st.caption("Simplifying assumptions: deterministic cash flows; no credit/default, accrued interest, taxes, fees, callable features, or shifts in credit spreads; "
           "valuation on a coupon date; flat YTM used to discount all cash flows; parallel yield shocks; no live market data.")
