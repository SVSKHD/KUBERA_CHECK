import MetaTrader5 as mt5
import time

def connect_to_mt5(account, password, server):
    if not mt5.initialize(login=account, password=password, server=server):
        print("Failed to initialize MT5 connection. Error code =", mt5.last_error())
        mt5.shutdown()
        raise Exception("Could not initialize MT5 connection")
    else:
        print("Connected to MetaTrader 5.")

def trade_action(symbol, action, volume):
    trade_type = mt5.ORDER_TYPE_BUY if action == "buy" else mt5.ORDER_TYPE_SELL
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": trade_type,
        "price": mt5.symbol_info_tick(symbol).ask if action == "buy" else mt5.symbol_info_tick(symbol).bid,
        "magic": 0,
        "comment": "Test trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to execute {action} trade for {symbol}: {result}")
    else:
        print(f"{action.capitalize()} trade for {symbol} executed successfully with volume {volume}.")

def check_and_trade(symbol, volume):
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        print(f"Found {len(positions)} open positions for {symbol}. Closing...")
        for position in positions:
            trade_action(symbol, "sell" if position.type == mt5.ORDER_TYPE_BUY else "buy", volume)
    else:
        print(f"No open positions for {symbol}. Opening a BUY order.")
        trade_action(symbol, "buy", volume)

# Main
connect_to_mt5(account=212792645, password="pn^eNL4U", server="OctaFX-Demo")

try:
    while True:
        for symbol in ["BTCUSD", "ETHUSD"]:
            check_and_trade(symbol, volume=0.1)
        time.sleep(60)  # Check every 60 seconds
finally:
    mt5.shutdown()
    print("Disconnected from MetaTrader 5.")
