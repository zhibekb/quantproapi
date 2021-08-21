import json
from pytickersymbols import PyTickerSymbols

stock_data = PyTickerSymbols()
countries = stock_data.get_all_countries()
indices = stock_data.get_all_indices()
industries = stock_data.get_all_industries()

tickers = []
seen_symbols = []
for i in indices:
    for s in stock_data.get_stocks_by_index(i):
        for ticker in s["symbols"]:
            if ticker["yahoo"] in seen_symbols:
                print("Skipping")
                continue
            tickers.append({"name": s["name"], "currency": ticker["currency"], "symbol": ticker["yahoo"]})
            seen_symbols.append(ticker["yahoo"])

with open("tickers.json", "w") as f:
    json.dump(tickers, f)

