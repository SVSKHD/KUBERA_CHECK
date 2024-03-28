import MetaTrader5 as mt5
import time
from startup import initialize_mt5, get_balance, shutdown_mt5
from trade_action import close_opposite_trades, execute_trade, manage_trades_for_symbol
import analysis

SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY"]
TIMEFRAME = mt5.TIMEFRAME_H1  # Define your desired timeframe here, e.g., hourly


def analyze_and_trade(symbol, timeframe, initial_balance):
    print(f"Analyzing {symbol}...")
    market_decision = analysis.analyze_market(symbol, timeframe)  # Assume this returns 'buy', 'sell', or 'hold'

    if market_decision in ['buy', 'sell']:
        print(f"{market_decision.capitalize()} signal detected for {symbol}")
        trade_type = mt5.ORDER_TYPE_BUY if market_decision == 'buy' else mt5.ORDER_TYPE_SELL
        close_opposite_trades(symbol, trade_type)
        execute_trade(symbol, market_decision.upper())

    manage_trades_for_symbol(symbol, initial_balance)


def main_loop():
    if initialize_mt5():
        print("MT5 initialized successfully")
        initial_balance = get_balance()

        try:
            while True:
                threads = []
                for symbol in SYMBOLS:
                    t = threading.Thread(target=analyze_and_trade, args=(symbol, TIMEFRAME, initial_balance))
                    t.start()
                    threads.append(t)

                # Wait for all threads to complete
                for t in threads:
                    t.join()

                print("Sleeping for a bit...")
                time.sleep(60)  # Sleep for 1 minute before next analysis
        except KeyboardInterrupt:
            print("Stopping the trading bot...")
        finally:
            shutdown_mt5()
            print("MT5 shutdown successfully")


if __name__ == "__main__":
    main_loop()