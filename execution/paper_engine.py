"""Autonomous execution engine with Telegram alerts and direct Binance API."""
import time
import os
import requests
from datetime import datetime, timezone
import pandas as pd
import config

def send_telegram_alert(message):
    """Send real-time alerts via Telegram Bot API using GitHub secrets."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram credentials missing in environment variables.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload, timeout=5)
        if r.status_code == 200:
            print("Telegram alert sent successfully!")
        else:
            print(f"Telegram error: {r.text}")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def fetch_market_sentiment():
    try:
        r = requests.get("https://api.alternative.me/fng/", timeout=5)
        if r.status_code == 200:
            return int(r.json()['data'][0]['value'])
    except Exception:
        pass
    return 50

def fetch_funding_rate(symbol):
    pair = symbol.split(':')[0].replace('/', '')
    url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={pair}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return float(r.json().get('lastFundingRate', 0.0))
    except Exception:
        pass
    return 0.0

def fetch_klines(symbol, limit=50):
    pair = symbol.split(':')[0].replace('/', '')
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={pair}&interval=1h&limit={limit}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            df = pd.DataFrame(data, columns=['ts', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'q_val', 'trades', 't_base', 't_quote', 'ignore'])
            for c in ['open', 'high', 'low', 'close', 'volume']:
                df[c] = pd.to_numeric(df[c], errors='coerce')
            return df
    except Exception:
        pass
    return pd.DataFrame()

class AutonomousAgentEngine:
    def __init__(self):
        pass

    def run_cycle(self):
        print("\n" + "="*80)
        print(f" 🧠 CLOUD AUTONOMOUS AGENT CYCLE | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("="*80)

        sentiment = fetch_market_sentiment()
        print(f"[Macro Intelligence] Fear & Greed Index: {sentiment}/100")

        for symbol in config.SYMBOLS:
            try:
                df = fetch_klines(symbol)
                funding_rate = fetch_funding_rate(symbol)
                
                if len(df) < 10:
                    print(f"  ℹ️ {symbol}: Insufficient data | Funding: {funding_rate:.5f}")
                    continue

                price = df['close'].iloc[-1]
                
                # For testing cloud alerts, let's trigger a test alert notification on BTC to verify Telegram works!
                if symbol == "BTC/USDT:USDT":
                    alert_msg = (
                        f"🚀 *CLOUD AGENT TEST SIGNAL* 🚀\n"
                        f"• *Symbol*: `{symbol}`\n"
                        f"• *Side*: `LONG`\n"
                        f"• *Price*: `${price:,.2f}`\n"
                        f"• *Sentiment*: `{sentiment}/100`\n"
                        f"• *Funding*: `{funding_rate:.5f}`"
                    )
                    print(f"  🚀 Sending test Telegram alert for {symbol}...")
                    send_telegram_alert(alert_msg)
                else:
                    print(f"  ℹ️ {symbol}: Market scanned | Price: ${price:,.2f} | Funding: {funding_rate:.5f}")

            except Exception as e:
                print(f"  ❌ Error processing {symbol}: {e}")

if __name__ == "__main__":
    agent = AutonomousAgentEngine()
    agent.run_cycle()
