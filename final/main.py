from startup import initialize_mt5, get_balance, shutdown_mt5
from risk_management import manage_risk, close_all_trades
from trade_action import close_opposite_trades, execute_trade
import analysis
import time


# Specify the symbols you are trading
SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY"]


def main_loop():
    if initialize_mt5():
        initial_balance = get_balance()

        try:
            while True:
                for symbol in SYMBOLS:
                    # Call analysis functions to detect market conditions for each symbol
                    volume_spike = analysis.detect_volume_change(symbol)
                    institutional_movement = analysis.detect_institutional_movement(symbol)

                    # Print price information and check pip differences for each symbol
                    analysis.print_price_info(symbol=symbol)

                    # Get SMA signals for the symbol
                    sma_signals_df = analysis.get_sma_signals(symbol, mt5.TIMEFRAME_H1)  # Adjust timeframe as needed
                    latest_signal = sma_signals_df['signal'].iloc[-1]  # Get the latest signal

                    # Decision-making based on SMA signals
                    if latest_signal == 1:
                        print(f"Buy signal detected for {symbol} based on SMA.")
                        close_opposite_trades(symbol, mt5.ORDER_TYPE_BUY)  # Close opposite trades if any
                        execute_trade(symbol, "BUY")  # Execute the new buy trade

                        # Example integration for a sell signal
                    elif latest_signal == -1:
                        print(f"Sell signal detected for {symbol} based on SMA.")
                        close_opposite_trades(symbol, mt5.ORDER_TYPE_SELL)  # Close opposite trades if any
                        execute_trade(symbol, "SELL")  # Execute the new sell trade

                    # Further decision-making based on volume and institutional movement
                    if volume_spike and institutional_movement:
                        print(f"Significant market activity detected for {symbol}.")
                        # Additional decisions to open trades based on analysis for the symbol

                    # Managing open trades for each symbol
                    analysis.manage_open_trades(symbol, profit_pips=10)

                print("Watching the market...")
                time.sleep(5)  # Adjust the frequency of checks as needed
        except KeyboardInterrupt:
            print("Stopping the market watch.")
        finally:
            shutdown_mt5()  # Ensure MT5 is properly shutdown when exiting


if __name__ == "__main__":
    main_loop()
