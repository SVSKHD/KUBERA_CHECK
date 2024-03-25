import MetaTrader5 as mt5
from datetime import datetime

# Define the pip size for the currency pair (commonly the fourth decimal place)
pip_size = 0.0001  # For most currency pairs

# Establish a connection to MetaTrader 5
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Define a function to calculate the pip difference
def calculate_pip_difference(high, low):
    return (high - low) / pip_size

# Get historical bars for a currency pair
symbol = "EURUSD"  # Replace with the desired currency pair
bars = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 100)

# Analyze historical bars for a 15 pip movement
pip_movement_threshold = 15
latest_significant_bar = None
for i in range(len(bars)-1, -1, -1):  # Iterate backwards to find the latest significant movement
    pip_difference = calculate_pip_difference(bars[i]['high'], bars[i]['low'])
    if pip_difference >= pip_movement_threshold:
        latest_significant_bar = bars[i]
        print(f"15 pip movement detected on {datetime.fromtimestamp(bars[i]['time'])}")
        break  # Exit the loop once the latest significant bar is found

# Check the current live feed for the currency pair
current_price = mt5.symbol_info_tick(symbol)

# Make a decision to go long or short based on the current price action
if latest_significant_bar:
    mid_price = (latest_significant_bar['high'] + latest_significant_bar['low']) / 2
    if current_price.last >= mid_price:
        # If current price is closer to the high, consider a short trade
        print(f"Decision: Consider taking a SHORT trade on {symbol}.")
    else:
        # If current price is closer to the low, consider a long trade
        print(f"Decision: Consider taking a LONG trade on {symbol}.")
else:
    print("No significant pip movement found recently.")

# Shutdown MT5 connection
mt5.shutdown()
