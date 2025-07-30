import numpy as np
import pandas as pd
from scipy import stats
from scipy.linalg import qr
from scipy.optimize import minimize_scalar


def projection_matrix(X):
    """Compute the projection matrix P = X (X'X)^(-1) X'."""
    Q, _ = qr(X, mode='economic')
    return Q @ Q.T


def MPxM(M, X):
    """Compute M' P_X M where P_X is the projection matrix onto the column space of X."""
    Q, _ = qr(X, mode='economic')
    QtM = Q.T @ M
    return QtM.T @ QtM


def MP1M(M):
    """Compute M' P_1 M where P_1 is the projection matrix onto the space spanned by 1_n (grand mean)."""
    M = np.atleast_2d(M)
    n = M.shape[0]
    Mbar = np.sum(M, axis=0, keepdims=True)
    return (Mbar.T @ Mbar) / n


def t_radius(g, n, number_of_coefficients, alpha):
    """Helper function to compute radius for optimizing g."""
    nu = n - number_of_coefficients
    factor = (1 + g) / (g * nu)
    quantile = stats.t.ppf(1 - alpha / 2, df=nu)
    return np.sqrt(factor) * quantile


def optimal_g(n, number_of_coefficients, alpha):
    """Find the optimal precision parameter g to minimize the radius.

    Parameters
    ----------
    n : int
        Total sample size.
    number_of_coefficients : int
        Number of predictors in the model.
    alpha : float
        Significance level.

    Returns
    -------
    float
        Optimal g value.
    """
    if n <= 0:
        raise ValueError("n must be positive.")
    if n <= number_of_coefficients:
        raise ValueError("n must be greater than number_of_coefficients.")
    if not (0 < alpha < 1):
        raise ValueError("alpha must be in (0,1).")

    nu = n - number_of_coefficients
    upper_bound = n * (alpha ** (2 / nu)) / (1 - alpha ** (2 / nu))
    lower_bound = 1

    result = minimize_scalar(
        t_radius,
        bounds=(lower_bound, upper_bound),
        args=(n, number_of_coefficients, alpha),
        method='bounded'
    )

    return result.x


def log_G_f(f, d1, d2, n, g):
    """Log anytime-valid p-value numerator.

    Parameters
    ----------
    f : float
        F-statistic.
    d1 : int
        Numerator degrees of freedom.
    d2 : int
        Denominator degrees of freedom.
    n : int
        Sample size.
    g : float
        Precision parameter.

    Returns
    -------
    float
        Log-transformed G function value.
    """
    term1 = -d1 / 2 * np.log(1 + g * f / d1)
    term2 = -d2 / 2 * np.log(1 - g / (n + g))
    return term1 + term2


def p_G_f(log_gf):
    """Transform log G(f) value into a valid p-value.

    Parameters
    ----------
    log_gf : float
        Log G(f) value.

    Returns
    -------
    float
        Anytime-valid p-value.
    """
    return min(1.0, np.exp(log_gf))


class AVAOV:
    """
    Anytime-Valid ANOVA wrapper class .

    This class wraps a fitted OLS model and transforms standard F-test p-values
    into anytime-valid p-values using the technique described in:

    Parameters
    ----------
    ols_result : statsmodels.regression.linear_model.RegressionResultsWrapper
        A fitted OLS model from statsmodels.
    g : float
        Precision parameter for the anytime-valid test (default: 1).
    """

    def __init__(self, ols_result, g=1):
        self.model = ols_result
        self.g = g
        self.nobs = int(ols_result.nobs)
        self.df_resid = int(ols_result.df_resid)
        self.df_model = int(ols_result.df_model)
        self.anova_table = None

    def summary(self):
        """
        Generate ANOVA table with anytime-valid p-values.

        Returns
        -------
        pandas.DataFrame
            ANOVA table where standard p-values are replaced by anytime-valid p-values.
        """
        from statsmodels.stats.anova import anova_lm
        table = anova_lm(self.model, typ=2)
        table = table.reset_index()

        d1s = table['df'].values
        d2 = self.df_resid
        Fs = table['F'].values

        av_pvalues = []
        for i in range(len(Fs)):
            f = Fs[i]
            if np.isnan(f):
                av_pvalues.append(np.nan)
                continue
            log_gf = log_G_f(f, d1s[i], d2, self.nobs, self.g)
            av_pvalues.append(p_G_f(log_gf))

        table['p_value'] = av_pvalues
        self.anova_table = table
        return table

    def print_summary(self):
        """
        Print the summary table with anytime-valid p-values.
        """
        if self.anova_table is None:
            _ = self.summary()

        print(self.anova_table.drop(columns=["PR(>F)"]) if "PR(>F)" in self.anova_table.columns else self.anova_table)
        print("\nAnytime-Valid: TRUE (p-values adjusted)")