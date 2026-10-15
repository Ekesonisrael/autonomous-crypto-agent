"""Main paper execution loop with live data fetching, strategy evaluation, and safety guards."""
import time
from datetime import datetime, timezone
from data.fetcher import load_symbol_data
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

    def run_cycle(self):
        print("\n" + "="*70)
        print(f" 🤖 RUNNING AGENT CYCLE AT {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("="*70)

        weights = self.critic.get_adaptive_weights()
        print(f"[Critic Meta-Layer] Risk Multiplier: {weights['risk_multiplier']} | Pause Shorts: {weights['pause_shorts']}")

        for symbol in config.SYMBOLS:
            try:
                # 1. Fetch real multi-timeframe candles using our data module
                h_df, h4_df, d1_df = load_symbol_data(symbol, days=60)
                
                # 2. Evaluate strategy signals
                result = self.strategy.evaluate(h_df, h4_df, d1_df)
                
                signal = result.get("signal", 0)
                reason = result.get("reason", "active")
                
                if signal != 0:
                    side = result.get("side")
                    # Check dynamic meta-rules from critic
                    if side == "SHORT" and weights["pause_shorts"]:
                        print(f"  ⚠️ {symbol}: SHORT signal generated, but paused by Critic layer.")
                        continue
                        
                    print(f"  ✅ SIGNAL DETECTED FOR {symbol}!")
                    print(f"     Side   : {side}")
                    print(f"     Entry  : ${result.get('entry'):,.2f}")
                    print(f"     Stop Loss : ${result.get('sl'):,.2f} ({result.get('stop_pct'):.2f}%)")
                    print(f"     Take Profit: ${result.get('tp'):,.2f}")
                else:
                    print(f"  ℹ️ {symbol}: No setup ({reason})")

            except Exception as e:
                print(f"  ❌ Error processing {symbol}: {e}")

    def run_loop(self):
        print("="*70)
        print(" 🚀 AUTONOMOUS PAPER TRADING AGENT INITIALIZED")
        print("="*70)
        
        while True:
            if self.is_halted:
                print("Bot is halted due to circuit breakers. Sleeping...")
                time.sleep(300)
                continue

            self.check_circuit_breakers()
            self.run_cycle()
            
            print("\nSleeping for 1 hour until next candle check...")
            time.sleep(3600)  # Poll hourly

if __name__ == "__main__":
    engine = PaperEngine()
    # To test a single cycle immediately instead of looping forever:
    engine.run_cycle()
