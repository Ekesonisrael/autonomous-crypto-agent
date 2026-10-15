"""Data fetcher module for Binance Vision and OKX perpetuals."""
import io
import zipfile
import time
from datetime import datetime, timezone
import requests
import pandas as pd
import config

BINANCE_VISION_BASE = 'https://data.binance.vision'
OKX_BASE = 'https://www.okx.com'

def inst_id_of(symbol):
    """'BTC/USDT:USDT' -> 'BTC-USDT-SWAP'"""
    pair = symbol.split(':')[0]
    base, quote = pair.split('/')
    return f"{base}-{quote}-SWAP"

def fetch_candles_binance_vision(symbol, tf, start_ms, end_ms):
    """Download monthly CSV dumps from data.binance.vision (public, no auth)."""
    base = symbol.split('/')[0] + 'USDT'
    rows = []
    start_dt = datetime.fromtimestamp(start_ms / 1000, timezone.utc)
    end_dt = datetime.fromtimestamp(end_ms / 1000, timezone.utc)
    y, m = start_dt.year, start_dt.month

    while (y, m) <= (end_dt.year, end_dt.month):
        url = (f"{BINANCE_VISION_BASE}/data/futures/um/monthly/klines/"
               f"{base}/{tf}/{base}-{tf}-{y}-{m:02d}.zip")
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                z = zipfile.ZipFile(io.BytesIO(r.content))
                df = pd.read_csv(z.open(z.namelist()[0]), header=None, low_memory=False)
                try:
                    int(df.iloc[0, 0])
                except (ValueError, TypeError):
                    df = df.iloc[1:].reset_index(drop=True)
                df = df.iloc[:, :6]
                df.columns = ['ts', 'open', 'high', 'low', 'close', 'volume']
                for c in ['ts', 'open', 'high', 'low', 'close', 'volume']:
                    df[c] = pd.to_numeric(df[c], errors='coerce')
                df = df.dropna(subset=['ts'])
                df['ts'] = df['ts'].astype('int64')
                rows.append(df)
                time.sleep(0.02)
        except Exception:
            pass # Month might not exist or network hiccup; safely skipped

        if m == 12:
            y += 1
            m = 1
        else:
            m += 1

    if not rows:
        return pd.DataFrame(columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
    
    out = pd.concat(rows).drop_duplicates('ts').sort_values('ts').reset_index(drop=True)
    
    # Step duration mapping for trimming
    step_map = {'1h': 3600000, '4h': 14400000, '1d': 86400000}
    step = step_map.get(tf, 3600000)
    
    return out[(out['ts'] >= start_ms) & (out['ts'] + step <= end_ms)].reset_index(drop=True)

def load_symbol_data(symbol, days=30):
    """Convenience helper to load multi-timeframe frames for a symbol."""
    end_ms = int(time.time() * 1000) // 3600000 * 3600000
    start_ms = end_ms - int(days * 86400000)
    
    dfs = {}
    for tf in ('1d', '4h', '1h'):
        step_map = {'1h': 3600000, '4h': 14400000, '1d': 86400000}
        warm = int(config.MIN_BARS * step_map[tf] * 1.15)
        
        print(f"Fetching {tf} data for {symbol}...")
        df = fetch_candles_binance_vision(symbol, tf, start_ms - warm, end_ms)
        dfs[tf] = df
        
    return dfs['1h'], dfs['4h'], dfs['1d']
