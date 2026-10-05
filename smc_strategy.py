import MetaTrader5 as mt5
import pandas as pd
import time

mt5.initialize() #Connecting
for i in range(10):
    if mt5.terminal_info() is not None:
        break
    time.sleep(1)

rates = mt5.copy_rates_from_pos("GOLD", mt5.TIMEFRAME_H1, 0, 2000) #Candle data including number of candles and timeframe
mt5.shutdown()

df = pd.DataFrame(rates) #Convert to dataframe, df
df['time'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('EET').dt.tz_convert('Europe/London').dt.strftime('%d/%m/%Y %H:%M')

lookback = 10 #BOS detection

df['bos_bullish'] = False
df['bos_bearish'] = False

for i in range(lookback, len(df)):

    recent_high = df['high'].iloc[i-lookback:i].max()
    recent_low = df['low'].iloc[i-lookback:i].min()
    
    if df['close'].iloc[i] > recent_high:
        df.loc[i, 'bos_bullish'] = True

    if df['close'].iloc[i] < recent_low: #Bearish BOS if statement
        df.loc[i, 'bos_bearish'] = True

df['ob_bullish_high'] = None
df['ob_bullish_low'] = None
df['ob_bearish_high'] = None
df['ob_bearish_low'] = None

for i in range(lookback, len(df)):

    if df['bos_bullish'].iloc[i] == True: #Bullish order block
        for j in range(i-1, i-lookback, -1):
            if df['close'].iloc[j] < df['open'].iloc[j]:
                df.loc[i, 'ob_bullish_high'] = df['high'].iloc[j]
                df.loc[i, 'ob_bullish_low'] = df['low'].iloc[j]
                break
    if df['bos_bearish'].iloc[i] == True: #Bearish order block
        for j in range(i-1, i-lookback, -1):
            if df['close'].iloc[j] > df['open'].iloc[j]:
                df.loc[i, 'ob_bearish_high'] = df['high'].iloc[j]
                df.loc[i, 'ob_bearish_low'] = df['low'].iloc[j]
                break

obs = df[df['ob_bullish_high'].notna() | df['ob_bearish_high'].notna()] #Prints
print("Order blocks found:", len(obs))
print(obs[['time', 'close', 'ob_bullish_high', 'ob_bullish_low', 'ob_bearish_high', 'ob_bearish_low']].tail(5))

df['fvg_bullish'] = False #Fair Value Gaps
df['fvg_bearish'] = False

for i in range(2, len(df)):
    if df['high'].iloc[i-2] < df['low'].iloc[i]:
        df.loc[i, 'fvg_bullish'] = True

    if df['low'].iloc[i-2] > df['high'].iloc[i]:
        df.loc[i, 'fvg_bearish'] = True

bullish_fvg = df[df['fvg_bullish'] == True]
bearish_fvg = df[df['fvg_bearish'] == True]

print("Bullish FVGs:", len(bullish_fvg))
print("Bearish FVGs:", len(bearish_fvg))

df['sweep_bullish'] = False #Liquidity sweep
df['sweep_bearish'] = False

for i in range(lookback, len(df)):
    recent_high = df['high'].iloc[i-lookback:i].max()
    recent_low = df['low'].iloc[i-lookback:i].min()

    if df['low'].iloc[i] < recent_low and df['close'].iloc[i] > recent_low: #Bullish sweep: wicking below recent low but closes above
        df.loc[i, 'sweep_bullish'] = True

    if df['high'].iloc[i] > recent_high and df['close'].iloc[i] < recent_high: #Bearish sweep: wicking above recent high but closes below
        df.loc[i, 'sweep_bearish'] = True

bullish_sweep = df[df['sweep_bullish'] == True]
bearish_sweep = df[df['sweep_bearish'] == True]

print("Bullish sweeps:", len(bullish_sweep))
print("Bearish sweeps:", len(bearish_sweep))

df['smc_long'] = False # Combined SMC Entry Signals - sequence required
df['smc_short'] = False

for i in range(lookback + 4, len(df)):
    
    bos_i = None # Long sequence: BOS to OB to FVG to Sweep (in order)
    ob_i = None
    fvg_i = None
    sweep_i = None

    for k in range(i, i-20, -1): # Find most recent bullish BOS
        if df['bos_bullish'].iloc[k] == True:
            bos_i = k
            break

    if bos_i is not None: # Find OB after BOS
        for k in range(bos_i, i):
            if df['ob_bullish_high'].iloc[k] is not None:
                ob_i = k
                break

    if ob_i is not None: # Find FVG after OB
        for k in range(ob_i, i):
            if df['fvg_bullish'].iloc[k] == True:
                fvg_i = k
                break

    if fvg_i is not None: # Find sweep after FVG
        for k in range(fvg_i, i):
            if df['sweep_bullish'].iloc[k] == True:
                sweep_i = k
                break

    if sweep_i is not None: # All four found in sequence = long signal
        ob_high = df['ob_bullish_high'].iloc[ob_i]
        ob_low = df['ob_bullish_low'].iloc[ob_i]
        sweep_low = df['low'].iloc[sweep_i]
        if sweep_low >= ob_low and sweep_low <= ob_high:
            df.loc[i, 'smc_long'] = True

    bos_i = None # Short sequence: BOS to OB to FVG to Sweep (in order)
    ob_i = None
    fvg_i = None
    sweep_i = None

    for k in range(i, i-20, -1):
        if df['bos_bearish'].iloc[k] == True:
            bos_i = k
            break

    if bos_i is not None:
        for k in range(bos_i, i):
            if df['ob_bearish_high'].iloc[k] is not None:
                ob_i = k
                break

    if ob_i is not None:
        for k in range(ob_i, i):
            if df['fvg_bearish'].iloc[k] == True:
                fvg_i = k
                break

    if fvg_i is not None:
        for k in range(fvg_i, i):
            if df['sweep_bearish'].iloc[k] == True:
                sweep_i = k
                break

    if sweep_i is not None:
        ob_high = df['ob_bearish_high'].iloc[ob_i]
        ob_low = df['ob_bearish_low'].iloc[ob_i]
        sweep_high = df['high'].iloc[sweep_i]
        if sweep_high >= ob_low and sweep_high <= ob_high:
            df.loc[i, 'smc_short'] = True

long_signals = df[df['smc_long'] == True]
short_signals = df[df['smc_short'] == True]
print("SMC Long signals:", len(long_signals))
print("SMC Short signals:", len(short_signals))
print(long_signals[['time', 'close']].head(5))
print(short_signals[['time', 'close']].head(5))