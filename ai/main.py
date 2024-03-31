import asyncio
from analysis_ai_multiple_timeframes import train_lstm_model, predict_signal
from startup import initialize_mt5, get_balance, shutdown_mt5
import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime, timedelta
import os
from concurrent.futures import ThreadPoolExecutor


# Function to determine the list of symbols to analyze based on the current day of the week
def get_symbols_for_today():
    today = datetime.today().weekday()  # Monday is 0, Sunday is 6
    if today == 5 or today == 6:  # Saturday or Sunday
        return ['ETHUSD', 'BTCUSD']
    else:  # Monday to Friday
        return ['EURUSD', 'GBPUSD', 'NZDUSD', 'USDJPY']


def analyze_symbol(symbol, timeframe):
    model_path = f'{symbol}_{timeframe}_lstm_model.h5'

    # Initialize MT5 connection if not already initialized
    if not mt5.initialize():
        print("MT5 initialize() failed, error code =", mt5.last_error())
        return

    # Fetch the asking price for the symbol
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"Failed to get tick data for {symbol}.")
        mt5.shutdown()
        return
    last_price = tick.ask  # Corrected to use the asking price directly

    print(f"Last known asking price for {symbol}: {last_price}")

    if not os.path.exists(model_path):
        print(f"Model for {symbol} not found. Training a new model.")
        train_lstm_model(symbol, timeframe, pd.Timestamp.now() - pd.Timedelta(days=365), pd.Timestamp.now())

    signal = predict_signal(symbol, timeframe, model_path)
    print(f"Signal for {symbol} at timeframe {timeframe}: {signal}")

    # Shutdown MT5 connection
    mt5.shutdown()



async def main():
    if not initialize_mt5():
        return

    balance = get_balance()
    if balance is not None:
        print(f"Starting balance: {balance}")

    timeframe = mt5.TIMEFRAME_H1

    try:
        while True:
            symbols = get_symbols_for_today()
            for symbol in symbols:
                model_path = f'{symbol}_{timeframe}_lstm_model.h5'

                # It's assumed that you only train the model once and not in this loop.
                # If model training needs to be done regularly, consider adding logic for it as well.
                if not os.path.exists(model_path):
                    print(f"Model for {symbol} not found. Training a new model.")
                    # Assuming your train_lstm_model function saves the model at model_path
                    train_lstm_model(symbol, timeframe, pd.Timestamp.now() - pd.Timedelta(days=365), pd.Timestamp.now())

                # Predict signal
                with ThreadPoolExecutor(max_workers=len(symbols)) as executor:
                    # Submit all the tasks for execution
                    futures = [executor.submit(analyze_symbol, symbol, timeframe) for symbol in symbols]

                    # Optionally, wait for all futures to complete if you need to process their results
                    # for future in futures:
                    #     future.result()

                await asyncio.sleep(60)  # Adjust as needed

    finally:
        shutdown_mt5()


if __name__ == "__main__":
    asyncio.run(main())
