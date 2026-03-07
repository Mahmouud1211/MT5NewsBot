import feedparser
import requests
import os
import sys
import json
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SENT_FILE = "sent_articles.json"

RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://finance.yahoo.com/news/rssindex",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://www.marketwatch.com/rss/topstories",
]

KEYWORDS = [
    "gold", "ذهب", "market", "fed", "federal reserve", "nvidia", "apple",
    "microsoft", "google", "amazon", "meta", "oil", "inflation", "rate",
    "stock", "AI", "artificial intelligence", "bitcoin", "crypto", "dollar",
    "nasdaq", "s&p", "dow", "earnings", "gdp", "recession", "interest rate",
    "openai", "anthropic", "gemini", "tesla", "semiconductor", "chip"
]

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent(sent):
    with open(SENT_FILE, "w") as f:
        json.dump(list(sent)[-200:], f)

def fetch_news(sent):
    all_entries = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            all_entries.extend(feed.entries)
        except Exception as e:
            print(f"⚠️ فشل جلب: {url} — {e}")

    # رتّب حسب الأحدث
    all_entries.sort(key=lambda x: x.get('published_parsed') or (0,), reverse=True)

    # فلتر الأخبار المرسلة مسبقاً
    new_entries = [e for e in all_entries if e.get('link') and e.link not in sent]

    # فلتر حسب الكلمات المفتاحية
    filtered = [
        e for e in new_entries
        if any(k.lower() in (e.title + e.get('summary', '')).lower() for k in KEYWORDS)
    ]

    return filtered

def build_news_text(entries):
    news_text = ""
    for entry in entries[:5]:
        title = entry.title
        summary = entry.get('summary', '')[:400]
        source = entry.get('source', {}).get('title', 'Unknown')
        news_text += f"Source: {source}\nTitle: {title}\nSummary: {summary}\n\n"
    return news_text

def summarize_with_gemini(news_text):
    client = genai.Client(api_key=API_KEY)

    prompt = (
        "أنت محلل مالي وتقني متخصص لمتداولي الذهب والأسهم في السعودية والأردن.\n\n"
        "مهمتك تحليل الأخبار التالية وتقديمها بهذا الشكل الثابت:\n\n"
        "1️⃣ لكل خبر مهم:\n"
        "   • <b>عنوان الخبر</b> + إيموجي معبّر\n"
        "   • ملخص سريع بجملتين\n"
        "   • 📊 التأثير المتوقع: [صعود 📈 / هبوط 📉 / ترقب ⚠️] على الذهب أو الأسهم\n\n"
        "2️⃣ في النهاية:\n"
        "   <b>🎯 توصية المتداول اليوم:</b> جملة واحدة واضحة وعملية\n\n"
        "قواعد صارمة:\n"
        "- استخدم <b>للعناوين فقط</b>\n"
        "- لا تذكر أخباراً غير مؤثرة على الأسواق\n"
        "- الأسلوب: مباشر، واثق، احترافي\n"
        "- اللغة: العربية فقط\n\n"
        f"الأخبار:\n{news_text}"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    return response.text

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    })
    return res

def run_bot():
    print("--- Sniper Bot V9.0 ---")

    if not all([API_KEY, BOT_TOKEN, CHAT_ID]):
        sys.exit("❌ خطأ: تأكد من إضافة الـ Secrets في GitHub.")

    print("Step 1: جلب الأخبار من المصادر...")
    sent = load_sent()
    entries = fetch_news(sent)

    if not entries:
        print("✅ لا يوجد أخبار جديدة مؤثرة الآن.")
        sys.exit(0)

    print(f"Step 2: وُجد {len(entries)} خبر جديد — جاري التحليل...")
    news_text = build_news_text(entries)

    try:
        summary = summarize_with_gemini(news_text)
        if not summary:
            raise Exception("Empty AI response")
        print("✅ تم توليد التحليل بنجاح.")

        print("Step 3: الإرسال إلى تيليجرام...")
        res = send_to_telegram(summary)

        if res.status_code == 200:
            for entry in entries[:5]:
                sent.add(entry.link)
            save_sent(sent)
            print("💎 تمت العملية بنجاح!")
        else:
            print(f"❌ خطأ تيليجرام: {res.text}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ خطأ فني: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
