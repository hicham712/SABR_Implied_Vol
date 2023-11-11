from scipy.optimize import minimize
import numpy as np

def use_fitted_sabr_volatility(params,strike,forward_rate, maturity):
    # Function to calculate the sabr vols with the params we got in optimizing

    alpha, rho, nu = params
    beta=0.5
    lnFK = np.log(forward_rate / strike)
    z = (nu / alpha) * (forward_rate * strike) ** ((1 - beta) / 2) * lnFK

    x_z = np.log((np.sqrt(1 - 2 * rho * z + z ** 2) + z - rho) / (1 - rho))

    factor1 = alpha / ((forward_rate * strike) ** ((1 - beta) / 2) * (
            1 + ((1 - beta) ** 2 / 24) * lnFK ** 2 + ((1 - beta) ** 4 / 1920) * lnFK ** 4))
    factor2 = z / x_z
    factor3 = 1 + (((1 - beta) ** 2 * alpha ** 2) / (24 * (forward_rate * strike) ** (1 - beta) / 2)
                   + ((2 - 3 * rho ** 2) * nu ** 2) / 24) * maturity

    result = factor1 * factor2 * factor3

    return result
def sabr_objective(params, market_strikes, market_vols, forward_rate, maturity):
    # Objective function to minimize, derived from singular pertubation on SABR model
    alpha, rho, nu = params
    beta = 0.5

    def sabr_volatility(strike):
        lnFK = np.log(forward_rate / strike)
        z = (nu / alpha) * (forward_rate * strike) ** ((1 - beta) / 2) * lnFK

        x_z = np.log((np.sqrt(1 - 2 * rho * z + z ** 2) + z - rho) / (1 - rho))

        factor1 = alpha / ((forward_rate * strike) ** ((1 - beta) / 2) * (
                1 + ((1 - beta) ** 2 / 24) * lnFK ** 2 + ((1 - beta) ** 4 / 1920) * lnFK ** 4))
        factor2 = z / x_z
        factor3 = 1 + (((1 - beta) ** 2 * alpha ** 2) / (24 * (forward_rate * strike) ** (1 - beta) / 2)
                       + ((2 - 3 * rho ** 2) * nu ** 2) / 24) * maturity

        result = factor1 * factor2 * factor3

        return result

    model_vols = np.array([sabr_volatility(strike) for strike in market_strikes])
    objective = np.sum((model_vols - market_vols) ** 2)

    return objective


def calibrate_SABR(market_strikes, market_vols, stock_price,rf_rate, maturity):
    initial_params = [0.2, 0.2, 0.3]
    forward_rate=stock_price*np.exp(rf_rate*maturity)
    return minimize(sabr_objective, initial_params, method = 'Nelder-Mead', args=(market_strikes, market_vols, forward_rate, maturity))
