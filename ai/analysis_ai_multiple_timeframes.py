import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import asyncio
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model


# Function to scale data
def scale_data(data):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data.reshape(-1, 1))
    return scaled_data, scaler


# Function to create sequences for LSTM input
def create_sequences(data, look_back=60):
    sequences = []
    for i in range(len(data) - look_back):
        sequences.append(data[i:(i + look_back), 0])
    return np.array(sequences)


# Asynchronous function to fetch rates using MetaTrader5
async def async_get_rates(symbol, timeframe, count):
    loop = asyncio.get_event_loop()

    def get_rates():
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            mt5.shutdown()
            return None
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        mt5.shutdown()  # Shutdown MT5 connection
        return rates

    # Use run_in_executor to run blocking MT5 function in a separate thread
    rates = await loop.run_in_executor(None, get_rates)

    # Convert to DataFrame
    if rates is not None and len(rates) > 0:
        rates_df = pd.DataFrame(rates)
        rates_df['time'] = pd.to_datetime(rates_df['time'], unit='s')
        return rates_df
    else:
        print(f"No rates data found for {symbol} on timeframe {timeframe}.")
        return None


# Asynchronous function to predict signal for a given symbol and timeframe
async def async_predict_signal_for_timeframe(symbol, timeframe, model_path='lstm_model.h5'):
    rates = await async_get_rates(symbol, timeframe, 500)  # Fetching last 500 bars
    if rates is None or len(rates) == 0:
        return (timeframe, 'neutral', None)  # Include 'None' for price when data is unavailable

    df = pd.DataFrame(rates)
    data, scaler = scale_data(df['close'].values)
    sequences = create_sequences(data)

    model = load_model(model_path)
    predictions = model.predict(sequences)
    predictions = scaler.inverse_transform(predictions)

    signal = 'buy' if predictions[-1] > df['close'].iloc[-1] else 'sell'

    # Suggested price is the last close price from the data
    suggested_price = df['close'].iloc[-1]
    return (timeframe, signal, suggested_price)  # Return a tuple with timeframe, signal, and price
