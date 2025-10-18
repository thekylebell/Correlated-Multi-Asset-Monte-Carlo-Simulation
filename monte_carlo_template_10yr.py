import yfinance as yf
import pandas as pd
import numpy as np

def run_strategy(strategy_name, tickers, weights, years=10, n_simulations=1000, inflation_rate=0.02):
    """
    Run a Monte Carlo simulation for a given portfolio strategy using real historical data.

    Returns:
        pd.DataFrame: Summary statistics with all metrics (Nominal + Inflation-Adjusted)
    """
    print(f"Running simulation for {strategy_name}...\n")

    # Fetch historical monthly data
    data = yf.download(tickers, period=f"{years}y", interval="1mo", auto_adjust=True)

    if isinstance(data, pd.Series):
        data = data.to_frame()

    if 'Adj Close' in data.columns:
        data = data['Adj Close']
    else:
        # If multi-index (Price, Ticker)
        if isinstance(data.columns, pd.MultiIndex):
            data = data['Close']

    monthly_returns = data.pct_change().dropna()
    mean_returns = monthly_returns.mean() * 12
    std_devs = monthly_returns.std() * np.sqrt(12)

    # Monte Carlo simulation
    final_values = []
    np.random.seed(42)
    for _ in range(n_simulations):
        portfolio_value = 1_000_000
        for year in range(years):
            annual_return = 0
            for ticker, weight in zip(tickers, weights):
                mu = mean_returns[ticker]
                sigma = std_devs[ticker]
                annual_return += weight * np.random.normal(mu, sigma)
            portfolio_value *= (1 + annual_return)
        final_values.append(portfolio_value)

    final_values_arr = np.array(final_values)

    # Nominal metrics
    mean_val = np.mean(final_values_arr)
    median_val = np.median(final_values_arr)
    std_val = np.std(final_values_arr)
    p10 = np.percentile(final_values_arr, 10)
    p25 = np.percentile(final_values_arr, 25)
    p75 = np.percentile(final_values_arr, 75)
    p90 = np.percentile(final_values_arr, 90)
    var95 = np.percentile(final_values_arr, 5)
    cvar95 = np.mean([v for v in final_values_arr if v <= var95])
    prob_loss = np.mean([v < 1_000_000 for v in final_values_arr]) * 100

    # Inflation-adjusted metrics
    final_values_infl = final_values_arr / ((1 + inflation_rate) ** years)
    mean_val_adj = np.mean(final_values_infl)
    median_val_adj = np.median(final_values_infl)
    std_val_adj = np.std(final_values_infl)
    p10_adj = np.percentile(final_values_infl, 10)
    p25_adj = np.percentile(final_values_infl, 25)
    p75_adj = np.percentile(final_values_infl, 75)
    p90_adj = np.percentile(final_values_infl, 90)
    var95_adj = np.percentile(final_values_infl, 5)
    cvar95_adj = np.mean([v for v in final_values_infl if v <= var95_adj])
    prob_loss_adj = np.mean([v < 1_000_000 for v in final_values_infl]) * 100

    # Summary DataFrame
    summary_df = pd.DataFrame({
        "Strategy": [strategy_name],
        # Nominal
        "Mean (Nominal)": [mean_val],
        "Median (Nominal)": [median_val],
        "StdDev (Nominal)": [std_val],
        "P10 (Nominal)": [p10],
        "P25 (Nominal)": [p25],
        "P75 (Nominal)": [p75],
        "P90 (Nominal)": [p90],
        "VaR95 (Nominal)": [var95],
        "CVaR95 (Nominal)": [cvar95],
        "P(Loss vs $1M) (Nominal %)": [prob_loss],
        # Inflation-adjusted
        "Mean (InflationAdj)": [mean_val_adj],
        "Median (InflationAdj)": [median_val_adj],
        "StdDev (InflationAdj)": [std_val_adj],
        "P10 (InflationAdj)": [p10_adj],
        "P25 (InflationAdj)": [p25_adj],
        "P75 (InflationAdj)": [p75_adj],
        "P90 (InflationAdj)": [p90_adj],
        "VaR95 (InflationAdj)": [var95_adj],
        "CVaR95 (InflationAdj)": [cvar95_adj],
        "P(Loss vs $1M) (InflationAdj %)": [prob_loss_adj]
    })

    return summary_df
