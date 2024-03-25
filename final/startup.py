# startup.py
import MetaTrader5 as mt5

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

if __name__ == "__main__":
    if initialize_mt5():
        get_balance()
        shutdown_mt5()
