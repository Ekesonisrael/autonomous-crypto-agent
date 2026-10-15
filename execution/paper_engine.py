"""Main paper execution loop with circuit breakers and logging safeguards."""
import time
from datetime import datetime, timezone
from core.strategy import SwingStrategy
from critic.memory import TradeCritic
import config

class PaperEngine:
    def __init__(self):
        self.strategy = SwingStrategy()
        self.critic = TradeCritic()
        self.balance = config.STARTING_BALANCE
        self.peak_balance = config.STARTING_BALANCE
        self.is_halted = False

    def check_circuit_breakers(self):
        if self.balance > self.peak_balance:
            self.peak_balance = self.balance
        drawdown = (self.peak_balance - self.balance) / self.peak_balance
        if drawdown >= 0.05:  # 5% max drawdown guardrail
            self.is_halted = True
            print(f"🚨 CIRCUIT BREAKER TRIGGERED: Drawdown {drawdown*100:.2f}% exceeds limit. Trading halted.")

    def run_loop(self):
        print("="*60)
        print(" 🚀 AUTONOMOUS PAPER TRADING AGENT INITIALIZED (v2 Clean Slate)")
        print("="*60)
        
        while True:
            if self.is_halted:
                print("Bot is halted due to circuit breakers. Sleeping...")
                time.sleep(300)
                continue

            self.check_circuit_breakers()
            weights = self.critic.get_adaptive_weights()
            
            print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC] "
                  f"Status: Active | Balance: ${self.balance:,.2f} | "
                  f"Risk Mult: {weights['risk_multiplier']} | Pause Shorts: {weights['pause_shorts']}")

            time.sleep(60)  # Polling interval placeholder

if __name__ == "__main__":
    engine = PaperEngine()
    engine.run_loop()
