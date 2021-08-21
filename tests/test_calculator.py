import pytest

from lib import calculator
from lib.optiontype import OptionType


def test_calculate_volatility():
    # GIVEN 5 days of close prices

    # CALCULATE 5 day volatility

    stock_price = [125.092575, 124.423584, 124.094070, 124.872902, 123.355186]

    assert pytest.approx(0.00764, abs=0.0001) == calculator.calculate_volatility(
        stock_price
    )

    # WHEN stock price is constant, volatility is zero
    assert 0 == calculator.calculate_volatility([3] * 20)

    # WHEN for monotinically increasing stock price, volatility is 0.20
    assert pytest.approx(0.2, abs=0.01) == calculator.calculate_volatility(range(1, 20))


def test_black_sholes():
    interest_rate = 0.05 / 100  # input interest rate
    underlying_price = 148.19  # today's price of AAPL stock
    strike_price = 160.2
    volatility = 0.76 / 100
    dividend_yield = 0.56 / 100
    tenor = 1

    assert pytest.approx(0) == calculator.black_scholes(
        OptionType.CALL,
        volatility,
        underlying_price,
        strike_price,
        interest_rate,
        tenor,
        dividend_yield,
    )
    assert pytest.approx(12.757, abs=0.001) == calculator.black_scholes(
        OptionType.PUT,
        volatility,
        underlying_price,
        strike_price,
        interest_rate,
        tenor,
        dividend_yield,
    )


def test_greeks_calculation():
    interest_rate = 0.05 / 100  # input interest rate
    underlying_price = 148.19  # today's price of AAPL stock
    strike_price = 160.2
    volatility = 0.76 / 100
    dividend_yield = 0.56 / 100
    tenor = 1

    assert (
        -0.9944156507715979,
        4.451436229064084e-27,
        -0.0020415610674002463,
        7.429362416016048e-27,
        -1.6011992002166293,
    ) == calculator.greeks(
        OptionType.PUT,
        volatility,
        underlying_price,
        strike_price,
        interest_rate,
        tenor,
        dividend_yield,
    )

    assert (
        4.5530849955671965e-28,
        4.451436229064084e-27,
        -6.791853657917837e-30,
        7.429362416016048e-27,
        6.742599946009795e-28,
    ) == calculator.greeks(
        OptionType.CALL,
        volatility,
        underlying_price,
        strike_price,
        interest_rate,
        tenor,
        dividend_yield,
    )
