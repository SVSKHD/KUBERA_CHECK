import MetaTrader5 as mt5
import time

# Initialize connection to the MetaTrader 5 terminal
if not mt5.initialize(login=212792645, server="OctaFX-Demo", password="pn^eNL4U"):
            raise Exception("Failed to initialize MT5 connection: Error code =", mt5.last_error())
print("Connected successfully")

# Main loop that continuously checks for open trades and closes them
while True:
    # Retrieve information about all open positions
    positions = mt5.positions_get()
    if positions == None:
        print("No positions found, error code =", mt5.last_error())
    elif len(positions) > 0:
        print(f"Found {len(positions)} open positions. Closing...")
        for position in positions:
            ticket = position.ticket
            # Check if the position is a BUY or SELL
            if position.type == mt5.ORDER_TYPE_BUY:
                action_type = mt5.ORDER_TYPE_SELL
            else:
                action_type = mt5.ORDER_TYPE_BUY
            # Prepare the request for closing the position
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": action_type,
                "position": ticket,
                "magic": 0,
                "comment": "Closed by script",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            # Send the trade request
            result = mt5.order_send(close_request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print("Failed to close position:", result)
            else:
                print(f"Position {ticket} closed successfully.")

    # Wait for a bit before checking again
    time.sleep(10)

# Shutdown the connection to the MetaTrader 5 terminal
mt5.shutdown()
