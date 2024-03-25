# analysis.py
import MetaTrader5 as mt5

def detect_volume_change(symbol, periods=20, threshold=1.5):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, periods + 1)
    volumes = [rate['volume'] for rate in rates]
    avg_volume = sum(volumes[:-1]) / periods
    return volumes[-1] > avg_volume * threshold

def detect_institutional_movement(symbol, periods=20, threshold=1.5):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, periods)
    large_movements = sum(1 for rate in rates if (rate['high'] - rate['low']) > ((sum(r['high'] - r['low'] for r in rates) / periods) * threshold))
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
