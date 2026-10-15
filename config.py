"""Global configurations, thresholds, and risk bounds."""
import os

SYMBOLS = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'XRP/USDT:USDT', 'DOGE/USDT:USDT']

# Strategy Parameters (Validated in Backtest v3)
ATR_MULT = 1.5
RR_RATIO = 2.0
ADX_MIN = 20
RSI_4H_OVERSOLD = 35
RSI_4H_OVERBOUGHT = 65
RSI_1H_PULLBACK_LONG = 45
RSI_1H_PULLBACK_SHORT = 55
TIME_STOP_HOURS = 168
MIN_STOP_PCT = 1.5        # Minimum stop distance filter
MIN_BARS = 150            # Warm-up requirement

# Capital & Sizing
STARTING_BALANCE = 10_000.0
RISK_PER_TRADE = 0.01     # Fixed 1% dollar risk
LEVERAGE_CAP = 3.0

# Storage Paths
LOG_PATH = "trade_history.json"
CACHE_DIR = ".bt_cache"
