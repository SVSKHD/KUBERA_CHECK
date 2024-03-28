import MetaTrader5 as mt5
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from startup import initialize_mt5, get_balance, shutdown_mt5
from trade_action import close_opposite_trades, execute_trade, manage_trades_for_symbol
import analysis  # Ensure this module contains the async_analyze_market function
from risk_management import close_all_trades, setup_risk_management

SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "NZDUSD"]
TIMEFRAMES = [mt5.TIMEFRAME_M15, mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4]



async def analyze_and_trade(symbol, timeframe, initial_balance):
    print(f"Analyzing {symbol} on {timeframe}...")
    market_decision = await analysis.async_analyze_market(symbol, timeframe)

    if market_decision in ['buy', 'sell']:
        print(f"{market_decision.capitalize()} signal detected for {symbol}")
        trade_type = mt5.ORDER_TYPE_BUY if market_decision == 'buy' else mt5.ORDER_TYPE_SELL
        close_opposite_trades(symbol, trade_type)
        execute_trade(symbol, market_decision.upper())

    manage_trades_for_symbol(symbol, initial_balance)


async def analyze_symbols(symbols, timeframes, initial_balance):
    tasks = []
    for symbol in symbols:
        for timeframe in timeframes:
            tasks.append(analyze_and_trade(symbol, timeframe, initial_balance))
    await asyncio.gather(*tasks)


def main_loop():
    if initialize_mt5():
        print("MT5 initialized successfully")
        initial_balance = get_balance()

        # Setup risk management parameters
        setup_risk_management(SYMBOLS, initial_balance)

        try:
            loop = asyncio.get_event_loop()
            while True:
                loop.run_until_complete(analyze_symbols(SYMBOLS, TIMEFRAMES, initial_balance))
                print("Sleeping for a bit...")
                time.sleep(1)  # Sleep for 1 minute before next analysis

                # Optionally, close all trades at the end of the trading day or on certain conditions
                # close_all_trades()

        except KeyboardInterrupt:
            print("Stopping the trading bot...")
            # Close all trades before shutting down
            close_all_trades()
        finally:
            shutdown_mt5()
            print("MT5 shutdown successfully")


if __name__ == "__main__":
    main_loop()
