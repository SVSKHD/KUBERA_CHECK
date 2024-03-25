import MetaTrader5 as mt5
import pytz
from datetime import datetime

# Function to fetch historical data
def get_historical_data(symbol, timeframe, n_periods):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_periods)
    return rates

# Convert timestamp to India's timezone
def convert_to_ist(timestamp):
    utc_time = datetime.utcfromtimestamp(timestamp)
    ist_timezone = pytz.timezone('Asia/Kolkata')
    ist_time = utc_time.replace(tzinfo=pytz.utc).astimezone(ist_timezone)
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')

# Example: Analyze and print historical data with IST timestamps
def analyze_data(symbol, timeframe, n_periods):
    data = get_historical_data(symbol, timeframe, n_periods)
    if data is not None and len(data) > 0:
        for bar in data:
            time_ist = convert_to_ist(bar['time'])
            print(f"Date and Time (IST): {time_ist}, Open: {bar['open']}, High: {bar['high']}, Low: {bar['low']}, Close: {bar['close']}")

# Initialize MT5 connection
if not mt5.initialize(login=212792645, server="OctaFX-Demo", password="pn^eNL4U"):
    raise Exception("Failed to initialize MT5 connection: Error code =", mt5.last_error())
else:
    print("Connected to MetaTrader 5.")
    # Example usage for EURUSD, 1-minute timeframe, last 10 periods
    analyze_data("EURUSD", mt5.TIMEFRAME_M1, 100)
    # Shutdown MT5 connection
    mt5.shutdown()
