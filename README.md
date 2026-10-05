# Trading Project

A Python project exploring algorithmic trading strategies on gold (XAUUSD) using
historical data from MetaTrader 5. Built as a learning project, starting from
connecting to MT5 and working up to strategy signals and backtesting.

## Files

- `practice.py` - first practice script
- `mt5_connect.py` - tests the connection to MetaTrader 5 and prints basic account info
- `get_gold_data.py` - pulls hourly XAUUSD price data from MetaTrader 5
- `SMA_gold_strategy.py` - moving average crossover strategy (30/100) with a fixed stop loss and backtest
- `SMC_gold_strategy.py` - detects break of structure, order blocks, fair value gaps and liquidity sweeps, then combines them into long/short signals (signal detection only, no backtest yet)

## Requirements

- Python 3
- MetaTrader 5 terminal installed and logged in (Windows)
- `pip install MetaTrader5 pandas`

## Limitations

The backtests are simplified:

- Stop loss is checked against the close price only, not candle highs and lows
- Profit is in price points, with no lot size
- No spread or commission is included
- An open position at the end of the data is not closed
- The SMC script only counts signals and does not trade them yet

## Next steps

- Check stops against candle highs and lows
- Add spread and commission to the backtest
- Fix the negative index issue in the SMC signal loop
- Stop the same SMC setup flagging on consecutive candles
- Backtest the SMC signals the way the SMA strategy is tested

## Disclaimer

For educational purposes only. Not financial advice.
