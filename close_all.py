import MetaTrader5 as mt5


def close_all_trades():
    # Initialize connection to the MetaTrader 5 terminal
    if not mt5.initialize(login=212792645, server="OctaFX-Demo", password="pn^eNL4U"):
        raise Exception("Failed to initialize MT5 connection: Error code =", mt5.last_error())
    print("Connected successfully")

    # Retrieve information about all open positions
    positions = mt5.positions_get()
    if positions is None:
        print("No positions found, error code =", mt5.last_error())
    elif len(positions) > 0:
        for position in positions:
            symbol = position.symbol
            volume = position.volume
            position_id = position.ticket
            trade_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY

            # Prepare the request for closing the position
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": trade_type,
                "position": position_id,
                "magic": 0,
                "comment": "Closed by script",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            # Send the trade request
            result = mt5.order_send(close_request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Failed to close position {position_id}: {result}")
            else:
                print(f"Position {position_id} closed successfully.")

    # Shutdown the connection to the MetaTrader 5 terminal
    mt5.shutdown()


# Execute the function to close all trades
close_all_trades()
