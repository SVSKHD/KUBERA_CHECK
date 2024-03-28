import MetaTrader5 as mt5
import analysis
from startup import get_balance
from trade_action import close_opposite_trades , execute_trade
import asyncio

# Risk management settings
DAILY_LOSS_LIMIT = 0.02  # 2%
DAILY_PROFIT_TARGET = 0.05  # 5%
DAILY_PROFIT_TARGET_NO_LOSS = 0.07  # 7%

symbol_initial_balances = {}
symbol_max_loss = {}
symbol_profit_target = {}


def manage_trades_for_symbol(symbol, initial_balance):
    # Check for open positions for the symbol
    open_positions = mt5.positions_get(symbol=symbol)
    if open_positions is None:
        print("Failed to get positions for symbol:", symbol)
        return

    for position in open_positions:
        current_profit = position.profit
        # Example condition: close position if profit exceeds a certain percentage of the initial balance
        profit_target = initial_balance * 0.01  # For example, 1% of the initial balance

        if current_profit >= profit_target:
            print(f"Closing position {position.ticket} for {symbol} with profit: {current_profit}")
            close_position(position)
        # Add more conditions as needed, for example, to adjust stop losses or take profit levels


def close_position(position):
    # This function sends a request to close a position. This is a simplified example.
    close_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
        "position": position.ticket,
        "price": mt5.symbol_info_tick(
            position.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(position.symbol).ask,
        "magic": position.magic,
        "comment": "Closed by manage_trades_for_symbol",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    result = mt5.order_send(close_request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to close position {position.ticket}, error code: {result.retcode}")
    else:
        print(f"Successfully closed position {position.ticket}.")


async def analyze_and_trade(symbol, timeframe, initial_balance):
    current_balance = get_balance()  # Update this to fetch the current balance for the symbol if possible
    profit_loss = current_balance - symbol_initial_balances[symbol]

    # Check if the loss limit has been reached
    if profit_loss < 0 and abs(profit_loss) > symbol_max_loss[symbol]:
        print(f"{symbol}: Daily loss limit reached. Skipping trades.")
        return

    # Check if the profit target has been reached
    if profit_loss > symbol_profit_target[symbol]:
        print(f"{symbol}: Daily profit target reached. Skipping trades.")
        return

    print(f"Analyzing {symbol} on {timeframe}...")
    market_decision = await analysis.async_analyze_market(symbol, timeframe)  # Use the async version

    if market_decision in ['buy', 'sell']:
        print(f"{market_decision.capitalize()} signal detected for {symbol}")
        trade_type = mt5.ORDER_TYPE_BUY if market_decision == 'buy' else mt5.ORDER_TYPE_SELL
        close_opposite_trades(symbol, trade_type)
        execute_trade(symbol, market_decision.upper())

    manage_trades_for_symbol(symbol, initial_balance)


def setup_risk_management(symbols, initial_balances):
    for symbol in symbols:
        symbol_initial_balances[symbol] = initial_balances[symbol]
        symbol_max_loss[symbol] = initial_balances[symbol] * DAILY_LOSS_LIMIT
        symbol_profit_target[symbol] = initial_balances[symbol] * DAILY_PROFIT_TARGET


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
