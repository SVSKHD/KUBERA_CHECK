# main.py
from startup import initialize_mt5, get_balance, shutdown_mt5
import time


def main_loop():
    # Initialize MT5 connection
    if initialize_mt5():
        # Print the account balance
        get_balance()

        # Market watch loop
        try:
            while True:
                print("Watching the market...")
                # Here you would add your market-watching logic.
                # For example, check for new price updates, etc.

                time.sleep(5)  # Pause for 5 seconds before the next check.
        except KeyboardInterrupt:
            print("Stopping the market watch.")
        finally:
            shutdown_mt5()


if __name__ == "__main__":
    main_loop()
