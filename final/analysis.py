# analysis.py
import MetaTrader5 as mt5
import ta
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
def detect_volume_change(symbol, periods=20, threshold=1.5):
    if not mt5.initialize():
        print("Could not initialize MT5, error code =", mt5.last_error())
        return False

    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, periods + 1)

    if rates is None or len(rates) == 0:
        print("No rates data found.")
        mt5.shutdown()
        return False

    # Print the first rate entry to inspect its fields

    mt5.shutdown()
    return False  # Temporary return to prevent further execution


def detect_institutional_movement(symbol, periods=20, threshold=1.5):
    if not mt5.initialize():
        print("Could not initialize MT5, error code =", mt5.last_error())
        return False

    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, periods)

    # Check if rates data was successfully retrieved
    if rates is None:
        print(f"Failed to retrieve rates for {symbol}.")
        mt5.shutdown()
        return False

    large_movements = sum(1 for rate in rates if (rate['high'] - rate['low']) > (
                (sum(r['high'] - r['low'] for r in rates) / periods) * threshold))

    mt5.shutdown()
    return large_movements >= 2



def manage_open_trades(symbol, profit_pips=10):
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        print("Failed to get positions, error code =", mt5.last_error())
        mt5.shutdown()
        return

    for position in positions:
        if position.profit >= profit_pips:
            print(f"Closing position {position.ticket} with profit: {position.profit}")

            # Determine the trade type for closing
            trade_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).bid if trade_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(
                symbol).ask

            # Prepare the request for closing the position
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": position.volume,
                "type": trade_type,
                "position": position.ticket,
                "price": price,
                "magic": 0,
                "comment": "Closed by bot for profit",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            # Send the trade request to close the position
            result = mt5.order_send(close_request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Failed to close position {position.ticket}, error code: {result.retcode}")
            else:
                print(f"Successfully closed position {position.ticket}.")


def detect_price_differences(symbols, pip_difference_threshold=15):
    if not mt5.initialize():
        print("Could not initialize MT5, error code =", mt5.last_error())
        return False

    for symbol in symbols:  # 'symbols' should be a list of strings, not tuples
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)
        if rates is None or len(rates) == 0:
            print(f"Failed to retrieve rates for {symbol}.")
            continue

        latest_rate = rates[0]
        high_to_current_diff = abs(latest_rate['high'] - latest_rate['close']) * 10**4
        low_to_current_diff = abs(latest_rate['close'] - latest_rate['low']) * 10**4

        if high_to_current_diff >= pip_difference_threshold or low_to_current_diff >= pip_difference_threshold:
            print(f"Criteria met in {symbol}: High-to-current diff {high_to_current_diff:.0f} pips, Low-to-current diff {low_to_current_diff:.0f} pips.")

    mt5.shutdown()
    return True

def print_price_info(symbol, pip_difference_threshold=15):
    if not mt5.initialize():
        print("Could not initialize MT5, error code =", mt5.last_error())
        return False

    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)

    if rates is None or len(rates) == 0:
        print(f"Failed to retrieve rates for {symbol}.")
        mt5.shutdown()
        return False

    latest_rate = rates[0]
    current_price = latest_rate['close']
    latest_high = latest_rate['high']
    latest_low = latest_rate['low']

    pip_size = 0.0001  # Adjust for 5-digit pricing or pairs like USDJPY if necessary
    high_to_current_diff_pips = (latest_high - current_price) / pip_size
    low_to_current_diff_pips = (current_price - latest_low) / pip_size

    print(f"Live price for {symbol}: {current_price}, Latest High: {latest_high}, Latest Low: {latest_low}")
    # Check if the pip difference thresholds are met or exceeded
    if high_to_current_diff_pips >= pip_difference_threshold:
        print(f"{symbol} High diff threshold met: {high_to_current_diff_pips:.2f} pips below the latest high.")

    if low_to_current_diff_pips >= pip_difference_threshold:
        print(f"{symbol} Low diff threshold met: {low_to_current_diff_pips:.2f} pips above the latest low.")

    return True

def get_sma_signals(symbol, timeframe):
    # Fetch historical bars for the symbol
    bars = mt5.copy_rates_from_pos(symbol, timeframe, 0, 240)
    if bars is None:
        print('copy_rates_from_pos() failed, error code =', mt5.last_error())
        quit()

    # Prepare the DataFrame
    df = pd.DataFrame(bars)
    df.set_index(pd.to_datetime(df['time'], unit='s'), inplace=True)
    df.drop(columns=['time'], inplace=True)

    # Define SMA periods
    short_window = 10  # Short-term SMA window
    long_window = 50   # Long-term SMA window

    # Calculate SMAs
    df['sma_short'] = ta.trend.sma_indicator(df['close'], window=short_window)
    df['sma_long'] = ta.trend.sma_indicator(df['close'], window=long_window)

    # Initialize signals column
    df['signal'] = 0  # No signal

    # Generate buy signals (1) where short SMA crosses above long SMA
    df.loc[df['sma_short'] > df['sma_long'], 'signal'] = 1  # Long/Buy signal

    # Generate sell signals (-1) where short SMA crosses below long SMA
    df.loc[df['sma_short'] < df['sma_long'], 'signal'] = -1  # Short/Sell signal

    return df[['close', 'sma_short', 'sma_long', 'signal']]

def get_rsi_signal(symbol, timeframe):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 500)
    if rates is None or len(rates) == 0:
        print(f"No rates data found for {symbol} on timeframe {timeframe}.")
        return 'neutral'  # Default to neutral if no data is found

    df = pd.DataFrame(rates)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)  # 14-period RSI

    # Define the signal based on RSI thresholds
    if df['rsi'].iloc[-1] > 70:
        return 'sell'
    elif df['rsi'].iloc[-1] < 30:
        return 'buy'
    else:
        return 'neutral'


def get_macd_signal(symbol, timeframe):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 500)
    if rates is None or len(rates) == 0:
        print(f"No rates data found for {symbol} on timeframe {timeframe}.")
        return 'neutral'  # Default to neutral if no data is found

    df = pd.DataFrame(rates)
    macd = ta.trend.MACD(df['close'])
    df['macd_diff'] = macd.macd_diff()

    # Define the signal based on the MACD histogram
    if df['macd_diff'].iloc[-2] < 0 and df['macd_diff'].iloc[-1] > 0:
        return 'buy'
    elif df['macd_diff'].iloc[-2] > 0 and df['macd_diff'].iloc[-1] < 0:
        return 'sell'
    else:
        return 'neutral'


def analyze_market(symbol, timeframe):
    rsi_signal = get_rsi_signal(symbol, timeframe)
    macd_signal = get_macd_signal(symbol, timeframe)

    if rsi_signal == 'buy' and macd_signal == 'buy':
        return 'buy'
    elif rsi_signal == 'sell' and macd_signal == 'sell':
        return 'sell'
    else:
        return 'neutral'


async def async_get_rates(symbol, timeframe, count):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        rates = await loop.run_in_executor(pool, mt5.copy_rates_from_pos, symbol, timeframe, 0, count)
    return rates

async def async_get_rsi_signal(symbol, timeframe):
    rates = await async_get_rates(symbol, timeframe, 500)
    if rates is None or len(rates) == 0:
        return 'neutral'

    df = pd.DataFrame(rates)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)

    if df['rsi'].iloc[-1] > 70:
        return 'sell'
    elif df['rsi'].iloc[-1] < 30:
        return 'buy'
    else:
        return 'neutral'

async def async_get_macd_signal(symbol, timeframe):
    rates = await async_get_rates(symbol, timeframe, 500)
    if rates is None or len(rates) == 0:
        return 'neutral'

    df = pd.DataFrame(rates)
    macd = ta.trend.MACD(df['close'])
    df['macd_diff'] = macd.macd_diff()

    if df['macd_diff'].iloc[-2] < 0 and df['macd_diff'].iloc[-1] > 0:
        return 'buy'
    elif df['macd_diff'].iloc[-2] > 0 and df['macd_diff'].iloc[-1] < 0:
        return 'sell'
    else:
        return 'neutral'

async def async_analyze_market(symbol, timeframe):
    rsi_signal = await async_get_rsi_signal(symbol, timeframe)
    macd_signal = await async_get_macd_signal(symbol, timeframe)

    if rsi_signal == 'buy' and macd_signal == 'buy':
        print("BUY")
        return 'buy'
    elif rsi_signal == 'sell' and macd_signal == 'sell':
        print("SEL")
        return 'sell'
    else:
        print("NOTHING FOR NOW")
        return 'neutral'