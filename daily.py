import requests
import os
import sys
from datetime import datetime
from google import genai
import feedparser

API_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_market_data(symbol, name):
    try:
        res = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        data = res.json()
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        prev = data['chart']['result'][0]['meta']['chartPreviousClose']
        change = price - prev
        pct = (change / prev) * 100
        arrow = "📈" if change > 0 else "📉"
        return f"{name}: {price:.2f} {arrow} ({pct:+.2f}%)"
    except:
        return f"{name}: غير متاح"

def get_top_news():
    entries = []
    for url in ["https://feeds.reuters.com/reuters/businessNews",
                "https://finance.yahoo.com/news/rssindex"\]:
        try:
            feed = feedparser.parse(url)
            entries.extend(feed.entries[:5])
        except:
            pass
    return entries[:5]

def run_daily():
    print("--- Daily Report ---")
    if not all([API_KEY, BOT_TOKEN, CHAT_ID]):
        sys.exit("❌ Secrets مفقودة.")

    today = datetime.now().strftime("%A، %d %B %Y")
    gold = get_market_data("GC=F", "🥇 الذهب")
    nasdaq = get_market_data("^IXIC", "📊 Nasdaq")
    sp500 = get_market_data("^GSPC", "📊 S&P 500")
    oil = get_market_data("CL=F", "🛢️ النفط")

    entries = get_top_news()
    news_text = "\n".join([f"- {e.title}" for e in entries])

    try:
        client = genai.Client(api_key=API_KEY)
        prompt = (
            f"أنت محلل مالي كبير. اكتب تقرير نهاية يوم احترافي للمتداولين العرب.\n\n"
            f"الأسعار:\n{gold}\n{nasdaq}\n{sp500}\n{oil}\n\n"
            f"أبرز أخبار اليوم:\n{news_text}\n\n"
            f"اكتب التقرير بهذا الشكل:\n"
            f"📋 <b>تقرير نهاية اليوم — {today}</b>\n\n"
            f"📌 <b>ملخص السوق:</b> [فقرة قصيرة]\n\n"
            f"💹 <b>الأسعار الختامية:</b>\n[الأسعار منسقة]\n\n"
            f"🔑 <b>أبرز أحداث اليوم:</b>\n[3 نقاط]\n\n"
            f"🔭 <b>توقعات الغد:</b> [جملتان]\n\n"
            f"🎯 <b>توصية ختامية:</b> [جملة واحدة]\n\n"
            f"استخدم <b> للعناوين فقط. العربية فقط."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        res = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": response.text, "parse_mode": "HTML"}
        )

        if res.status_code == 200:
            print("✅ تم إرسال التقرير اليومي!")
        else:
            print(f"❌ تيليجرام: {res.text}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ خطأ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_daily()
