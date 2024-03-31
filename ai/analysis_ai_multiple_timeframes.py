import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout

def scale_data(data):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data.reshape(-1, 1))
    return scaled_data, scaler

def create_sequences(data, look_back=60):
    sequences = []
    labels = []
    for i in range(len(data) - look_back - 1):
        sequences.append(data[i:(i + look_back), 0])
        labels.append(data[i + look_back, 0])
    return np.array(sequences), np.array(labels)

def get_rates_for_training(symbol, timeframe, start_date, end_date):
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        return None
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
    mt5.shutdown()
    if rates is not None and len(rates) > 0:
        rates_df = pd.DataFrame(rates)
        return rates_df['close'].values
    else:
        print(f"No rates data found for {symbol} on timeframe {timeframe}.")
        return None

def train_lstm_model(symbol, timeframe, start_date, end_date, look_back=60, epochs=10, batch_size=32):
    data = get_rates_for_training(symbol, timeframe, start_date, end_date)
    if data is not None:
        scaled_data, scaler = scale_data(data)
        sequences, labels = create_sequences(scaled_data, look_back)
        X = sequences.reshape((sequences.shape[0], sequences.shape[1], 1))
        y = labels

        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(X, y, epochs=epochs, batch_size=batch_size)
        model.save(f'{symbol}_{timeframe}_lstm_model.h5')
        return model
    else:
        print("Failed to fetch training data.")
        return None

def predict_signal(symbol, timeframe, model_path, look_back=60):
    rates = get_rates_for_training(symbol, timeframe, pd.Timestamp.now() - pd.Timedelta(days=look_back), pd.Timestamp.now())
    if rates is None:
        return 'none'

    scaled_data, scaler = scale_data(rates)
    sequences = create_sequences(scaled_data, look_back)[0][-1].reshape((1, look_back, 1))

    model = load_model(model_path)
    prediction = model.predict(sequences)
    predicted_price = scaler.inverse_transform(prediction)[0][0]
    last_known_price = rates[-1]

    if predicted_price > last_known_price:
        return 'buy'
    elif predicted_price < last_known_price:
        return 'sell'
    else:
        return 'none'
