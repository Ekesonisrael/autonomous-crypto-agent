"""Autonomous execution engine combining technicals, fundamentals, and critic learning."""
import time
from datetime import datetime, timezone
from data.fetcher import load_symbol_data, fetch_funding_rate, fetch_market_sentiment
from core.strategy import SwingStrategy
from critic.memory import TradeCritic
import config

class AutonomousAgentEngine:
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
        if drawdown >= 0.05:
            self.is_halted = True
            print(f"🚨 CIRCUIT BREAKER TRIGGERED: Drawdown {drawdown*100:.2f}% exceeds limit. Halting agent.")

    def run_cycle(self):
        print("\n" + "="*80)
        print(f" 🧠 AUTONOMOUS AGENT CYCLE | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("="*80)

        # 1. Fetch macro/fundamental intelligence
        sentiment = fetch_market_sentiment()
        weights = self.critic.get_adaptive_weights()
        print(f"[Macro Intelligence] Fear & Greed Index: {sentiment}/100")
        print(f"[Critic Memory] {weights['reason']} | Risk Mult: {weights['risk_multiplier']}")

        for symbol in config.SYMBOLS:
            try:
                # 2. Gather data & fundamentals
                h_df, h4_df, d1_df = load_symbol_data(symbol, days=60)
                funding_rate = fetch_funding_rate(symbol)
                
                # 3. Evaluate technical setup
                result = self.strategy.evaluate(h_df, h4_df, d1_df)
                signal = result.get("signal", 0)
                
                if signal != 0:
                    side = result.get("side")
                    
                    # 4. Autonomous filtering using fundamentals and learning memory
                    # Filter out longs if market is in extreme fear and funding is extremely negative, etc.
                    confidence_boost = weights["long_confidence_boost"] if side == "LONG" else weights["short_confidence_boost"]
                    
                    # Fundamental filter: Avoid going long if funding rate is heavily positive (over-leveraged longs paying shorts)
                    if side == "LONG" and funding_rate > 0.0005:
                        print(f"  ⚠️ {symbol}: Technical LONG signal, but blocked by Fundamental filter (High positive funding rate: {funding_rate:.5f})")
                        continue

                    if confidence_boost < 0.8:
                        print(f"  ⚠️ {symbol}: Technical {side} signal, but blocked by Critic Memory (Low historical expectancy).")
                        continue

                    print(f"  🚀 AUTONOMOUS TRADE DECISION APPROVED FOR {symbol}!")
                    print(f"     Side           : {side}")
                    print(f"     Entry Price    : ${result.get('entry'):,.2f}")
                    print(f"     Stop Loss      : ${result.get('sl'):,.2f} ({result.get('stop_pct'):.2f}%)")
                    print(f"     Take Profit    : ${result.get('tp'):,.2f}")
                    print(f"     Funding Rate   : {funding_rate:.5f}")
                else:
                    print(f"  ℹ️ {symbol}: No setup ({result.get('reason', 'flat')}) | Funding: {funding_rate:.5f}")

            except Exception as e:
                print(f"  ❌ Error processing {symbol}: {e}")

if __name__ == "__main__":
    agent = AutonomousAgentEngine()
    agent.run_cycle()
