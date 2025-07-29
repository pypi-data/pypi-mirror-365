import numpy as np

class RiskMetrics:
    """
    A class to compute various risk metrics for a given set of returns.

    :param returns: A 1D NumPy array of asset returns.
    :type returns: np.ndarray
    :raises TypeError: If `returns` is not a NumPy array.
    :raises ValueError: If `returns` contains NaN or infinite values.
    """

    def __init__(self, returns: np.ndarray):
        if not isinstance(returns, np.ndarray):
            raise TypeError("ticker_returns must be a NumPy array.")
        if np.isnan(returns).any():
            raise ValueError("ticker_returns contains NaN values.")
        if np.isinf(returns).any():
            raise ValueError("ticker_returns contains infinite values.")
        self.returns = returns

    def value_at_risk(self, alpha: float) -> float:
        """
        Calculate the Value at Risk (VaR) at the given confidence level.

        :param alpha: Confidence level (e.g., 0.95 for 95%).
        :type alpha: float
        :return: Value at Risk.
        :rtype: float
        """
        self._check_param(alpha, 'alpha')
        return float(np.quantile(self.returns, 1 - alpha))

    def conditional_var(self, alpha: float) -> float:
        """
        Calculate the Conditional Value at Risk (CVaR) at the given confidence level.

        :param alpha: Confidence level (e.g., 0.95 for 95%).
        :type alpha: float
        :return: Conditional Value at Risk.
        :rtype: float
        """
        self._check_param(alpha, 'alpha')
        threshold = np.quantile(self.returns, 1 - alpha)
        cvar = -self.returns[self.returns <= threshold].mean()
        return float(cvar)

    def max_drawdown(self) -> float:
        """
        Calculate the maximum drawdown from cumulative returns.

        :return: Maximum drawdown.
        :rtype: float
        """
        cum_ret = np.cumsum(self.returns)
        peak = np.maximum.accumulate(cum_ret)
        drawdown = peak - cum_ret
        return float(np.max(drawdown))

    def expected_drawdown(self, threshold: float) -> float:
        """
        Compute expected drawdown beyond a specified threshold.

        :param threshold: Drawdown threshold.
        :type threshold: float
        :return: Expected drawdown over the threshold.
        :rtype: float
        """
        self._check_param(threshold, 'threshold')
        cum_ret = np.cumsum(self.returns)
        peak = np.maximum.accumulate(cum_ret)
        drawdown = peak - cum_ret
        edor = np.mean(np.maximum(drawdown - threshold, 0))
        return float(edor)

    def conditional_drawdown(self, alpha: float) -> float:
        """
        Compute conditional drawdown at a given confidence level.

        :param alpha: Confidence level.
        :type alpha: float
        :return: Conditional drawdown average over the largest alpha% drawdowns.
        :rtype: float
        """
        self._check_param(alpha, 'alpha')
        cum_ret = np.cumsum(self.returns)
        peak = np.maximum.accumulate(cum_ret)
        drawdown = peak - cum_ret
        k = int(alpha * len(drawdown))
        cdar = np.mean(np.sort(drawdown)[-k:]) if k > 0 else 0.0
        return float(cdar)

    def lower_partial_moment(self, threshold: float, order: int) -> float:
        """
        Calculate the Lower Partial Moment (LPM).

        :param threshold: Minimum acceptable return.
        :type threshold: float
        :param order: The order of the moment (e.g., 2 for semi-variance).
        :type order: int
        :return: Lower partial moment.
        :rtype: float
        """
        self._check_param(threshold, 'threshold')
        self._check_param(order, 'order')
        downside = np.maximum(threshold - self.returns, 0)
        return float(np.mean(downside ** order))

    def variance(self) -> float:
        """
        Calculate the variance of returns.

        :return: Variance.
        :rtype: float
        """
        return float(np.var(self.returns))

    def std_deviation(self) -> float:
        """
        Calculate the standard deviation of returns.

        :return: Standard deviation.
        :rtype: float
        """
        return float(np.std(self.returns))

    def skewness(self) -> float:
        """
        Compute the skewness of returns.

        :return: Skewness value.
        :rtype: float
        """
        mean = np.mean(self.returns)
        std = np.std(self.returns)
        return float(np.mean(((self.returns - mean) / std) ** 3))

    def kurtosis(self) -> float:
        """
        Compute the kurtosis of returns.

        :return: Kurtosis value.
        :rtype: float
        """
        mean = np.mean(self.returns)
        std = np.std(self.returns)
        return float(np.mean(((self.returns - mean) / std) ** 4))

    def volatility(self) -> float:
        """
        Calculate annualized volatility assuming 252 trading days.

        :return: Annualized volatility.
        :rtype: float
        """
        return float(np.std(self.returns) * np.sqrt(252))

    def _check_param(self, value, name):
        """
        Internal method to validate parameters.

        :param value: The parameter value to check.
        :param name: Name of the parameter.
        :raises ValueError: If the value is None.
        """
        if value is None:
            raise ValueError(f"{name} is required for this risk measure.")
