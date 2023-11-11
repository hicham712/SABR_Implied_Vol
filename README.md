# SABR_Implied_Vol
Implementation of a SABR model for Equity Options using Yahoo Finance API

/!\ This uses my version of the lib yoptions (hence the file my_yoptions) since it doesn't seem to be getting up to date but it stills works fine with a little tuning ! /!\

This code replicates the following paper: 

- Title: Stochastic Alpha, Beta, Rho (SABR): A Conceptual Study
- Authors: Patrick Hagan, Deep Kumar, Andrew Lesniewski, Diana Woodward
- Published in: Wilmott Magazine, 2002 (Issue 2, pages 56-65)

and applies it to Equity options.

All the data is retrieved from yahoo finance and yahoo finance options chains are used to compute implied volatilities.

The code works this way : 
  
  1- Get options chain data from yahoo finance, and keep the most liquid contracts and various data cleaning
  2- Compute the Implied Volatilities using Black & Scholes model with Newton Raphson Method 
  3- Calibrating the SABR model to those volatilities by minimizing the SABR objective function (more information here : https://www.youtube.com/watch?v=Nldzkkdwt1M)
  4- Plots the SABR and market implied volatilities corresponding to strikes 

This code serves an educating purpose and should not be used to intend profit. 
