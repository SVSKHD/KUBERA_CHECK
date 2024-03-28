import MetaTrader5 as mt5
import pandas as pd
from startup import initialize_mt5, get_balance, shutdown_mt5
from risk_management import manage_risk, close_all_trades
from trade_action import close_opposite_trades, execute_trade, manage_trades_for_symbol
import analysis
import time

# Specify the symbols and timeframes you are trading
SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY"]
TIMEFRAMES = [mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M10, mt5.TIMEFRAME_M30, mt5.TIMEFRAME_H1, mt5.TIMEFRAME_D1]

def main_loop():
    if initialize_mt5():
        initial_balance = get_balance()

        try:
            while True:
                for symbol in SYMBOLS:
                    # Fetch RSI and MACD data for the symbol across specified timeframes
                    rsi_results = analysis.get_rsi(symbol, TIMEFRAMES)
                    macd_results = analysis.get_macd(symbol, TIMEFRAMES)

                    for timeframe in TIMEFRAMES:
                        rsi_df = rsi_results.get(timeframe)
                        macd_df = macd_results.get(timeframe)

                        # Ensure we have the data for both RSI and MACD
                        if rsi_df is not None and macd_df is not None:
                            latest_rsi = rsi_df['RSI'].iloc[-1]
                            latest_macd = macd_df['MACD_12_26_9'].iloc[-1]
                            latest_macd_signal = macd_df['MACDs_12_26_9'].iloc[-1]

                            # RSI-based decision making
                            if latest_rsi > 70:
                                print(f"{symbol} is overbought on timeframe {timeframe}. Consider selling.")
                                close_opposite_trades(symbol, mt5.ORDER_TYPE_SELL)
                                execute_trade(symbol, "SELL")
                            elif latest_rsi < 30:
                                print(f"{symbol} is oversold on timeframe {timeframe}. Consider buying.")
                                close_opposite_trades(symbol, mt5.ORDER_TYPE_BUY)
                                execute_trade(symbol, "BUY")

                            # MACD-based decision making
                            if latest_macd > latest_macd_signal:
                                print(f"MACD crossover above signal line for {symbol} on timeframe {timeframe}. Consider buying.")
                                close_opposite_trades(symbol, mt5.ORDER_TYPE_BUY)
                                execute_trade(symbol, "BUY")
                            elif latest_macd < latest_macd_signal:
                                print(f"MACD crossover below signal line for {symbol} on timeframe {timeframe}. Consider selling.")
                                close_opposite_trades(symbol, mt5.ORDER_TYPE_SELL)
                                execute_trade(symbol, "SELL")

                    # Existing SMA-based decision logic here

                    # Managing open trades for each symbol
                    analysis.manage_open_trades(symbol, profit_pips=10)
                    manage_trades_for_symbol(symbol, initial_balance)

                print("Watching the market...")
                time.sleep(5)  # Adjust the frequency of checks as needed

        except KeyboardInterrupt:
            print("Stopping the market watch.")
        finally:
            shutdown_mt5()  # Ensure MT5 is properly shutdown when exiting

if __name__ == "__main__":
    main_loop()
