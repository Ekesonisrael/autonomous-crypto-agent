"""Autonomous execution engine with Telegram alerts, fundamentals, and critic learning."""
import time
import os
import requests
from datetime import datetime, timezone
from data.fetcher import load_symbol_data, fetch_funding_rate, fetch_market_sentiment
from core.strategy import SwingStrategy
from critic.memory import TradeCritic
import config

def send_telegram_alert(message):
    """Send real-time alerts via Telegram Bot API."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

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
            msg = f"🚨 *CIRCUIT BREAKER TRIGGERED*: Drawdown {drawdown*100:.2f}% exceeds limit. Halting agent."
            print(msg)
            send_telegram_alert(msg)

    def run_cycle(self):
        print("\n" + "="*80)
        print(f" 🧠 AUTONOMOUS AGENT CYCLE | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("="*80)

        sentiment = fetch_market_sentiment()
        weights = self.critic.get_adaptive_weights()
        print(f"[Macro Intelligence] Fear & Greed Index: {sentiment}/100")
        print(f"[Critic Memory] {weights['reason']} | Risk Mult: {weights['risk_multiplier']}")

        for symbol in config.SYMBOLS:
            try:
                h_df, h4_df, d1_df = load_symbol_data(symbol, days=60)
                funding_rate = fetch_funding_rate(symbol)
                
                result = self.strategy.evaluate(h_df, h4_df, d1_df)
                signal = result.get("signal", 0)
                
                if signal != 0:
                    side = result.get("side")
                    confidence_boost = weights["long_confidence_boost"] if side == "LONG" else weights["short_confidence_boost"]
                    
                    if side == "LONG" and funding_rate > 0.0005:
                        print(f"  ⚠️ {symbol}: LONG signal blocked by Fundamental filter (High funding: {funding_rate:.5f})")
                        continue

                    if confidence_boost < 0.8:
                        print(f"  ⚠️ {symbol}: {side} signal blocked by Critic Memory (Low historical win rate).")
                        continue

                    alert_msg = (
                        f"🚀 *AUTONOMOUS TRADE SIGNAL* 🚀\n"
                        f"• *Symbol*: `{symbol}`\n"
                        f"• *Side*: `{side}`\n"
                        f"• *Entry*: `${result.get('entry'):,.2f}`\n"
                        f"• *Stop Loss*: `${result.get('sl'):,.2f}` ({result.get('stop_pct'):.2f}%)\n"
                        f"• *Take Profit*: `${result.get('tp'):,.2f}`\n"
                        f"• *Sentiment Index*: `{sentiment}/100`\n"
                        f"• *Funding Rate*: `{funding_rate:.5f}`"
                    )
                    print(f"  🚀 TRADE APPROVED FOR {symbol}! Sending Telegram notification...")
                    send_telegram_alert(alert_msg)
                else:
                    print(f"  ℹ️ {symbol}: No setup ({result.get('reason', 'flat')}) | Funding: {funding_rate:.5f}")

            except Exception as e:
                print(f"  ❌ Error processing {symbol}: {e}")

if __name__ == "__main__":
    agent = AutonomousAgentEngine()
    agent.run_cycle()
