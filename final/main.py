import MetaTrader5 as mt5
import pandas as pd
import time
from startup import initialize_mt5, get_balance, shutdown_mt5
from risk_management import manage_risk, close_all_trades
from trade_action import close_opposite_trades, execute_trade, manage_trades_for_symbol
import analysis

SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY"]

def main_loop():
    if initialize_mt5():
        print("MT5 initialized successfully")
        initial_balance = get_balance()
        print(f"Initial Balance: {initial_balance}")

        try:
            while True:
                for symbol in SYMBOLS:
                    print(f"Analyzing {symbol}...")
                    market_decision = analysis.analyze_market(symbol)  # This should return 'buy', 'sell', or 'hold'

                    if market_decision in ['buy', 'sell']:
                        print(f"{market_decision.capitalize()} signal detected for {symbol}")

                        # Close opposite trades if any
                        if market_decision == 'buy':
                            close_opposite_trades(symbol, mt5.ORDER_TYPE_SELL)
                        else:
                            close_opposite_trades(symbol, mt5.ORDER_TYPE_BUY)

                        # Execute trade
                        execute_trade(symbol, market_decision.upper())

                    # Manage open trades for the symbol
                    manage_trades_for_symbol(symbol, initial_balance)

                print("Sleeping for a bit...")
                time.sleep(60)  # Sleep for 1 minute before next analysis
        except KeyboardInterrupt:
            print("Stopping the trading bot...")
        finally:
            shutdown_mt5()
            print("MT5 shutdown successfully")

if __name__ == "__main__":
    main_loop()
