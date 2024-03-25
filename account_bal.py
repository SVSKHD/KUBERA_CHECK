import MetaTrader5 as mt5

def start_up():
    # Initialize connection to the MetaTrader 5 terminal
    if not mt5.initialize(login=212792645, server="OctaFX-Demo", password="pn^eNL4U"):
        raise Exception("Failed to initialize MT5 connection: Error code =", mt5.last_error())
    print("Connected successfully")

    # Retrieve account information
    account_info = mt5.account_info()
    if account_info is None:
        print("Failed to retrieve account information, error code =", mt5.last_error())
    else:
        # Print the account balance
        print(f"Account Balance: {account_info.balance}")

    # Shutdown the connection to the MetaTrader 5 terminal
    mt5.shutdown()

# Execute the function to get and print the account balance
start_up()
