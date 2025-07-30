import numpy as np
from scipy.linalg import qr
from scipy.optimize import minimize_scalar

# === Projection Matrix ===
def projection_matrix(X):
    """
    Compute the orthogonal projection matrix onto the column space of X.

    Given a matrix X (n x p), this function returns the projection matrix P = Q Q^T,
    where Q is an orthonormal basis for the column space of X obtained via QR decomposition.

    Args:
        X (np.ndarray): An (n x p) design matrix.

    Returns:
        np.ndarray: The (n x n) projection matrix onto span(X).

    Note:
        This matrix satisfies P = P^2 = P^T, projecting vectors onto the space spanned by X.
    """
    Q, _ = qr(X, mode='economic')
    return Q @ Q.T


# === M' P M ===
def MPxM(M, X):
    """
    Compute the quadratic form M' P M, where P is the projection matrix onto span(X).

    Args:
        M (np.ndarray): An (n x k) matrix (or vector) representing coefficients or features.
        X (np.ndarray): An (n x p) design matrix.

    Returns:
        np.ndarray: The matrix M' P M (k x k), measuring how M aligns with span(X).

    Explanation:
        This function first projects M onto span(X) by P = Q Q^T (Q from X),
        then computes the inner product of the projected M with itself.
    """
    Q, _ = qr(X, mode='economic')
    QtM = Q.T @ M
    return QtM.T @ QtM


# === M' P 1 M ===
def MP1M(M):
    """
    Compute the scalar quantity M' P_1 M, where P_1 is the projection matrix onto the
    space spanned by the all-ones vector (mean projection).

    Args:
        M (np.ndarray): An (n x k) matrix or vector.

    Returns:
        np.ndarray: A (k x k) matrix representing the quadratic form with P_1.

    Explanation:
        P_1 = (1/n) 11^T projects onto the mean vector.
        This function computes (M' P_1 M) = (mean(M))' (mean(M)) * n.

    Notes:
        Useful in statistical adjustments related to intercept or centering.
    """
    M = np.atleast_2d(M)
    n = M.shape[0]
    Mbar = np.sum(M, axis=0, keepdims=True)
    return (Mbar.T @ Mbar) / n


# === Radius Function for Confidence Ball ===
def t_radius(g, n, number_of_coefficients, alpha):
    """
    Compute the radius of a t-ball (confidence region) used for anytime-valid inference.

    This radius corresponds to a (1 - alpha) confidence region radius adjusted by
    the prior strength g, sample size n, and number of regression coefficients.

    Args:
        g (float): Prior strength parameter controlling shrinkage.
        n (int): Sample size.
        number_of_coefficients (int): Number of regression coefficients (excluding intercept).
        alpha (float): Significance level (e.g., 0.05).

    Returns:
        float: Radius of the confidence ball.
    """
    nu = n - number_of_coefficients
    factor = (1 + g) / (g * nu)
    from scipy.stats import t
    quantile = t.ppf(1 - alpha / 2, df=nu)
    return np.sqrt(factor) * quantile


# === Optimal g Selection Function ===
def optimal_g(n, number_of_coefficients, alpha):
    """
    Compute an approximately optimal prior strength g that minimizes the t-radius.

    This optimization balances the tradeoff between prior influence and sample size,
    aiming to produce the tightest confidence ball radius for anytime-valid inference.

    Args:
        n (int): Sample size.
        number_of_coefficients (int): Number of regression coefficients (excluding intercept).
        alpha (float): Significance level (e.g., 0.05).

    Returns:
        float: The optimal value of g.

    Raises:
        ValueError: If input parameters are invalid (e.g., n <= 0, or n <= number_of_coefficients,
                    or alpha not in (0,1)).

    Procedure:
        Minimizes the t_radius function over g in [1, upper_bound], where
        upper_bound = n * (alpha^(2/nu)) / (1 - alpha^(2/nu)) with nu = n - number_of_coefficients.
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