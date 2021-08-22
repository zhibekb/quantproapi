from flask import Flask
from flask_restful import Resource, Api, reqparse

from flask_cors import CORS

from tickers import tickersdb
from lib import black_scholes_calculator, monte_carlo_calculator
from lib.optiontype import OptionType

import numpy as np

import yfinance as yf

server = Flask(__name__)
CORS(server)
api = Api(server)


class EuropeanOptionCalculator(Resource):
    def get(self):
        return {"hello": "world"}


class AllTickers(Resource):
    def get(self):
        return tickersdb.get_all_tickers()


class TickerData(Resource):
    def get(self, ticker):
        ticker_data = yf.Ticker(ticker)

        hist = ticker_data.history(period="1d")

        last_close = hist["Close"][0]

        dividend_yield = ticker_data.info["trailingAnnualDividendRate"] / last_close

        return {"close": last_close, "dividendYield": dividend_yield}


class VolatilityCalculator(Resource):
    def get(self, ticker):
        ticker_data = yf.Ticker(ticker)

        stock_price = ticker_data.history(period="60d")["Close"]

        return {
            "volatility": black_scholes_calculator.calculate_volatility(stock_price)
        }


class BlackScholesCalculator(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("strikePrice")
    parser.add_argument("volatility")
    parser.add_argument("interestRate")
    parser.add_argument("underlyingPrice")
    parser.add_argument("tenor")
    parser.add_argument("dividendYield")

    def _calculate(
        self,
        option_type,
        volatility,
        underlying_price,
        strike_price,
        interest_rate,
        tenor,
        dividend_yield,
    ):
        option_price = black_scholes_calculator.black_scholes(
            option_type,
            volatility,
            underlying_price,
            strike_price,
            interest_rate,
            tenor,
            dividend_yield,
        )

        delta, gamma, theta, vega, rho = black_scholes_calculator.greeks(
            option_type,
            volatility,
            underlying_price,
            strike_price,
            interest_rate,
            tenor,
            dividend_yield,
        )

        return {
            "price": option_price,
            "delta": delta,
            "gamma": gamma,
            "theta": theta,
            "vega": vega,
            "rho": rho,
        }

    def post(self):
        args = BlackScholesCalculator.parser.parse_args()

        volatility = float(args["volatility"]) / 100
        underlying_price = float(args["underlyingPrice"])
        strike_price = float(args["strikePrice"])
        interest_rate = float(args["interestRate"]) / 100
        tenor = float(args["tenor"])
        dividend_yield = float(args["dividendYield"]) / 100

        black_scholes_plot = black_scholes_calculator.plot_options(
            volatility,
            underlying_price,
            strike_price,
            interest_rate,
            tenor,
            dividend_yield,
        )

        return {
            "call": self._calculate(
                OptionType.CALL,
                volatility,
                underlying_price,
                strike_price,
                interest_rate,
                tenor,
                dividend_yield,
            ),
            "put": self._calculate(
                OptionType.PUT,
                volatility,
                underlying_price,
                strike_price,
                interest_rate,
                tenor,
                dividend_yield,
            ),
            "plot_data": black_scholes_plot,
        }


class MonteCarloOptionPriceCalculator(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("strikePrice")
    parser.add_argument("volatility")
    parser.add_argument("interestRate")
    parser.add_argument("underlyingPrice")
    parser.add_argument("tenor")
    parser.add_argument("dividendYield")
    parser.add_argument("timeSteps")
    parser.add_argument("numSimulations")
    parser.add_argument("deltaPrice")
    parser.add_argument("deltaVolatility")
    parser.add_argument("deltaInterestRate")

    def _calculate(
        self,
        option_type,
        volatility,
        underlying_price,
        strike_price,
        interest_rate,
        tenor,
        dividend_yield,
        time_steps,
        num_simulations,
        delta_price,
        delta_volatility,
        delta_interest_rate,
    ):

        option_price = monte_carlo_calculator.monte_carlo(
            option_type,
            underlying_price,
            strike_price,
            tenor,
            interest_rate,
            dividend_yield,
            volatility,
            time_steps,
            num_simulations,
        )

        delta, gamma, theta, vega, rho = monte_carlo_calculator.greeks_fdm(
            option_type,
            underlying_price,
            strike_price,
            tenor,
            interest_rate,
            dividend_yield,
            volatility,
            time_steps,
            num_simulations,
            delta_price,
            delta_volatility,
            delta_interest_rate,
        )

        return {
            "price": option_price,
            "delta": delta,
            "gamma": gamma,
            "theta": theta,
            "vega": vega,
            "rho": rho,
        }

    def post(self):
        args = MonteCarloOptionPriceCalculator.parser.parse_args()

        volatility = float(args["volatility"]) / 100
        underlying_price = float(args["underlyingPrice"])
        strike_price = float(args["strikePrice"])
        interest_rate = float(args["interestRate"]) / 100
        tenor = float(args["tenor"])
        dividend_yield = float(args["dividendYield"]) / 100
        time_steps = int(args["timeSteps"])
        num_simulations = int(args["numSimulations"])
        delta_price = float(args["deltaPrice"])
        delta_volatility = float(args["deltaVolatility"])
        delta_interest_rate = float(args["deltaInterestRate"])

        params = (
            volatility,
            underlying_price,
            strike_price,
            interest_rate,
            tenor,
            dividend_yield,
            time_steps,
            num_simulations,
            delta_price,
            delta_volatility,
            delta_interest_rate,
        )

        return {
            "call": self._calculate(
                OptionType.CALL,
                *params,
            ),
            "put": self._calculate(OptionType.PUT, *params),
            "plot_data": monte_carlo_calculator.plot_data(
                underlying_price,
                strike_price,
                tenor,
                interest_rate,
                dividend_yield,
                volatility,
                time_steps,
                num_simulations
            )
        }


api.add_resource(EuropeanOptionCalculator, "/options")
api.add_resource(AllTickers, "/symbols")
api.add_resource(TickerData, "/symbol/<ticker>")
api.add_resource(VolatilityCalculator, "/symbol/volatility/<ticker>")
api.add_resource(BlackScholesCalculator, "/option/calculator/black-scholes")
api.add_resource(MonteCarloOptionPriceCalculator, "/option/calculator/monte-carlo")

if __name__ == "__main__":
    server.run(debug=True)
