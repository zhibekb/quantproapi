import numpy as np

from lib.optiontype import OptionType


def monte_carlo_paths(S_0, T, r, q, sigma, steps, N):
    dt = T / steps
    logS_T = np.log(S_0) + np.cumsum(
        (
            (r - q - sigma ** 2 / 2) * dt
            + sigma * np.sqrt(dt) * np.random.normal(size=(steps, N))
        ),
        axis=0,
    )
    return np.exp(logS_T)


def monte_carlo(option_type, S_0, K, T, r, q, sigma, steps, N):
    paths_S_T = monte_carlo_paths(S_0, T, r, q, sigma, steps, N)

    if option_type == OptionType.CALL:
        expectedvalue_C_T = np.mean(np.maximum(paths_S_T[-1] - K, 0))
    elif option_type == OptionType.PUT:
        expectedvalue_C_T = np.mean(np.maximum(K - paths_S_T[-1], 0))

    fairOptionPrice = np.exp(r * 0) * expectedvalue_C_T / np.exp(r * T)

    return fairOptionPrice


def greeks_fdm(
    option_type, S_0, K, T, r, q, sigma, steps, N, delta_S, delta_sigma, delta_r
):
    delta_T = T / steps

    delta = (
        monte_carlo(option_type, S_0 + delta_S, K, T, r, q, sigma, steps, N)
        - monte_carlo(option_type, S_0, K, T, r, q, sigma, steps, N)
    ) / delta_S
    gamma = (
        monte_carlo(option_type, S_0 + delta_S, K, T, r, q, sigma, steps, N)
        - 2 * monte_carlo(option_type, S_0, K, T, r, q, sigma, steps, N)
        + monte_carlo(option_type, S_0 - delta_S, K, T, r, q, sigma, steps, N)
    ) / (delta_S * delta_S)
    theta = (
        monte_carlo(option_type, S_0, K, T + delta_T, r, q, sigma, steps, N)
        - monte_carlo(option_type, S_0, K, T, r, q, sigma, steps, N)
    ) / delta_T
    vega = (
        monte_carlo(option_type, S_0, K, T, r, q, sigma + delta_sigma, steps, N)
        - monte_carlo(option_type, S_0, K, T, r, q, sigma, steps, N)
    ) / delta_sigma

    print(delta_r)
    rho = (
        monte_carlo(option_type, S_0, K, T, r + delta_r, q, sigma, steps, N)
        - monte_carlo(option_type, S_0, K, T, r, q, sigma, steps, N)
    ) / delta_r


    return delta, gamma, theta, vega, rho


def plot_data(S_0, K, T, r, q, sigma, steps, N):
    paths_S_T = monte_carlo_paths(S_0, T, r, q, sigma, steps, N)

    call_payoff = np.maximum(paths_S_T[-1] - K, 0)
    put_payoff = np.maximum(K - paths_S_T[-1], 0)

    data = [
        (price, call_price, put_price)
        for price, call_price, put_price in zip(
            list(paths_S_T[-1]), list(call_payoff), list(put_payoff)
        )
    ]

    return [{"price" : price, "put_price" : put_price, "call_price": call_price} for (price, call_price, put_price) in sorted(data, key=lambda x: x[0])]

