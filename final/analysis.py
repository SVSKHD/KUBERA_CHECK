# analysis.py
import MetaTrader5 as mt5


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


def execute_trade(symbol, direction, lot_size=0.01):
    price = mt5.symbol_info_tick(symbol).ask if direction == "BUY" else mt5.symbol_info_tick(symbol).bid
    trade_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": trade_type,
        "price": price,
        "comment": "Executed by bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to execute trade:", result)


def manage_open_trades(symbol, profit_pips=10):
    if not mt5.initialize():
        print("Could not initialize MT5, error code =", mt5.last_error())
        return

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
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Send the trade request to close the position
            result = mt5.order_send(close_request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Failed to close position {position.ticket}, error code: {result.retcode}")
            else:
                print(f"Successfully closed position {position.ticket}.")


import MetaTrader5 as mt5

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

import MetaTrader5 as mt5

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

    pip_size = 0.0001  # Adjust if necessary, e.g., 0.01 for pairs like USDJPY
    high_to_current_diff_pips = (latest_high - current_price) / pip_size
    low_to_current_diff_pips = (current_price - latest_low) / pip_size

    print(f"Live price for {symbol}: {current_price}")

    # Check if the difference from the latest high to the current price is at least 15 pips
    if high_to_current_diff_pips >= pip_difference_threshold:
        print(f"High diff 15 pip from live price: Current price is {high_to_current_diff_pips:.2f} pips below the latest high.")

    # Check if the difference from the current price to the latest low is at least 15 pips
    if low_to_current_diff_pips >= pip_difference_threshold:
        print(f"Low diff 15 pip from live price: Current price is {low_to_current_diff_pips:.2f} pips above the latest low.")

    mt5.shutdown()
    return True

