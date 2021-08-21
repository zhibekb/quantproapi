import json

class TickersDatabase:
    all_tickers = None

def load_tickers_data():
    if TickersDatabase.all_tickers is not None:
        return

    with open("data/tickers.json") as f:
        TickersDatabase.all_tickers = json.load(f)

def get_all_tickers():
    load_tickers_data()

    return TickersDatabase.all_tickers