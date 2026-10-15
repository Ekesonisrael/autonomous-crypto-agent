"""True learning critic: analyzes historical trade performance to adapt weights."""
import json
import os
import config

class TradeCritic:
    def __init__(self):
        self.log_path = config.LOG_PATH

    def load_history(self):
        if not os.path.exists(self.log_path):
            return []
        try:
            with open(self.log_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def get_adaptive_weights(self):
        history = self.load_history()
        if len(history) < 3:
            return {"risk_multiplier": 1.0, "long_confidence_boost": 1.0, "short_confidence_boost": 1.0, "reason": "insufficient_data"}

        # Analyze rolling performance of the last 20 trades
        recent = history[-20:]
        longs = [t for t in recent if t.get('side') == 'LONG']
        shorts = [t for t in recent if t.get('side') == 'SHORT']

        def get_expectancy(trades):
            if not trades:
                return 0.5
            wins = sum(1 for t in trades if t.get('status') == 'WIN')
            return wins / len(trades)

        long_win_rate = get_expectancy(longs)
        short_win_rate = get_expectancy(shorts)

        # Dynamic learning adjustments
        long_boost = 1.2 if long_win_rate > 0.6 else (0.5 if long_win_rate < 0.3 else 1.0)
        short_boost = 1.2 if short_win_rate > 0.6 else (0.5 if short_win_rate < 0.3 else 1.0)

        # Global risk multiplier based on overall recent drawdowns or loss streaks
        consecutive_losses = 0
        for t in reversed(history):
            if t.get('status') == 'LOSS':
                consecutive_losses += 1
            else:
                break

        risk_mult = 0.5 if consecutive_losses >= 3 else 1.0

        return {
            "risk_multiplier": risk_mult,
            "long_confidence_boost": long_boost,
            "short_confidence_boost": short_boost,
            "reason": f"learned from {len(history)} past trades (L_win: {long_win_rate:.2f}, S_win: {short_win_rate:.2f})"
        }
