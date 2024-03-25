import MetaTrader5 as mt5

# Define the pip size for BTCUSD (it may vary depending on your broker's definition)
pip_size = 0.01  # A pip is typically the second decimal place for BTCUSD

# Establish a connection to MetaTrader 5
if not mt5.initialize(login=212792645, server="OctaFX-Demo", password="pn^eNL4U"):
    raise Exception("Failed to initialize MT5 connection: Error code =", mt5.last_error())
print("Connected successfully")

# Get the last bar for BTCUSD
bars = mt5.copy_rates_from_pos("BTCUSD", mt5.TIMEFRAME_M5, 0, 1)  # Get the last bar

if bars is not None and len(bars) > 0:
    # Calculate pip difference between the open and close of the last bar
    price_movement = bars[-1]['close'] - bars[-1]['open']  # Close price difference from open price
    pip_difference = price_movement / pip_size

    # Calculate potential profit or loss for 1 lot (1 Bitcoin)
    # This assumes 1 lot equals 1 Bitcoin
    profit_loss_per_lot_long = price_movement  # For a long position
    profit_loss_per_lot_short = -price_movement  # For a short position

    # Output the findings
    print(f"Pip difference between open and close of the last bar: {pip_difference:.2f}")
    print(f"Potential profit or loss for 1 lot (1 Bitcoin) if long: {profit_loss_per_lot_long:.2f}")
    print(f"Potential profit or loss for 1 lot (1 Bitcoin) if short: {profit_loss_per_lot_short:.2f}")

else:
    print("Not enough data to calculate differences.")

# Shutdown MT5 connection
mt5.shutdown()
