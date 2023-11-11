from typing import List
import numpy as np
import matplotlib.pyplot as plt
import my_yoptions as yo
from datetime import datetime
import yfinance as yf
import pandas as pd
import SABR_functions as sabr_f
import BS_implied_vol as bs_vol

def get_chains(tick):
    # using yoptions to get option chains

    chain_c = yo.get_plain_chain(stock_ticker=tick, option_type='c')
    chain_p = yo.get_plain_chain(stock_ticker=tick, option_type='p')
    chain_c["Opt_Type"] = 'c'
    chain_p["Opt_Type"] = 'p'

    return chain_c, chain_p


def get_best_chain(chain_c, chain_p):
    # Optimizes the option chains gotten from yahoo finance, keeping the contracts with the most volume for each strike

    df_concat = pd.concat([chain_c, chain_p])
    df_concat["Volume"] = df_concat["Volume"].replace('-', 0)
    chain_cp = df_concat.sort_values("Volume", ascending=False).drop_duplicates(subset=["Strike"], keep="first") # keep only calls or puts based on volume
    chain_cp=chain_cp[chain_cp["Volume"]>100] # Only use options where the volume is at least significant
    chain_cp["Last Price"] = (chain_cp["Ask"] + chain_cp["Bid"]) / 2
    chain_cp = chain_cp[chain_cp.Bid != 0]
    chain_cp = chain_cp[chain_cp.Ask != 0]
    chain_cp = chain_cp.reset_index()
    return chain_cp

def nan_helper(y):
    # replace nan by any function (we will use linear interpolation between vols)
    return np.isnan(y), lambda z: z.nonzero()[0]
def convert_date(input_date):
    # Conversion of dates

    input_datetime = datetime.strptime(input_date, "%a %b %d %Y")
    return input_datetime.strftime("%Y-%m-%d")


def get_chain_from_csv(path_, exp_date):
    # Read a CSV file from CBOE option data, works for any option

    chain = pd.read_csv(path_, skiprows=3)
    chain_c = chain[["Expiration Date", "Bid", "Ask", "Volume", "IV", "Strike"]]
    chain_c["Opt_Type"] = "c"
    chain_p = chain[["Expiration Date", "Bid.1", "Ask.1", "Volume.1", "IV.1", "Strike"]]
    chain_p = chain_p.rename(columns={"Bid.1": "Bid", "Ask.1": "Ask", "Volume.1": "Volume", "IV.1": "IV"})
    chain_p["Opt_Type"] = "p"
    chain_p["Expiration Date"] = chain_p["Expiration Date"].apply(convert_date)
    chain_c["Expiration Date"] = chain_c["Expiration Date"].apply(convert_date)
    chain_c = chain_c.loc[chain_c["Expiration Date"] == exp_date]
    chain_p = chain_p.loc[chain_p["Expiration Date"] == exp_date]
    return chain_c, chain_p


def get_ivs(chain, price, T, rf_rate):
    # Function to get IVs using Newton Raphson method
    ivs = {}

    for row in chain.index:
        iv = bs_vol.find_vol(chain["Last Price"][row], price, chain.Strike[row], T, rf_rate, chain["Opt_Type"][row])
        """
        Other method to get IV using scipy
        # iv=implied_vol(chain["Last Price"][row], price, chain.Strike[row], T, rf_rate, chain["Opt_Type"][row])
        """
        ivs[chain.Strike[row]] = iv

    return ivs


def convert_dict_toarray(ivs_c):
    lists1 = sorted(ivs_c.items())
    market_strikes, market_vols = zip(*lists1)
    market_vols = np.array(market_vols)
    market_strikes = np.array(market_strikes)
    return market_strikes,market_vols

def plot_smile_vs_SABR(market_strikes,market_vols,SABR_vols,stock,expiry_opt,tick):
    f = plt.figure(1)
    """
    -----If CSV from CBOE is used-----
    # lists = sorted(ivs_csv.items())
    # x, y = zip(*lists)
    # plt.scatter(x, y)
    """
    plt.scatter(market_strikes, market_vols, label='Market volatilities')
    plt.title(
        'Implied vol smile/skew for options on ' + tick + ' expiring on ' + expiry_opt.date().isoformat())
    plt.axvline(x=stock,linestyle='dotted',color='r',label='ATM point')
    plt.scatter(market_strikes, SABR_vols, label='SABR volatilities')
    plt.legend()
    f.show()


def get_vol_smile(tick,rf,date_format,expiry_opt):

    # Get stock and rfr value
    stock = yf.Ticker(tick).history()['Close'].iloc[-1]
    rf_indx = (100-yf.Ticker(rf).history()['Close'].iloc[-1])/ (365)

    # Get option chains from Yahoo
    chain_c, chain_p = get_chains(tick)
    chain_cp = get_best_chain(chain_c, chain_p)

    # from CSV from CBOE
    """
    -----If CSV from CBOE is used-----
    chain_cdata_csv,chain_p_data_csv=get_chain_from_csv(r"tsla_quotedata.csv",expiry_opt.date().isoformat())
    chain_cp_csv=get_best_chain(chain_cdata_csv, chain_p_data_csv)
    """

    # Get time until expiry
    now_date = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), date_format)
    T = expiry_opt - now_date
    T = T.days / 255

    # Get IVs
    ivs_c = get_ivs(chain_cp, stock, T, rf_indx)

    """
    -----If CSV from CBOE is used-----
    # ivs_csv=get_ivs(chain_cp_csv, stock, T, rf_indx)
    """

    # Get every strikes and every vols in two ndarray

    market_strikes, market_vols = convert_dict_toarray(ivs_c)

    # linear interpolation for missing IV values
    nans, x= nan_helper(market_vols)
    market_vols[nans]= np.interp(x(nans), x(~nans), market_vols[~nans])

    # Calibrating the SABR model and comparing it to the actual market vols

    result=sabr_f.calibrate_SABR(market_strikes,market_vols,stock,rf_indx,T)
    print("Results from SABR calibration are [alpha,rho,nu]= "+ str(result.x))
    sabr_vols=[sabr_f.use_fitted_sabr_volatility(result.x,K,stock*np.exp(rf_indx*T),T) for K in market_strikes]
    K_test=stock * 1.2
    opt_price_test=round(bs_vol.bs_price(stock, K_test, T, rf_indx,sabr_f.use_fitted_sabr_volatility(result.x, K_test, stock * np.exp(rf_indx * T), T), 'p'), 2)
    print("The option price of the put option of strike 120% (K=" + str(K_test) + ") is according to SABR: " + str(opt_price_test))
    # Plotting the smile
    plot_smile_vs_SABR(market_strikes,market_vols,sabr_vols,stock,expiry_opt,tick)


""" ---------Parameters to modify---------"""

tick = 'TSLA'
rf = 'SR3=F'
date_format = "%Y-%m-%d"
expiry_opt = datetime.strptime(yo.get_expiration_dates(stock_ticker=tick)[1], date_format) # Change the [1] to [0] for nearest expiry of option, or [-1] for furthest

"""---------End of parameters to modify---------"""

get_vol_smile(tick,rf,date_format,expiry_opt)

a=1