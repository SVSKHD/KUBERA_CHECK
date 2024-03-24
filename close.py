import MetaTrader5 as mt5

def generic_trade(action, symbol, volume, position_ticket=None, comment="Trade executed by script"):
    # Determine the trade type based on the action
    if action == "buy":
        trade_type = mt5.ORDER_TYPE_BUY
    elif action == "sell":
        trade_type = mt5.ORDER_TYPE_SELL
    elif action == "close_buy":
        trade_type = mt5.ORDER_TYPE_SELL
    elif action == "close_sell":
        trade_type = mt5.ORDER_TYPE_BUY
    else:
        print("Invalid action specified.")
        return

    # Prepare the trade request
    trade_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": trade_type,
        "magic": 0,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    # If a position ticket is provided, it's a close request
    if position_ticket is not None:
        trade_request["position"] = position_ticket

    # Send the trade request
    result = mt5.order_send(trade_request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to execute trade:", result)
    else:
        if position_ticket is None:
            print(f"Trade opened successfully. Ticket: {result.order}")
        else:
            print(f"Trade closed successfully. Closed position ticket: {position_ticket}")