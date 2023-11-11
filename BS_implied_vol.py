import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize_scalar

def bs_price(S, K, T, r, vol, opt_type):
    # Option price in B&S

    d1 = (np.log(S / K) + (r + 0.5 * vol ** 2) * T) / (vol * np.sqrt(T))
    d2 = d1 - vol * np.sqrt(T)
    if opt_type == 'c':
        price = S * norm.cdf(d1) - np.exp(-r * T) * K * norm.cdf(d2)
    else:
        price = norm.cdf(-d2) * K * np.exp(-r * T) - S * norm.cdf(-d1)

    return price


def bs_vega(S, K, T, r, sigma):
    # Vega of B&S
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    return S * norm.pdf(d1) * np.sqrt(T)


def find_vol(target_value, S, K, T, r, opt_type):

    # Simple Newton-Raphson implementation for getting IVs, uses multiple starting points

    MAX_ITERATIONS = 500
    PRECISION = 1.0e-5
    sigma = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 2, 5, 10]

    for j in range(0, len(sigma)):
        for i in range(0, MAX_ITERATIONS):
            price = bs_price(S, K, T, r, sigma[j], opt_type)
            vega = bs_vega(S, K, T, r, sigma[j])
            diff = target_value - price  # our root
            if abs(diff) < PRECISION:
                true_val = j
                return sigma[true_val]

            true_val = j
            sigma[j] = sigma[j] + diff / vega

    return sigma[true_val]


def implied_vol(opt_value, S, K, T, r, opt_type):
    # Method of getting implied vol using scipy

    def call_obj(sigma):
        return abs(bs_price(S, K, T, r, sigma, opt_type) - opt_value)

    res = minimize_scalar(call_obj, bounds=(0.0001, 10), method='bounded')
    return res.x