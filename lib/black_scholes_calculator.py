import math

import numpy as np
import scipy
import scipy.stats

from lib.optiontype import OptionType


def calculate_volatility(stock_price):
    stock_price = stock_price[0:5]
    N = len(stock_price)

    hist_r_60 = [np.log(stock_price[i] / stock_price[i - 1]) for i in range(1, N)]

    hist_r_avg = np.mean(hist_r_60)

    hist_sigma = np.sqrt(
        1
        / (len(hist_r_60) - 1)
        * np.sum([(r_i - hist_r_avg) ** 2 for r_i in hist_r_60])
    )

    return hist_sigma


def black_scholes(option_type, sigma, S_0, K, r, T, q):
    d1 = (np.log(S_0 / K) + (r - q + sigma ** 2 * 0.5) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == OptionType.CALL:
        price = np.exp(-r * T) * (
            S_0 * np.exp((r - q) * T) * scipy.stats.norm.cdf(d1)
            - K * scipy.stats.norm.cdf(d2)
        )

        return price

    elif option_type == OptionType.PUT:
        price = np.exp(-r * T) * (
            K * scipy.stats.norm.cdf(-d2)
            - S_0 * np.exp((r - q) * T) * scipy.stats.norm.cdf(-d1)
        )

        return price


def greeks(option_type, sigma, S_0, K, r, T, q):
    d1 = (np.log(S_0 / K) + (r - q + sigma ** 2 * 0.5) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == OptionType.CALL:
        greeks_delta = np.exp((-q) * T) * scipy.stats.norm.cdf(d1)
        greeks_gamma = (
            np.exp((-q) * T)
            * np.exp((-(d1 ** 2)) / 2)
            / (S_0 * sigma * np.sqrt(T) * np.sqrt(2 * math.pi))
        )
        greeks_theta = (
            -(
                S_0
                * sigma
                * np.exp(-q * T)
                / (2 * np.sqrt(T))
                * 1
                / np.sqrt(2 * math.pi)
                * np.exp(-(d1 ** 2) / 2)
            )
            - r * K * np.exp(-r * T) * scipy.stats.norm.cdf(d2)
            + q * S_0 * np.exp(-q * T) * scipy.stats.norm.cdf(d1)
        ) / 365
        greeks_vega = (
            S_0
            * np.sqrt(T)
            * np.exp((-q) * T)
            * np.exp((-(d1 ** 2)) / 2)
            / (100 * np.sqrt(2 * math.pi))
        )
        greeks_rho = K * T * np.exp(-r * T) * scipy.stats.norm.cdf(d2) / 100

        return greeks_delta, greeks_gamma, greeks_theta, greeks_vega, greeks_rho
    elif option_type == OptionType.PUT:
        greeks_delta = -np.exp((-q) * T) * scipy.stats.norm.cdf(-d1)
        greeks_gamma = (
            np.exp((-q) * T)
            * np.exp((-(d1 ** 2)) / 2)
            / (S_0 * sigma * np.sqrt(T) * np.sqrt(2 * math.pi))
        )
        greeks_theta = (
            -(
                S_0
                * sigma
                * np.exp(-q * T)
                / (2 * np.sqrt(T))
                * 1
                / np.sqrt(2 * math.pi)
                * np.exp(-(d1 ** 2) / 2)
            )
            + r * K * np.exp(-r * T) * scipy.stats.norm.cdf(-d2)
            - q * S_0 * np.exp(-q * T) * scipy.stats.norm.cdf(-d1)
        ) / 365
        greeks_vega = (
            S_0
            * np.sqrt(T)
            * np.exp((-q) * T)
            * np.exp((-(d1 ** 2)) / 2)
            / (100 * np.sqrt(2 * math.pi))
        )
        greeks_rho = -K * T * np.exp(-r * T) * scipy.stats.norm.cdf(-d2) / 100

        return greeks_delta, greeks_gamma, greeks_theta, greeks_vega, greeks_rho


def plot_options(sigma, S_0, K, r, T, q):
    S = list(np.arange(S_0 - S_0 / 2, S_0 + S_0 / 2, 0.5))


    calls = [black_scholes(OptionType.CALL, sigma, s, K, r, T, q) for s in S]
    puts = [black_scholes(OptionType.PUT, sigma, s, K, r, T, q) for s in S]

    return [{"price": price, "call_price": call_price, "put_price": put_price} for price, call_price, put_price in zip(S, calls, puts)]