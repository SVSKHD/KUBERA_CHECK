import MetaTrader5 as mt5
import numpy as np

if not mt5.initialize(login=212792645, server="OctaFX-Demo", password="pn^eNL4U"):
    raise Exception("Failed to initialize MT5 connection: Error code =", mt5.last_error())
print("Connected successfully")

def get_historical_data(symbol, timeframe, n_periods):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_periods)
    return rates


def analyze_movements_volumes(symbol, timeframe, n_periods, volume_factor=2, movement_factor=1.5):
    # Fetch historical data
    data = get_historical_data(symbol, timeframe, n_periods)
    if data is None or len(data) == 0:
        print(f"No historical data found for {symbol}")
        return

    # Calculate average volume and price movements
    volumes = [bar['real_volume'] for bar in data if 'real_volume' in bar]
    avg_volume = np.mean(volumes) if volumes else 0

    movements = [abs(bar['close'] - bar['open']) for bar in data]
    avg_movement = np.mean(movements) if movements else 0

    # Ensure avg_volume and avg_movement are not zero or NaN to avoid division errors
    if not avg_volume or not avg_movement or np.isnan(avg_volume) or np.isnan(avg_movement):
        print("Average volume or movement is zero or NaN, cannot analyze movements and volumes.")
        return

    # Detect sudden volume and price movements in the last bar
    last_bar = data[-1]
    volume_change = last_bar['real_volume'] / avg_volume
    movement_change = abs(last_bar['close'] - last_bar['open']) / avg_movement

    # Check for significant changes
    if volume_change > volume_factor and movement_change > movement_factor:
        print(f"Sudden movement detected in {symbol}! Volume Change: {volume_change}, Movement Change: {movement_change}")
        # Here, you can insert your logic for taking trading actions

# Example usage
analyze_movements_volumes("EURUSD", mt5.TIMEFRAME_M1, 300)