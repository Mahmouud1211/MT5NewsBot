import feedparser
import requests
import os
import sys
from google import genai

# جلب الإعدادات من الأسرار
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# مصادر الأخبار
RSS_SOURCES = ["https://techcrunch.com/category/artificial-intelligence/feed/"]

def fetch_and_summarize():
    if not GEMINI_KEY:
        sys.exit("❌ خطأ: GEMINI_API_KEY مفقود!")
        
    print("جاري جلب الأخبار...")
    news_feed = ""
    try:
        for url in RSS_SOURCES:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                news_feed += f"Title: {entry.title}\nDescription: {entry.summary[:300]}\n\n"
    except Exception as e:
        sys.exit(f"❌ خطأ في جلب RSS: {str(e)}")
    
    if not news_feed:
        sys.exit("لا توجد أخبار جديدة.")

    print("جاري الاتصال بـ Gemini (النسخة المستقرة)...")
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        prompt = f"أنت محرر تقني. لخص الأخبار التالية لمتداولي MT5 بالعربية في نقاط قصيرة جداً مع إيموجي:\n{news_feed}"
        
        # تغيير النموذج إلى النسخة المستقرة المضمونة
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=prompt
        )
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
