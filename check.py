# check.py
import MetaTrader5 as mt5
import time
from close import generic_trade  # Import the generic_trade function from close.py

# Initialize connection to the MetaTrader 5 terminal
if not mt5.initialize(login=212792645, server="OctaFX-Demo", password="pn^eNL4U"):
    raise Exception("Failed to initialize MT5 connection: Error code =", mt5.last_error())
print("Connected successfully")

# Main loop that continuously checks for open trades and closes or opens them based on conditions
while True:
    positions = mt5.positions_get(symbol="BTCUSD")
    if positions is None:
        print("No positions found for BTCUSD, error code =", mt5.last_error())
    elif len(positions) > 0:
        print(f"Found {len(positions)} open positions for BTCUSD. Closing...")
        for position in positions:
            # Close each position
            generic_trade(action="close_sell" if position.type == mt5.ORDER_TYPE_BUY else "close_buy", symbol="BTCUSD", volume=position.volume, position_ticket=position.ticket)
    else:
        # No open positions for BTCUSD, let's open a new BUY order as an example
        print("No open positions for BTCUSD, opening a new BUY order.")
        generic_trade(action="buy", symbol="BTCUSD", volume=0.01)  # Adjust volume as needed

    # Wait for a bit before checking again
    time.sleep(60)  # 60 seconds wait time

# Shutdown the connection to the MetaTrader 5 terminal
mt5.shutdown()
