import numpy as np
from numpy.linalg import det, solve
from scipy.linalg import cholesky
from statsmodels.stats.outliers_influence import OLSInfluence
import pandas as pd

# === Anytime-valid inference helper functions ===

def t_radius(g, n, number_of_coefficients, alpha):
    """
    Compute the radius of the t-ball confidence region for anytime-valid inference.

    Args:
        g (float): Prior strength hyperparameter controlling shrinkage.
        n (int): Sample size.
        number_of_coefficients (int): Number of regression coefficients (excluding intercept).
        alpha (float): Significance level (e.g., 0.05).

    Returns:
        float: Radius of the confidence ball.
    """
    nu = n - number_of_coefficients
    d = 1
    T = g / (g + n)
    powered_term = (T * alpha ** 2) ** (1 / (nu + d))
    numerator = nu * (1 - powered_term)
    denominator = max(0, powered_term - T)
    return np.sqrt(numerator / denominator)


def z_radius(g, n, alpha):
    """
    Compute the z-radius for anytime-valid inference in the one-dimensional known variance case.

    Args:
        g (float): Prior strength.
        n (int): Sample size.
        alpha (float): Significance level.

    Returns:
        float: Radius of the z-ball confidence interval.

    """
    return np.sqrt(((g + n) / n) * np.log((g + n) / (g * alpha ** 2)))


def log_G_t(t2, nu, n, g):
    """
    Calculate the log Bayes factor bound for a squared t-statistic under anytime-valid framework.

    Args:
        t2 (float): Squared t-statistic value.
        nu (int): Degrees of freedom.
        n (int): Sample size.
        g (float): Prior strength.

    Returns:
        float: Log Bayes factor.

    """
    r = g / (g + n)
    return 0.5 * np.log(r) + 0.5 * (nu + 1) * (np.log(1 + t2 / nu) - np.log(1 + r * t2 / nu))


def p_G_t(log_G_t_values):
    """
    Compute the anytime-valid p-value from the log Bayes factor for a t-test.

    Args:
        log_G_t_values (float or np.ndarray): Log Bayes factor values.

    Returns:
        float or np.ndarray: Anytime-valid p-values bounded by 1.
    """
    return np.minimum(1.0, np.exp(-log_G_t_values))


def log_G_f(f, d, nu, n, g):
    """
    Compute the log Bayes factor bound for an F-statistic under anytime-valid inference.

    Args:
        f (float): F-statistic.
        d (int): Numerator degrees of freedom.
        nu (int): Denominator degrees of freedom.
        n (int): Sample size.
        g (float): Prior strength.

    Returns:
        float: Log Bayes factor for the F-test.

    """
    r = g / (g + n)
    return 0.5 * d * np.log(r) + 0.5 * (nu + d) * (
        np.log(1 + (d / nu) * f) - np.log(1 + r * (d / nu) * f)
    )


def p_G_f(log_G_f_values):
    """
    Compute anytime-valid p-value from the log Bayes factor for an F-test.

    Args:
        log_G_f_values (float or np.ndarray): Log Bayes factor values for F-test.

    Returns:
        float or np.ndarray: Anytime-valid p-values bounded by 1.
    """
    return np.minimum(1.0, np.exp(-log_G_f_values))


def log_E_t(t2, nu, phi, z2):
    """
    Compute the log Bayes factor for a t-test using an empirical Bayes prior.

    Args:
        t2 (float): Squared t-statistic.
        nu (int): Degrees of freedom.
        phi (float): Prior precision parameter.
        z2 (float): Variance estimate related to the design.

    Returns:
        float: Log Bayes factor.

    """
    r = phi / (phi + z2)
    return 0.5 * np.log(r) + 0.5 * (nu + 1) * (np.log(1 + t2 / nu) - np.log(1 + r * t2 / nu))


def p_t(t2, nu, phi, z2):
    """
    Compute anytime-valid p-value from the empirical Bayes t-test log Bayes factor.

    Args:
        t2 (float): Squared t-statistic.
        nu (int): Degrees of freedom.
        phi (float): Prior precision.
        z2 (float): Variance estimate.

    Returns:
        float: Anytime-valid p-value.
    """
    return np.minimum(1, np.exp(-log_E_t(t2, nu, phi, z2)))


def log_E_f(delta, n, p, d, Phi, ZtZ, s2):
    """
    Compute the log Bayes factor for an F-test using an empirical Bayes prior on groups of coefficients.

    Args:
        delta (np.ndarray): Vector of coefficients tested.
        n (int): Sample size.
        p (int): Number of parameters in the null model (usually 1 for intercept).
        d (int): Number of coefficients tested.
        Phi (np.ndarray): Prior precision matrix.
        ZtZ (np.ndarray): Covariance matrix of tested covariates.
        s2 (float): Residual variance estimate.

    Returns:
        float: Log Bayes factor for group hypothesis.
    """
    if d > 1:
        norm_const = 0.5 * np.log(det(Phi)) - 0.5 * np.log(det(Phi + ZtZ))
        sol = solve(Phi + ZtZ, ZtZ)
        t1 = delta.T @ ZtZ @ delta
        t2 = delta.T @ (ZtZ - ZtZ @ sol) @ delta
    else:
        norm_const = 0.5 * np.log(Phi) - 0.5 * np.log(Phi + ZtZ)
        sol = ZtZ / (ZtZ + Phi)
        t1 = delta * ZtZ * delta
        t2 = delta * (ZtZ - ZtZ * sol) * delta

    scale = s2 * (n - p - d)
    return norm_const + 0.5 * (n - p) * (np.log(1 + t1 / scale) - np.log(1 + t2 / scale))


def p_F(lmfit, phi, s2):
    """
    Compute the anytime-valid p-value for an F-test using an empirical Bayes prior.

    Args:
        lmfit: Fitted linear regression model (e.g., statsmodels RegressionResults).
        phi (float): Prior precision parameter.
        s2 (float): Residual variance estimate.

    Returns:
        float: Anytime-valid p-value for the group F-test.
    """
    W = lmfit.model.exog  # Design matrix
    beta = lmfit.params

    n = W.shape[0]
    d = W.shape[1] - 1
    p = 1  # Null model dimension (intercept)

    Z = W[:, 1:(d + p + 1)]
    delta = beta[1:(d + p + 1)]

    ZtZ = Z.T @ Z
    Phi = np.eye(d) * phi

    logE = log_E_f(delta, n, p, d, Phi, ZtZ, s2)
    return min(1, np.exp(-logE))


# === Anytime Valid Linear Model (AVLM) class ===

class AVLM:
    """
    Anytime-valid linear regression inference wrapper for statsmodels OLS results.

    Enables anytime-valid p-values and confidence intervals for regression coefficients,
    incorporating optional robust covariance estimators (HC0-HC3).

    Args:
        model: Fitted OLS regression result object (statsmodels RegressionResultsWrapper).
        g (float): Prior strength parameter for anytime-valid inference (default=1).
        vcov_estimator (str or None): Type of robust covariance estimator to use.
            One of {"HC0", "HC1", "HC2", "HC3"} or None for standard errors.

    Methods:
        summary(): Returns a pandas DataFrame with coefficients, robust std errors,
                   anytime-valid t-statistics, and anytime-valid p-values.
        print_summary(): Prints a formatted anytime-valid summary to console.
        confint(level=0.95): Returns anytime-valid confidence intervals at given level.
    """

    def __init__(self, model, g=1, vcov_estimator=None):
        if vcov_estimator and vcov_estimator not in {"HC0", "HC1", "HC2", "HC3"}:
            raise ValueError("Invalid vcov_estimator. Must be one of: HC0, HC1, HC2, HC3")

        self.model = model
        self.g = g
        self.vcov_estimator = vcov_estimator

    def summary(self):
        X = self.model.model.exog
        y = self.model.model.endog
        n, k = X.shape
        residuals = self.model.resid
        beta_hat = self.model.params
        nu = self.model.df_resid

        if self.vcov_estimator is None:
            stderr = self.model.bse
            t_vals = self.model.tvalues
            t_sq = t_vals**2
            log_g_t = log_G_t(t_sq, nu, n, self.g)
            av_pvals = p_G_t(log_g_t)
        else:
            infl = OLSInfluence(self.model)
            h = infl.hat_matrix_diag
            e = residuals

            if self.vcov_estimator == "HC0":
                weights = e ** 2
            elif self.vcov_estimator == "HC1":
                weights = e ** 2 * n / (n - k)
            elif self.vcov_estimator == "HC2":
                weights = e ** 2 / (1 - h)
            elif self.vcov_estimator == "HC3":
                weights = e ** 2 / (1 - h)**2

            W = weights[:, np.newaxis]
            XV_hatX = X.T @ (X * W)
            XX = X.T @ X
            U = cholesky(np.linalg.inv(XV_hatX), lower=False)
            X_star = U @ XX
            precision_matrix = X_star.T @ X_star
            cov_matrix = np.linalg.inv(precision_matrix)

            stderr = np.sqrt(np.diag(cov_matrix))
            t_vals = beta_hat / stderr
            t_sq = t_vals ** 2
            log_g_t = log_G_t(t_sq, nu, n, self.g)
            av_pvals = p_G_t(log_g_t)

            if "const" in self.model.model.exog_names:
                idx = [i for i, name in enumerate(self.model.model.exog_names) if name != "const"]
            else:
                idx = list(range(k))

            bhat_sub = beta_hat[idx]
            precision_sub = precision_matrix[np.ix_(idx, idx)]
            fval = float(bhat_sub.T @ precision_sub @ bhat_sub)
        
        if self.vcov_estimator is None:
            fval = self.model.fvalue

        f_pval = p_G_f(log_G_f(fval, self.model.df_model, nu, n, self.g))

        summary_df = pd.DataFrame({
            'coef': beta_hat,
            'std err': stderr,
            't': t_vals,
            'p value': av_pvals
        })
        
        summary_df.attrs.update({
            'r2': self.model.rsquared,
            'adj_r2': self.model.rsquared_adj,
            'df_resid': nu,
            'fvalue': fval,
            'f_pvalue': f_pval,
            'g': self.g,
            'vcov_estimator': self.vcov_estimator
        })
        return summary_df

    def print_summary(self):
        summ = self.summary()
        print("Coefficients (anytime-valid):\n")
        print(summ.round(4))
        print("\nAnytime-Valid: TRUE")
        if summ.attrs['vcov_estimator']:
            print(f"Robust Standard Error Type: {summ.attrs['vcov_estimator']}")
        print(f"Multiple R-squared: {summ.attrs['r2']:.4f}, Adjusted R-squared: {summ.attrs['adj_r2']:.4f}")
        print(f"F-statistic: {summ.attrs['fvalue']:.4f}, p-value: {summ.attrs['f_pvalue']:.4e}")

    def confint(self, level=0.95):
        summ = self.summary()
        coefs = summ['coef']
        se = summ['std err']
        alpha = 1 - level
        t_rad = t_radius(self.g, self.model.nobs, len(coefs), alpha)
        lower = coefs - t_rad * se
        upper = coefs + t_rad * se
        ci_df = pd.DataFrame({
            f"{100*alpha/2:.1f}%": lower,
            f"{100*(1-alpha/2):.1f}%": upper
        })
        return ci_df