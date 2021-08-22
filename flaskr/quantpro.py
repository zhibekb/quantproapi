from flask import Flask
from flask_restful import Resource, Api, reqparse

from flask_cors import CORS

from tickers import tickersdb
from lib import black_scholes_calculator, monte_carlo_calculator
from lib.optiontype import OptionType

import numpy as np

import yfinance as yf

from flaskr import validation

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
        parser = reqparse.RequestParser(bundle_errors=True)

        parser.add_argument("strikePrice", required=True, type=validation.non_zero_positive_float)
        parser.add_argument("volatility", required=True, type=validation.non_zero_positive_float)
        parser.add_argument("interestRate", required=True, type=validation.non_zero_positive_float)
        parser.add_argument("underlyingPrice", required=True, type=validation.non_zero_positive_float)
        parser.add_argument("tenor", required=True, type=validation.non_zero_positive_float)
        parser.add_argument("dividendYield", required=True, type=validation.non_zero_positive_float)

        args = parser.parse_args()

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
        parser = reqparse.RequestParser(bundle_errors=True)

        parser.add_argument("strikePrice", required=True, type=validation.non_zero_positive_float)
        parser.add_argument("volatility", required=True, type=validation.non_zero_positive_float)
        parser.add_argument("interestRate", required=True, type=validation.non_zero_positive_float)
        parser.add_argument("underlyingPrice", required=True, type=validation.non_zero_positive_float)
        parser.add_argument("tenor", required=True, type=validation.non_zero_positive_float)
        parser.add_argument("dividendYield", required=True, type=validation.non_zero_positive_float)

        parser.add_argument("timeSteps", required=True, type=validation.positive_int)
        parser.add_argument("numSimulations", required=True, type=validation.positive_int)
        parser.add_argument("deltaPrice", required=True, type=validation.non_zero_positive_float)
        parser.add_argument("deltaVolatility", required=True, type=validation.non_zero_positive_float)
        parser.add_argument("deltaInterestRate", required=True, type=validation.non_zero_positive_float)

        args = parser.parse_args()

        volatility = args["volatility"] / 100
        underlying_price = args["underlyingPrice"]
        strike_price = args["strikePrice"]
        interest_rate = args["interestRate"] / 100
        tenor = args["tenor"]
        dividend_yield = args["dividendYield"] / 100
        time_steps = args["timeSteps"]
        num_simulations = args["numSimulations"]
        delta_price = args["deltaPrice"]
        delta_volatility = args["deltaVolatility"]
        delta_interest_rate = args["deltaInterestRate"]

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
