"""Mathematical indicator calculations (Wilder smoothing, RSI, ATR, ADX)."""
import pandas as pd
import numpy as np

def compute_indicators(df, n=14, use_wilder=True):
    df = df.copy()
    c, h, l = df['close'], df['high'], df['low']
    delta = c.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    
    if use_wilder:
        avg_gain = gain.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
        avg_loss = loss.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    else:
        avg_gain = gain.rolling(n).mean()
        avg_loss = loss.rolling(n).mean()
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    df['RSI'] = rsi.where(~((avg_loss == 0) & (avg_gain > 0)), 100.0)
    
    df['EMA_20'] = c.ewm(span=20, adjust=False).mean()
    df['EMA_50'] = c.ewm(span=50, adjust=False).mean()
    
    prev_c = c.shift()
    tr = pd.concat([h - l, (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    df['ATR'] = tr.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean() if use_wilder else tr.rolling(n).mean()
    
    up, dn = h.diff(), -l.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=df.index)
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=df.index)
    
    pdi = 100 * (pdm.ewm(alpha=1.0/n, adjust=False).mean() if use_wilder else pdm.rolling(n).mean()) / df['ATR']
    mdi = 100 * (mdm.ewm(alpha=1.0/n, adjust=False).mean() if use_wilder else mdm.rolling(n).mean()) / df['ATR']
    
    denom = (pdi + mdi).replace(0, np.nan)
    dx = 100 * (pdi - mdi).abs() / denom
    df['ADX'] = dx.ewm(alpha=1.0/n, adjust=False).mean() if use_wilder else dx.rolling(n).mean()
    
    return df
