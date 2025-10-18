import pandas as pd
import os
from monte_carlo_template_10yr import run_strategy

strategies = [
    {"name": "Ivy League Allocation Strategy (10-Year)",
     "tickers": ['VTI', 'BND', 'VXUS', 'DBC', 'VNQ'],
     "weights": [0.35, 0.28, 0.15, 0.11, 0.11]},
    {"name": "Merriman Financial Buy & Hold (10-Year)",
     "tickers": ['VOO', 'VTV', 'VB', 'VNQ', 'VXUS', 'VTRIX', 'VSS', 'VIOV', 'VIOO', 'VWO', 'BSV'],
     "weights": [0.06]*10 + [0.40]},
    {"name": "Dave Ramsey 4-Fund Strategy (10-Year)",
     "tickers": ['NEIAX', 'JMGPX', 'REREX', 'FSGRX'],
     "weights": [0.25]*4},
    {"name": "Coffee House Strategy (10-Year)",
     "tickers": ['VFIAX', 'KO', 'VSMAX', 'VNQ', 'VTIAX', 'VBTLX'],
     "weights": [0.10]*5 + [0.40]}
]

all_summaries = []

for strat in strategies:
    # Run simulation, returns DataFrame with both Nominal and Inflation-Adjusted columns
    summary = run_strategy(strat["name"], strat["tickers"], strat["weights"])
    all_summaries.append(summary)

# Combine all summaries for Excel
summary_df = pd.concat(all_summaries, ignore_index=True)

# ------------------------------
# 1️⃣ Print to terminal in old format
# ------------------------------
pd.set_option('display.float_format', '${:,.2f}'.format)

for strat in strategies:
    name = strat["name"]
    df = [s for s in all_summaries if s['Strategy'][0] == name][0]  # get this strategy summary
    
    print(f"\n===== {name} =====\n")
    
    # Nominal values first
    print("=== 10-Year Monte Carlo Portfolio Simulation (Nominal) ===")
    for col in df.columns:
        if "Nominal" in col:
            print(f"{col.replace(' (Nominal)','')}: {df[col][0]:,.2f}")
    
    # Inflation-Adjusted values
    print("\n=== 10-Year Monte Carlo Portfolio Simulation (Inflation-Adjusted @ 2%) ===")
    for col in df.columns:
        if "InflationAdj" in col:
            print(f"{col.replace(' (InflationAdj)','')}: {df[col][0]:,.2f}")

# ------------------------------
# 2️⃣ Save full Excel unchanged
# ------------------------------
base_name = "all_portfolio_results"
i = 1
while os.path.exists(f"{base_name}_sim{i}.xlsx"):
    i += 1
excel_file = f"{base_name}_sim{i}.xlsx"

summary_df.to_excel(excel_file, sheet_name="Summary_Statistics", index=False)
print(f"\n✅ All summary statistics saved to {excel_file}")
