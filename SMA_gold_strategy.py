import MetaTrader5 as mt5
import pandas as pd
import time

# Connect
if not mt5.initialize():
    print("initialize() failed:", mt5.last_error())
    quit()

for i in range(10):
    if mt5.terminal_info() is not None:
        break
    time.sleep(1)

# Check the symbol exists
symbol = "GOLD"
if not mt5.symbol_select(symbol, True):
    print(f"Symbol {symbol} not found. Try XAUUSD or check Market Watch.")
    print("Last error:", mt5.last_error())
    mt5.shutdown()
    quit()

rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 2000)
if rates is None or len(rates) == 0:
    print("No data returned:", mt5.last_error())
    mt5.shutdown()
    quit()

mt5.shutdown()

# Convert to dataframe
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('EET').dt.tz_convert('Europe/London').dt.strftime('%d/%m/%Y %H:%M')

# Calculate moving averages

fast_period = 30
slow_period = 100

df['MA_fast'] = df['close'].rolling(fast_period).mean()
df['MA_slow'] = df['close'].rolling(slow_period).mean()

# Generate buy and sell signals
df['signal'] = 0

for i in range(1, len(df)):
    if df['MA_fast'].iloc[i] > df['MA_slow'].iloc[i] and df['MA_fast'].iloc[i-1] <= df['MA_slow'].iloc[i-1]:
        df.loc[i, 'signal'] = 1
    if df['MA_fast'].iloc[i] < df['MA_slow'].iloc[i] and df['MA_fast'].iloc[i-1] >= df['MA_slow'].iloc[i-1]:
        df.loc[i, 'signal'] = -1

signals = df[df['signal'] != 0]

# Backtest with stop loss
balance = 10000
position = 0
entry_price = 0
stop_loss = 0
trades = []

for i in range(len(df)):
    current_price = df['close'].iloc[i]
    current_signal = df['signal'].iloc[i]
    current_time = df['time'].iloc[i]

    # Check stop loss on long
    if position == 1 and current_price <= stop_loss:
        profit = current_price - entry_price
        balance += profit
        trades.append(profit)
        position = 0
        print(f"STOP LOSS (long) at ${current_price:.2f} on {current_time} | Loss: ${profit:.2f} | Balance: ${balance:.2f}")

    #Check stop loss on short
    elif position == -1 and current_price >= stop_loss:
        profit = entry_price - current_price
        balance += profit
        trades.append(profit)
        position = 0
        print(f"STOP LOSS (short) at ${current_price:.2f} on {current_time} | Loss: ${profit:.2f} | Balance: ${balance:.2f}")
    
    #BUY
    elif current_signal == 1:
        if position  == -1: #Need to close the short first before the buy
            profit = entry_price - current_price
            balance += profit
            trades.append(profit)
            print(f"CLOSE SHORT at ${current_price:.2f} on {current_time} | Profit: ${profit:.2f} | Balance: ${balance:.2f}")
        entry_price = current_price
        stop_loss = entry_price - 60
        position = 1
        print(f"OPEN LONG at ${entry_price:.2f} on {current_time} | Stop loss: ${stop_loss:.2f}")

    #SELL
    elif current_signal == -1:
        if position == 1: #Need to close the long first before the buy
            profit = current_price - entry_price
            balance += profit
            trades.append(profit)
            print(f"CLOSE LONG at ${current_price:.2f} on {current_time} | Profit: ${profit:.2f} | Balance: ${balance:.2f}")
        entry_price = current_price
        stop_loss = entry_price + 60
        position = -1
        print(f"OPEN SHORT at ${entry_price:.2f} on {current_time} | Stop loss: ${stop_loss:.2f}")

   

print(f"\nTotal trades: {len(trades)}")
print(f"Final balance: ${balance:.2f}")
print(f"Total profit: ${balance - 10000:.2f}")
