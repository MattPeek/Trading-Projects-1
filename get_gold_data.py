import MetaTrader5 as mt5
import pandas as pd

# Connect to MT5
mt5.initialize()

# Get the last 100 candles of GOLD on the 1 hour timeframe
rates = mt5.copy_rates_from_pos("GOLD", mt5.TIMEFRAME_H1, 0, 20)

# Convert to a pandas table
df = pd.DataFrame(rates)

# Convert time column to readable dates
df['time'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('EET').dt.tz_convert('Europe/London').dt.strftime('%d/%m/%Y %H:%M')

# Print the data
print(df[['time', 'open', 'high', 'low', 'close']])

mt5.shutdown()