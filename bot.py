import feedparser
import requests
import os
import sys
from google import genai

# جلب الإعدادات
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

RSS_SOURCES = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"
]

def fetch_and_summarize():
    if not GEMINI_KEY:
        print("❌ خطأ: مفتاح GEMINI_API_KEY مفقود!")
        sys.exit(1)
        
    print("جاري جلب الأخبار...")
    news_feed = ""
    for url in RSS_SOURCES:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:
            news_feed += f"Title: {entry.title}\nDescription: {entry.summary[:300]}\n\n"
    
    if not news_feed:
        print("لا توجد أخبار جديدة حالياً.")
        sys.exit(0)

    print("جاري الاتصال بـ Gemini (النسخة الحديثة)...")
    try:
        # استخدام المكتبة الجديدة والنموذج المعتمد 2.0
        client = genai.Client(api_key=GEMINI_KEY)
        prompt = f"أنت محرر تقني. لخص الأخبار التالية لمتداولي MT5 بالعربية في نقاط قصيرة جداً مع إيموجي:\n{news_feed}"
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"❌ خطأ من Gemini: {str(e)}")
        sys.exit(1)

def send_telegram(message):
    try:
        print("جاري النشر على تيليجرام...")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        res = requests.post(url, json=payload)
        
        if res.status_code == 200:
            print("✅ تم النشر بنجاح!")
        else:
            print(f"❌ خطأ من تيليجرام: {res.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    summary = fetch_and_summarize()
    if summary:
        send_telegram(summary)
