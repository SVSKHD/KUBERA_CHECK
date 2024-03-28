import MetaTrader5 as mt5


def execute_trade(symbol, direction, lot_size=0.01):
    symbol_info = mt5.symbol_info_tick(symbol)
    if symbol_info is None:
        print(f"Failed to get symbol info for {symbol}.")
        return False

    # Use the already retrieved symbol_info for the price
    price = symbol_info.ask if direction == "BUY" else symbol_info.bid

    # Define trade type based on direction
    trade_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL

    # Prepare the request dictionary
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": trade_type,
        "price": price,
        "comment": "Executed by bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    # Send a trading request
    result = mt5.order_send(request)

    # Check the result and print detailed error information if needed
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        error_code, error_description = mt5.last_error()
        print(f"Failed to execute trade for {symbol}. Error code: {error_code}, Description: {error_description}")
        return False

    # If the trade was successful, you might want to print some confirmation or return a success indicator
    print(f"Trade executed successfully for {symbol}, direction: {direction}, lot size: {lot_size}.")
    return True


def volume_calculated_based_on_risk_reward(symbol, balance, target_profit, stop_loss):
    # Assuming stop_loss is the risk percentage (e.g., 0.02 for 2%)
    risk_amount = balance * stop_loss  # Amount of money at risk based on the stop loss percentage

    # Determine the stop loss size in pips
    stop_loss_pips = 20  # Example value, adjust based on your strategy

    # Calculate the pip value for the symbol
    # This is a simplified example. Adjust the formula based on your account currency and the traded symbol
    pip_value = 10 / mt5.symbol_info(symbol).point  # $10 per pip for a standard lot in some pairs

    # Calculate the volume that matches the risk amount with the stop loss size
    volume = risk_amount / (stop_loss_pips * pip_value)

    # Adjust volume based on broker's restrictions
    symbol_info = mt5.symbol_info(symbol)
    volume = max(symbol_info.volume_min, min(volume, symbol_info.volume_max))
    volume_step = symbol_info.volume_step
    volume = (volume // volume_step) * volume_step  # Adjust volume to the nearest allowed step

    return volume


def manage_trades_for_symbol(symbol, initial_balance, loss_threshold=0.02, target_profit=0.05, stop_loss=0.02):
    # Calculate allowable loss in account currency
    max_loss_amount = initial_balance * loss_threshold

    # Fetch open positions for the symbol
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        print(f"No positions for {symbol}, error code =", mt5.last_error())
        return

    current_loss = sum(position.profit for position in positions if position.profit < 0)

    # Close all positions if losses exceed the threshold
    if abs(current_loss) > max_loss_amount:
        for position in positions:
            close_opposite_trades(symbol, position.type)

        # Define "BUY_OR_SELL" logic based on your strategy
        trade_direction = "BUY"  # or "SELL", as determined by your analysis

        # Calculate the required volume for the new trade
        volume = volume_calculated_based_on_risk_reward(symbol, initial_balance, target_profit, stop_loss)

        # Execute the new trade
        execute_trade(symbol, trade_direction, volume)


def place_trade(symbol, order_type, volume, stop_loss=None, take_profit=None, deviation=20):
    # Get current price for the symbol
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"{symbol} not found, can not call order_check()")
        mt5.shutdown()
        return

    if not symbol_info.visible:
        print(f"{symbol} is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            print(f"symbol_select({symbol}) failed, exit")
            mt5.shutdown()
            return

    point = symbol_info.point
    price = mt5.symbol_info_tick(symbol).ask if order_type == 'long' else mt5.symbol_info_tick(symbol).bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY if order_type == 'long' else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": price - 100 * point if stop_loss is None else stop_loss,
        "tp": price + 100 * point if take_profit is None else take_profit,
        "deviation": deviation,
        "magic": 0,
        "comment": "Placed by Python script",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    # Send the trade request
    result = mt5.order_send(request)
    return result


def close_opposite_trades(symbol, trade_type):
    # Retrieve information about open positions for a specific symbol
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        for position in positions:
            # Determine the opposite trade type
            opposite_type = mt5.ORDER_TYPE_BUY if position.type == mt5.ORDER_TYPE_SELL else mt5.ORDER_TYPE_SELL

            # Check if the current position is in the opposite direction of the intended trade
            if trade_type != position.type:
                # Prepare the request for closing the opposite position
                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": position.volume,
                    "type": opposite_type,
                    "position": position.ticket,
                    "magic": 0,
                    "comment": "Close opposite trade",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK,
                }
                # Send the trade request to close the position
                result = mt5.order_send(close_request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f"Failed to close opposite position {position.ticket}: {result}")
                else:
                    print(f"Opposite position {position.ticket} closed successfully.")

