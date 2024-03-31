# data_manager.py

import MetaTrader5 as mt5
import pandas as pd


def initialize_mt5():
    if not mt5.initialize(login=212792645, server="OctaFX-Demo", password="pn^eNL4U"):
        print("Failed to initialize MT5 connection: Error code =", mt5.last_error())
        return False
    else:
        print("Connected successfully")
        return True


def get_balance():
    account_info = mt5.account_info()
    if account_info is None:
        print("Failed to retrieve account information, error code =", mt5.last_error())
        return None
    else:
        print(f"Account Balance: {account_info.balance}")
        return account_info.balance


def shutdown_mt5():
    mt5.shutdown()
    print("MT5 connection shut down.")


def get_historical_data(symbol, timeframe, from_date, to_date):
    rates = mt5.copy_rates_range(symbol, timeframe, from_date, to_date)
    data = pd.DataFrame(rates)
    data['time'] = pd.to_datetime(data['time'], unit='s')
    return data


def preprocess_data(data):
    data['SMA'] = data['close'].rolling(window=5).mean()
    data.dropna(inplace=True)
    data['target'] = (data['close'].shift(-1) > data['close']).astype(int)
    return data[['SMA', 'target']].dropna()
