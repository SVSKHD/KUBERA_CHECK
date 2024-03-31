# main.py

import pandas as pd
from data_manager import initialize_mt5, shutdown_mt5, get_historical_data, preprocess_data
from model import TradingModel
import MetaTrader5 as mt5

# Initialize and shutdown procedures for MT5
initialize_mt5()

# Retrieve and preprocess data
data = get_historical_data("EURUSD", mt5.TIMEFRAME_D1, pd.to_datetime('2020-01-01'), pd.to_datetime('2020-12-31'))
processed_data = preprocess_data(data)

# Separate features and target
X = processed_data[['SMA']]  # Features
y = processed_data['target']  # Target

# Initialize model and train
trading_model = TradingModel()
X_train, X_test, y_train, y_test = trading_model.split_data(X, y)
trading_model.train(X_train, y_train)

# Example prediction (replace with real-time data in a live setup)
predictions = trading_model.predict(X_test)

# Here, you could add your simulation of trading decisions based on predictions

shutdown_mt5()
