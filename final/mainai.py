import asyncio
import MetaTrader5 as mt5
from analysisai import async_analyze_market_with_ai

async def main():
    signal=await async_analyze_market_with_ai('EURUSD', mt5.TIMEFRAME_H1)
    print(f"Trading signal for EURUSD: {signal}")


if __name__ == "__main__":
    asyncio.run(main())