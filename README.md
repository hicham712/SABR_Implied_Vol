# SABR_Implied_Vol
============= Implementation of a SABR model for Equity Options using Yahoo Finance API =============

/!\ This uses my version of the lib yoptions (hence the file my_yoptions) since it doesn't seem to be getting up to date but it stills works fine with a little tuning ! /!\

This code replicates the following paper: 

- Title: Stochastic Alpha, Beta, Rho (SABR): A Conceptual Study
- Authors: Patrick Hagan, Deep Kumar, Andrew Lesniewski, Diana Woodward
- Published in: Wilmott Magazine, 2002 (Issue 2, pages 56-65)

and applies it to Equity options.

============= The code is applicable to any Equity options that has option data on yahoo finance. It is possible to change parameters in the "main.py" file to apply to different equities =============

All the data is retrieved from yahoo finance and yahoo finance options chains are used to compute implied volatilities.
Commented code is here if one's would like to use CBOE data,downloaded as csv, for accuracy (example on TSLA : https://www.cboe.com/delayed_quotes/tsla/quote_table)

Data of yahoo finance has been tested against CBOE and seems to be accurate in most cases.

The code works this way : 

1- Get options chain data from yahoo finance, and keep the most liquid contracts and various data cleaning
2- Compute the Implied Volatilities using Black & Scholes model with Newton Raphson Method 
3- Calibrating the SABR model to those volatilities by minimizing the SABR objective function, with a Beta set to 0.5 for simplicity (more information here : https://www.youtube.com/watch?v=Nldzkkdwt1M)
4- Plots the SABR and market implied volatilities corresponding to strikes 

Here is an example using the TSLA options that expires on 2023-11-24

Results from SABR calibration are [alpha,rho,nu]= [ 3.81596237 -0.33392059  3.3351598 ]

![Project Image]([image_url](TSLA_impliedvol.png))


This code serves an educating purpose and should not be used to intend profit. 
