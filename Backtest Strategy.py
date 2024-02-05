# IMPORTING PACKAGES

import pandas as pd
import requests
import pandas_ta as ta
import matplotlib.pyplot as plt
from termcolor import colored as cl
import math 

plt.rcParams['figure.figsize'] = (20, 10)
plt.style.use('fivethirtyeight')

# EXTRACTING HISTORICAL DATA

def get_historical_data(symbol, start_date, interval):
    url = "https://api.benzinga.com/api/v2/bars"
    querystring = {"token": "379e867da08f4f76bbbb55d5e15cf81d", "symbols": f"{symbol}", "from": f"{start_date}",
                   "interval": f"{interval}"}

    hist_json = requests.get(url, params=querystring).json()

    # Print the obtained JSON for debugging purposes
    print("Obtained JSON:", hist_json)

    df = pd.DataFrame(hist_json[0]['candles'])
    
    return df

# Function to calculate Donchian Channels for day trading
def calculate_donchian_channels(df, window):
    df['dcl'] = df['low'].rolling(window=window).min()
    df['dcm'] = df['close'].rolling(window=window).mean()
    df['dcu'] = df['high'].rolling(window=window).max()
    return df

# PLOTTING INTRADAY DONCHIAN CHANNEL

def plot_intraday_donchian_channel(df, symbol, window):
    plt.plot(df.close, label='CLOSE')
    plt.plot(df.dcl, color='black', linestyle='--', alpha=0.3)
    plt.plot(df.dcm, color='orange', label='DCM')
    plt.plot(df.dcu, color='black', linestyle='--', alpha=0.3, label='DCU, DCL')
    plt.legend()
    plt.title(f'{symbol} Intraday DONCHIAN CHANNELS {window}')
    plt.xlabel('Time')
    plt.ylabel('Close')
    plt.show()

# Function to implement day trading strategy
def implement_day_trading_strategy(df, investment, window):
    in_position = False
    equity = investment
    no_of_shares = 0
    
    for i in range(window, len(df)):
        if df['high'][i] == df['dcu'][i] and not in_position:
            no_of_shares = math.floor(equity / df.close[i])
            equity -= (no_of_shares * df.close[i])
            in_position = True
            print(cl('BUY: ', color='green', attrs=['bold']), f'{no_of_shares} Shares are bought at ${df.close[i]} on {str(df.index[i])}')
        elif df['low'][i] == df['dcl'][i] and in_position:
            equity += (no_of_shares * df.close[i])
            in_position = False
            print(cl('SELL: ', color='red', attrs=['bold']), f'{no_of_shares} Shares are sold at ${df.close[i]} on {str(df.index[i])}')
    
    if in_position:
        equity += (no_of_shares * df.close[i])
        print(cl(f'\nClosing position at {df.close[i]} on {str(df.index[i])}', attrs=['bold']))
        in_position = False

    earning = round(equity - investment, 2)
    roi = round((earning / investment) * 100, 2)
    print(cl(f'EARNING: ${earning} ; ROI: {roi}%', attrs=['bold']))

# Example usage for AAPL stock with a 30-minute interval and a 20-period Donchian Channel
aapl = get_historical_data('AAPL', '2024-01-01', '30m')
aapl_with_dc = calculate_donchian_channels(aapl, 20)
plot_intraday_donchian_channel(aapl_with_dc, 'AAPL', 20)
implement_day_trading_strategy(aapl_with_dc, 100000, 20)
