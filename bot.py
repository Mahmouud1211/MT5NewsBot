import feedparser
import requests
import os
import sys
from google import genai

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

RSS_SOURCES = ["https://techcrunch.com/category/artificial-intelligence/feed/"]

def fetch_and_summarize():
    if not GEMINI_KEY:
        sys.exit("❌ خطأ: مفتاح GEMINI_API_KEY مفقود!")
        
    print("جاري جلب الأخبار...")
    news_feed = ""
    for url in RSS_SOURCES:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:
            news_feed += f"Title: {entry.title}\nDescription: {entry.summary[:300]}\n\n"
    
    if not news_feed:
        sys.exit("لا توجد أخبار جديدة حالياً.")

    print("جاري الاتصال بـ Gemini...")
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        prompt = f"أنت محرر تقني. لخص الأخبار التالية لمتداولي MT5 بالعربية في نقاط قصيرة جداً مع إيموجي:\n{news_feed}"
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        return response.text
    except Exception as e:
        sys.exit(f"❌ خطأ من Gemini: {str(e)}")

def send_telegram(message):
    print("جاري النشر على تيليجرام...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"})
    if res.status_code == 200:
        print("✅ تم النشر بنجاح!")
    else:
        sys.exit(f"❌ خطأ من تيليجرام: {res.text}")

if __name__ == "__main__":
    summary = fetch_and_summarize()
    if summary:
        send_telegram(summary)
