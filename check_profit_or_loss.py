import MetaTrader5 as mt5

def check_positions_profit_loss():
    # Initialize connection to the MetaTrader 5 terminal
    if not mt5.initialize(login=212792645, server="OctaFX-Demo", password="pn^eNL4U"):
        raise Exception("Failed to initialize MT5 connection: Error code =", mt5.last_error())
    print("Connected successfully")

    # Retrieve information about all open positions
    positions = mt5.positions_get()
    if positions is None:
        print("No positions found, error code =", mt5.last_error())
    elif len(positions) > 0:
        print("Checking positions for profit or loss...")
        for position in positions:
            symbol = position.symbol
            position_type = "BUY" if position.type == mt5.ORDER_TYPE_BUY else "SELL"
            open_price = position.price_open
            current_price = mt5.symbol_info_tick(symbol).ask if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
            profit_loss = "Profit" if ((position_type == "BUY" and current_price > open_price) or (position_type == "SELL" and current_price < open_price)) else "Loss"

            print(f"Position ID: {position.ticket}, Symbol: {symbol}, Type: {position_type}, Open Price: {open_price}, Current Price: {current_price}, Status: {profit_loss}")

    else:
        print("No open positions found.")

    # Shutdown the connection to the MetaTrader 5 terminal
    mt5.shutdown()

# Execute the function to check positions for profit or loss
check_positions_profit_loss()
