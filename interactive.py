import requests
import os
import sys
import time
import json
import feedparser
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OFFSET_FILE = "bot_offset.json"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def load_offset():
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "r") as f:
            return json.load(f).get("offset", 0)
    return 0

def save_offset(offset):
    with open(OFFSET_FILE, "w") as f:
        json.dump({"offset": offset}, f)

def send_msg(chat_id, text):
    requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": chat_id, "text": text, "parse_mode": "HTML"
    })

def get_gold():
    try:
        res = requests.get(
            "https://query1.finance.yahoo.com/v8/finance/chart/GC=F",
            headers={"User-Agent": "Mozilla/5.0"}, timeout=10
        )
        data = res.json()
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        prev = data['chart']['result'][0]['meta']['chartPreviousClose']
        pct = ((price - prev) / prev) * 100
        arrow = "📈" if price > prev else "📉"
        return f"🥇 <b>سعر الذهب الآن:</b>\n{price:.2f} $ {arrow} ({pct:+.2f}%)"
    except:
        return "⚠️ تعذّر جلب سعر الذهب."

def get_news():
    try:
        feed = feedparser.parse("https://feeds.reuters.com/reuters/businessNews")
        msg = "📰 <b>آخر 3 أخبار:</b>\n\n"
        for e in feed.entries[:3]:
            msg += f"• {e.title}\n"
        return msg
    except:
        return "⚠️ تعذّر جلب الأخبار."

def get_analysis():
    try:
        client = genai.Client(api_key=API_KEY)
        feed = feedparser.parse("https://feeds.reuters.com/reuters/businessNews")
        news = "\n".join([e.title for e in feed.entries[:5]])
        prompt = (
            "بناءً على هذه الأخبار، قدم تحليلاً سريعاً للسوق:\n"
            f"{news}\n\n"
            "🤖 <b>تحليل AI للسوق:</b>\n\n"
            "• وضع السوق: [جملة]\n"
            "• الذهب: [توقع]\n"
            "• الأسهم: [توقع]\n"
            "• <b>التوصية:</b> [جملة واحدة]\n\n"
            "استخدم <b> للعناوين فقط. العربية فقط."
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", contents=prompt)
        return response.text
    except Exception as e:
        return f"⚠️ خطأ: {e}"

def handle(chat_id, text):
    cmd = text.strip().lower()
    if cmd in ["/gold", "/ذهب"]:
        send_msg(chat_id, get_gold())
    elif cmd in ["/news", "/اخبار"]:
        send_msg(chat_id, get_news())
    elif cmd in ["/analysis", "/تحليل"]:
        send_msg(chat_id, "⏳ جاري التحليل...")
        send_msg(chat_id, get_analysis())
    elif cmd in ["/start", "/help"]:
        send_msg(chat_id, (
            "👋 <b>الأوامر المتاحة:</b>\n\n"
            "/gold أو /ذهب — سعر الذهب الآن\n"
            "/news أو /اخبار — آخر 3 أخبار\n"
            "/analysis أو /تحليل — تحليل AI للسوق\n"
        ))

def run_interactive():
    print("--- Interactive Bot Started ---")
    if not BOT_TOKEN:
        sys.exit("❌ BOT_TOKEN مفقود.")

    offset = load_offset()

    while True:
        try:
            res = requests.get(f"{BASE_URL}/getUpdates",
                params={"offset": offset, "timeout": 30}, timeout=35)
            for update in res.json().get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                if chat_id and text:
                    print(f"📩 {chat_id}: {text}")
                    handle(chat_id, text)
            save_offset(offset)
        except Exception as e:
            print(f"⚠️ {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_interactive()
