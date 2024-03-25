# main.py
from startup import initialize_mt5, get_balance, shutdown_mt5
from risk_management import manage_risk, close_all_trades
import time


def main_loop():
    if initialize_mt5():
        initial_balance = get_balance()
        print(f"Initial Balance: {initial_balance}")

        try:
            while True:
                # Here you call manage_risk periodically to check if certain conditions are met
                manage_risk(target_profit=0.03, max_loss=0.02, initial_balance=initial_balance)

                print("Watching the market...")
                # Your market-watching logic goes here

                time.sleep(5)  # Adjust the frequency of checks as needed
        except KeyboardInterrupt:
            print("Stopping the market watch.")
        finally:
            shutdown_mt5()


if __name__ == "__main__":
    main_loop()
