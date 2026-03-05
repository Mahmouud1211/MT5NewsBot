import feedparser
import requests
import os
import sys
from google import genai

# جلب الإعدادات - تأكد أنها موجودة في Secrets بنفس الأسماء
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

RSS_URL = "https://techcrunch.com/category/artificial-intelligence/feed/"

def run_engine():
    print("--- Sniper Bot V4.0 Starting ---")
    
    if not GEMINI_KEY:
        sys.exit("❌ خطأ: GEMINI_API_KEY مفقود!")

    print("1. جلب الأخبار من المصدر...")
    feed = feedparser.parse(RSS_URL)
    content = ""
    for entry in feed.entries[:3]:
        content += f"Title: {entry.title}\nDescription: {entry.summary[:300]}\n\n"
    
    if not content:
        sys.exit("⚠️ لا توجد أخبار جديدة.")

    print("2. الاتصال بـ Gemini 1.5 Flash (النسخة المستقرة)...")
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        # استخدام gemini-1.5-flash حصراً لتجنب أخطاء 404 للنماذج التجريبية
        prompt = f"أنت محرر تقني. لخص الأخبار التالية لمتداولي MT5 بالعربية في نقاط مشوقة مع إيموجي:\n{content}"
        
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=prompt
        )
        summary = response.text
        print("✅ تم التلخيص بنجاح.")
        
        print("3. إرسال إلى تيليجرام...")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": summary, "parse_mode": "Markdown"}
        res = requests.post(url, json=payload)
        
        if res.status_code == 200:
            print("💎 تمت العملية بنجاح! تفقد القناة.")
        else:
            print(f"❌ خطأ تيليجرام: {res.text}")
            
    except Exception as e:
        print(f"❌ خطأ تقني: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_engine()