import yfinance as yf

msft = yf.Ticker("MSFT")

print(msft.info)

hist = msft.history(period="1d")

print(hist)
