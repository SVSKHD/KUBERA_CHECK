import MetaTrader5 as mt5
from datetime import datetime

# Define the pip size for BTCUSD (it may vary depending on your broker's definition)
pip_size = 0.01  # Assuming a pip is the second decimal place for BTCUSD

# Establish a connection to MetaTrader 5
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Define a function to calculate the pip difference
def calculate_pip_difference(price1, price2):
    return (price2 - price1) / pip_size

# Get historical bars for BTCUSD
bars = mt5.copy_rates_from_pos("BTCUSD", mt5.TIMEFRAME_M5, 0, 100)

# Analyze historical bars for a 15 pip movement
pip_movement_threshold = 15
for i in range(len(bars)-1):
    pip_difference = calculate_pip_difference(bars[i]['close'], bars[i+1]['close'])
    if abs(pip_difference) >= pip_movement_threshold:
        print(f"15 pip movement detected between {datetime.fromtimestamp(bars[i]['time'])} and {datetime.fromtimestamp(bars[i+1]['time'])}")

# Get the current live feed for BTCUSD
current_price = mt5.symbol_info_tick("BTCUSD")

# Make a decision to go long or short based on the current price action
# This is a simplified decision-making example
if current_price.bid > current_price.ask:  # If the bid price is higher than the ask, it may indicate an uptrend
    print("Decision: Consider taking a LONG position.")
elif current_price.bid < current_price.ask:  # If the bid price is lower than the ask, it may indicate a downtrend
    print("Decision: Consider taking a SHORT position.")
else:
    print("Decision: Market is undecided, no action recommended.")

# Shutdown MT5 connection
mt5.shutdown()
