import os
import tempfile

import pytest
import json

from flaskr import quantpro

@pytest.fixture
def client():
    quantpro.server.config['TESTING'] = True

    with quantpro.server.test_client() as client:
        yield client

def test_black_scholes_bad_request_1(client):
    rv = client.post('/option/calculator/black-scholes', 
                     data = {
                        "strikePrice" : 160.2,
                        "volatility" : 0,
                        "interestRate" : 5,
                        "underlyingPrice": 0,
                        "tenor": 1,
                        "dividendYield": 0})

    data = json.loads(rv.data.decode("utf-8"))

    assert "message" in data

    assert set(["volatility", "underlyingPrice", "dividendYield"]) == set(data["message"].keys())

def test_black_scholes_bad_request_2(client):
    rv = client.post('/option/calculator/black-scholes', 
                     data = {
                        "strikePrice" : 160.2,
                        "volatility" : 0.75,
                        "interestRate" : 0,
                        "underlyingPrice": 148.19,
                        "tenor": 0,
                        "dividendYield": 0.56})

    data = json.loads(rv.data.decode("utf-8"))

    assert "message" in data

    assert set(["tenor", "interestRate"]) == set(data["message"].keys())

def test_black_scholes_request(client):
    rv = client.post('/option/calculator/black-scholes', 
                     data = {
                        "strikePrice" : 160.2,
                        "volatility" : 0.75,
                        "interestRate" : 5,
                        "underlyingPrice": 148.19,
                        "tenor": 1,
                        "dividendYield": 0.56})

    assert set(("call", "put", "plot_data")) == set(rv.get_json().keys())

def test_monte_carlo_bad_request(client):
    rv = client.post('/option/calculator/monte-carlo', 
                     data = {
                        "strikePrice" : 160.2,
                        "volatility" : 0.75,
                        "interestRate" : 0,
                        "underlyingPrice": 148.19,
                        "tenor": 0,
                        "dividendYield": 0.56,
                        "deltaPrice": 0.001, 
                        "deltaInterestRate": 0,
                        "deltaVolatility": 0.001})

    data = rv.get_json()

    assert "message" in data

    assert "400 BAD REQUEST" == rv.status

    assert set(["tenor", "interestRate", "timeSteps", "numSimulations", "deltaInterestRate"]) == set(data["message"].keys())

def test_monte_carlo_request(client):
    rv = client.post('/option/calculator/monte-carlo', 
                     data = {
                        "strikePrice" : 160.2,
                        "volatility" : 0.75,
                        "interestRate" : 5,
                        "underlyingPrice": 148.19,
                        "tenor": 1,
                        "dividendYield": 0.56,
                        "deltaPrice": 0.001, 
                        "numSimulations": 1000,
                        "timeSteps": 10,
                        "deltaInterestRate": 0.001,
                        "deltaVolatility": 0.001})

    data = rv.get_json()

    assert "message" not in data

    assert set(("call", "put", "plot_data")) == set(data.keys())
