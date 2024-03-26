import MetaTrader5 as mt5

def place_trade(symbol, order_type, volume, stop_loss=None, take_profit=None, deviation=20):
    """
    Places a trade on MT5.

    Parameters:
    - symbol (str): The symbol to trade.
    - order_type (str): 'long' for a buy order, 'short' for a sell order.
    - volume (float): The volume of the trade.
    - stop_loss (float, optional): The stop loss price.
    - take_profit (float, optional): The take profit price.
    - deviation (int): Maximum allowed deviation from the requested price.

    Returns:
    - dict: Result of the trade operation.
    """
    # Get current price for the symbol
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"{symbol} not found, can not call order_check()")
        mt5.shutdown()
        return

    if not symbol_info.visible:
        print(f"{symbol} is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            print(f"symbol_select({symbol}) failed, exit")
            mt5.shutdown()
            return

    point = symbol_info.point
    price = mt5.symbol_info_tick(symbol).ask if order_type == 'long' else mt5.symbol_info_tick(symbol).bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY if order_type == 'long' else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": price - 100 * point if stop_loss is None else stop_loss,
        "tp": price + 100 * point if take_profit is None else take_profit,
        "deviation": deviation,
        "magic": 0,
        "comment": "Placed by Python script",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Send the trade request
    result = mt5.order_send(request)
    return result


def close_opposite_trades(symbol, trade_type):
    # Retrieve information about open positions for a specific symbol
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        for position in positions:
            # Determine the opposite trade type
            opposite_type = mt5.ORDER_TYPE_BUY if position.type == mt5.ORDER_TYPE_SELL else mt5.ORDER_TYPE_SELL

            # Check if the current position is in the opposite direction of the intended trade
            if trade_type != position.type:
                # Prepare the request for closing the opposite position
                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": position.volume,
                    "type": opposite_type,
                    "position": position.ticket,
                    "magic": 0,
                    "comment": "Close opposite trade",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK,
                }
                # Send the trade request to close the position
                result = mt5.order_send(close_request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f"Failed to close opposite position {position.ticket}: {result}")
                else:
                    print(f"Opposite position {position.ticket} closed successfully.")

