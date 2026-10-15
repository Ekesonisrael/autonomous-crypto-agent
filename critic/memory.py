"""Trade feedback loop and self-correcting meta-layer."""
import json
import os
import config

class TradeCritic:
    def __init__(self):
        self.log_path = config.LOG_PATH

    def log_trade(self, trade_dict):
        history = self.load_history()
        history.append(trade_dict)
        with open(self.log_path, "w") as f:
            json.dump(history, f, indent=2)

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
        if len(history) < 5:
            return {"risk_multiplier": 1.0, "pause_shorts": False, "pause_longs": False}

        recent = history[-10:]
        short_trades = [t for t in recent if t.get('side') == 'SHORT']
        
        # Pause shorts if they exhibit heavy underperformance recently
        pause_shorts = False
        if len(short_trades) >= 4:
            losses = sum(1 for t in short_trades if t.get('status') == 'LOSS')
            if (losses / len(short_trades)) >= 0.7:
                pause_shorts = True

        # Reduce risk multiplier if a consecutive loss streak hits
        consecutive_losses = 0
        for t in reversed(history):
            if t.get('status') == 'LOSS':
                consecutive_losses += 1
            else:
                break

        risk_mult = 0.5 if consecutive_losses >= 3 else 1.0

        return {
            "risk_multiplier": risk_mult,
            "pause_shorts": pause_shorts,
            "pause_longs": False
        }
