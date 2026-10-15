"""Core multi-timeframe swing strategy signal generator."""
import pandas as pd
import numpy as np
from core.indicators import compute_indicators
import config

class SwingStrategy:
    def __init__(self):
        self.atr_mult = config.ATR_MULT
        self.rr_ratio = config.RR_RATIO
        self.adx_min = config.ADX_MIN
        self.min_stop_pct = config.MIN_STOP_PCT

    def evaluate(self, h_df, h4_df, d1_df):
        if len(h_df) < config.MIN_BARS or len(h4_df) < config.MIN_BARS or len(d1_df) < config.MIN_BARS:
            return {"signal": 0, "reason": "warming_up"}

        h_ind = compute_indicators(h_df)
        h4_ind = compute_indicators(h4_df)
        d1_ind = compute_indicators(d1_df)

        latest_h = h_ind.iloc[-1]
        latest_4h = h4_ind.iloc[-1]
        latest_d1 = d1_ind.iloc[-1]

        if latest_h['ADX'] < self.adx_min:
            return {"signal": 0, "reason": "low_adx"}

        d_long = latest_d1['EMA_20'] > latest_d1['EMA_50']
        f_long = latest_4h['EMA_20'] > latest_4h['EMA_50']
        r1, r4 = latest_h['RSI'], latest_4h['RSI']
        close, ema50 = latest_h['close'], latest_h['EMA_50']
        atr = latest_h['ATR']
        ep = latest_h['close']

        dd = self.atr_mult * atr
        stop_pct = (dd / ep) * 100

        if stop_pct < self.min_stop_pct:
            return {"signal": 0, "reason": "min_stop_filter_violated"}

        is_long = (d_long and not f_long and r4 < config.RSI_4H_OVERSOLD and r1 > 50) or \
                  (d_long and f_long and r1 < config.RSI_1H_PULLBACK_LONG and close > ema50)

        is_short = (not d_long and f_long and r4 > config.RSI_4H_OVERBOUGHT and r1 < 50) or \
                   (not d_long and not f_long and r1 > config.RSI_1H_PULLBACK_SHORT and close < ema50)

        if is_long:
            return {"signal": 1, "side": "LONG", "entry": ep, "sl": ep - dd, "tp": ep + (self.rr_ratio * dd), "stop_pct": stop_pct}
        elif is_short:
            return {"signal": -1, "side": "SHORT", "entry": ep, "sl": ep + dd, "tp": ep - (self.rr_ratio * dd), "stop_pct": stop_pct}

        return {"signal": 0, "reason": "no_setup"}
