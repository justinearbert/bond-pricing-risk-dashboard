# Bond Pricing & Risk Dashboard

An interactive fixed-income analytics project designed for **Fixed Income Sales** discussions. It models the price and rate sensitivity of a standard fixed-coupon bond with reproducible Python calculations.

## Features

- Price a fixed-coupon bond using a constant yield to maturity (YTM).
- Solve for YTM from an observed price.
- Calculate Macaulay duration, modified duration, convexity, and DV01.
- Run parallel yield-shock scenarios (-200 to +200 basis points).
- Visualize the price–yield curve and scenario P&L in Streamlit.
- Unit tests for basic financial identities.

## Run locally (Mac / VS Code)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

If you use Anaconda, you can also select your Anaconda Python interpreter in VS Code, then install the dependencies into that environment.

## Finance example

A 5-year bond with €1,000 face value, 4% annual coupon and semiannual payments is discounted using a 4.5% nominal annual YTM. Try moving the yield from 4.5% to 5.5% to see the price impact. **DV01** indicates the *positive magnitude* of the approximate price loss if yield rises by 1 basis point for the specified face amount.

## Core formulas

Cash flows paid every `1/m` year (at exact coupon dates):

- Price: `P(y) = sum(CF_t / (1 + y/m)^(m*t))`.
- Macaulay duration: PV-weighted average time to cash flow.
- Modified duration: `D_mod = D_Mac / (1 + y/m)`.
- Convexity: `(1/P) * d²P/dy²`.
- DV01: approximately `-dP/dy * 0.0001`, estimated by a centered 1bp difference.

## Important limitations

This is an **educational tool, not investment advice or a live trading pricer**. It assumes fixed deterministic cash flows, no default, no accrued interest, no transaction costs, no early redemption, a flat discount rate (YTM), and valuation on a coupon date. Rate shocks are parallel moves in the bond's YTM, not a full term-structure or spread-risk simulation. For real bonds, day counts, settlement, clean/dirty price, credit spreads and market conventions matter.

## Repository structure

- `bond_math.py` — pricing and risk functions
- `app.py` — Streamlit dashboard
- `test_bond_math.py` — finance sanity checks
- `requirements.txt` — Python dependencies

## Suggested next steps

Integrate government yield curves, benchmark spread analysis, issuer comparisons, and a client-ready fixed-income factsheet.
