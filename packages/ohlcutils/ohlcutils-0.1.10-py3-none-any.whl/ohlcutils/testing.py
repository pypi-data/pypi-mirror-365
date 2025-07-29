from ohlcutils.data import load_symbol
from ohlcutils.enums import Periodicity
from ohlcutils.charting import plot
from ohlcutils.indicators import backtest_abc_trend_strategy

# symbol = "INFY_STK___"
# md = load_symbol(symbol, days=10000)
# out = backtest_abc_trend_strategy(md, symbol=symbol)
md = load_symbol(
    "INFY_STK___",
    end_time="2021-07-31",
    days=100,
)
print(md)
