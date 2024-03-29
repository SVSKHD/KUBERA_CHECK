import asyncio
import MetaTrader5 as mt5
from analysis_ai_multiple_timeframes import async_predict_signal_for_timeframe


async def analyze_symbol_timeframe(symbol, timeframe):
    # Path to your trained LSTM model
    model_path = 'lstm_model.h5'

    # Predict signal for the given symbol and timeframe
    timeframe, signal, suggested_price = await async_predict_signal_for_timeframe(symbol, timeframe, model_path)

    # Handle the case where there is no data (suggested_price is None)
    if suggested_price is not None:
        print(f"Signal for {symbol} at timeframe {timeframe}: {signal} with suggested price: {suggested_price}")
    else:
        print(f"No data available for {symbol} at timeframe {timeframe}.")


async def main():
    symbols = ['EURUSD', 'GBPUSD', 'USDJPY']  # Example symbols
    timeframes = [mt5.TIMEFRAME_M1, mt5.TIMEFRAME_M5, mt5.TIMEFRAME_H1]  # Example timeframes

    tasks = []
    for symbol in symbols:
        for timeframe in timeframes:
            # Create a task for each symbol-timeframe combination
            task = analyze_symbol_timeframe(symbol, timeframe)
            tasks.append(task)

    # Run all tasks concurrently
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
