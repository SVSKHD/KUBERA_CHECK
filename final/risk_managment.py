import MetaTrader5 as mt5
def close_all_trades():
    # Initialize connection to the MetaTrader 5 terminal
    if not mt5.initialize(login=212792645, server="OctaFX-Demo", password="pn^eNL4U"):
        raise Exception("Failed to initialize MT5 connection: Error code =", mt5.last_error())
    print("Connected successfully")

    # Retrieve information about all open positions
    positions = mt5.positions_get()
    if positions is None:
        print("No positions found, error code =", mt5.last_error())
    elif len(positions) > 0:
        for position in positions:
            symbol = position.symbol
            volume = position.volume
            position_id = position.ticket
            trade_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY

            # Prepare the request for closing the position
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": trade_type,
                "position": position_id,
                "magic": 0,
                "comment": "Closed by script",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }

            # Send the trade request
            result = mt5.order_send(close_request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Failed to close position {position_id}: {result}")
            else:
                print(f"Position {position_id} closed successfully.")



def manage_risk(target_profit, max_loss, initial_balance):
    current_balance = get_balance()
    profit_loss = current_balance - initial_balance

    # Check for 2% loss from initial balance
    if profit_loss <= -max_loss * initial_balance:
        print("2% loss threshold hit, closing all trades.")
        close_all_trades()
        # Insert logic to open new trades to cover the loss and aim for 3% profit

    # Check for 3% profit target
    elif profit_loss >= target_profit * initial_balance:
        print("Target profit reached for the day.")
        # Insert logic for actions after reaching target profit