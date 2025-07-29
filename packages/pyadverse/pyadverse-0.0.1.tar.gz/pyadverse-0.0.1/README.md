# RiskMetrics 📊

pyadverse is a Python library for calculating various financial risk metrics from return data.

## 📦 Installation

Install the package from PyPI:

```bash
pip install pyadverse
```


## 💡 Example Usage

```python
import numpy as np
from pyadverse import RiskMetrics

returns = np.array([0.01, -0.02, 0.03, -0.01])
risk = RiskMetrics(returns)

print("VaR (95%):", risk.value_at_risk(0.95))
print("CVaR (95%):", risk.conditional_var(0.95))
print("Max Drawdown:", risk.max_drawdown())
print("Volatility:", risk.volatility())
```

## 📘 Risk Metrics Descriptions

- **Value at Risk (VaR):**
  Estimates the maximum potential loss at a given confidence level (e.g., 95%).

- **Conditional Value at Risk (CVaR):**
  Measures the expected loss given that the loss is beyond the VaR threshold.

- **Max Drawdown:**
  The maximum observed loss from a peak to a trough before a new peak is attained.

- **Expected Drawdown:**
  The average drawdown that exceeds a user-defined threshold.

- **Conditional Drawdown (CDaR):**
  The average of the worst-case drawdowns, defined by a confidence percentile.

- **Lower Partial Moment (LPM):**
  Measures downside risk. The higher the order, the more sensitive to extreme losses.

- **Variance:**
  The average squared deviation from the mean return; basic risk indicator.

- **Standard Deviation:**
  Square root of the variance; common measure of return volatility.

- **Skewness:**
  Measures asymmetry of the return distribution. Negative skew indicates more left tail risk.

- **Kurtosis:**
  Measures "tailedness" of the return distribution. Higher values mean more outlier-prone.

- **Volatility:**
  Annualized standard deviation of returns (assuming 252 trading days).