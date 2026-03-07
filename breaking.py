import feedparser
import requests
import os
import sys
import json
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SENT_FILE = "sent_breaking.json"

BREAKING_KEYWORDS = [
    "breaking", "urgent", "alert", "crash", "surge", "plunge", "soars",
    "federal reserve", "fed rate", "rate hike", "rate cut", "inflation data",
    "cpi", "gdp", "jobs report", "war", "sanctions", "bank collapse",
    "bitcoin crash", "gold hits", "oil spike", "market crash", "black monday"
]

RSS_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://finance.yahoo.com/news/rssindex",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.marketwatch.com/rss/topstories",
]

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent(sent):
    with open(SENT_FILE, "w") as f:
        json.dump(list(sent)[-300:], f)

def is_breaking(entry):
    text = (entry.title + entry.get('summary', '')).lower()
    return any(k.lower() in text for k in BREAKING_KEYWORDS)

def run_breaking():
    print("--- Breaking News Monitor ---")
    if not all([API_KEY, BOT_TOKEN, CHAT_ID]):
        sys.exit("❌ Secrets مفقودة.")

    sent = load_sent()
    breaking_entries = []

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if entry.get('link') and entry.link not in sent and is_breaking(entry):
                    breaking_entries.append(entry)
        except Exception as e:
            print(f"⚠️ {url}: {e}")

    if not breaking_entries:
        print("✅ لا يوجد أخبار عاجلة.")
        sys.exit(0)

    print(f"🔴 وُجد {len(breaking_entries)} خبر عاجل!")

    for entry in breaking_entries[:3]:
        try:
            client = genai.Client(api_key=API_KEY)
            prompt = (
                "أنت محلل أسواق متخصص. هذا خبر عاجل — حلله بسرعة وبدقة:\n\n"
                f"العنوان: {entry.title}\n"
                f"التفاصيل: {entry.get('summary', '')[:500]}\n\n"
                "الصيغة المطلوبة:\n"
                "🔴 <b>عاجل: [عنوان الخبر]</b>\n\n"
                "📌 ما الذي حدث: [جملتان]\n\n"
                "💥 التأثير الفوري:\n"
                "   • الذهب: [صعود📈 / هبوط📉 / محايد➡️] — السبب\n"
                "   • الأسهم الأمريكية: [تأثير]\n"
                "   • الدولار: [تأثير]\n\n"
                "⚡ <b>قرار المتداول الآن:</b> [جملة واحدة حاسمة]\n\n"
                "استخدم <b> للعناوين فقط. اللغة العربية فقط."
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )

            msg = response.text
            if not msg:
                continue

            url_tg = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            res = requests.post(url_tg, json={
                "chat_id": CHAT_ID,
                "text": msg,
                "parse_mode": "HTML"
            })

            if res.status_code == 200:
                sent.add(entry.link)
                print(f"✅ أُرسل: {entry.title[:60]}")
            else:
                print(f"❌ تيليجرام: {res.text}")

        except Exception as e:
            print(f"❌ خطأ: {e}")

    save_sent(sent)

if __name__ == "__main__":
    run_breaking()
