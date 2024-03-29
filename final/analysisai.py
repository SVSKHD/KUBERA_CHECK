import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model


# Existing functions...

# LSTM-related functions

def scale_data(data):
    scaler = MinMaxScaler(feature_range=(0, 1))
    return scaler.fit_transform(data), scaler


def create_sequences(data, look_back=60):
    sequences = []
    for i in range(len(data) - look_back):
        sequences.append(data[i:(i + look_back)])
    return np.array(sequences)


async def async_predict_signal(symbol, timeframe, model_path='lstm_model.h5'):
    rates = await async_get_rates(symbol, timeframe, 500)  # Fetching last 500 bars
    if rates is None or len(rates) == 0:
        return 'neutral'

    df = pd.DataFrame(rates)
    # Assume 'Close' prices are used for prediction
    data, scaler = scale_data(df['close'].values.reshape(-1, 1))
    sequences = create_sequences(data)

    model = load_model(model_path)  # Load your pre-trained LSTM model
    predictions = model.predict(sequences)
    # Rescale predictions back to original price range
    predictions = scaler.inverse_transform(predictions)

    # Simple strategy: if last predicted price > last actual close price -> 'buy', else -> 'sell'
    signal = 'buy' if predictions[-1] > df['close'].iloc[-1] else 'sell'
    return signal




