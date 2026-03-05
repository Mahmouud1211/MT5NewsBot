import feedparser
import requests
import os
import sys
from google import genai

# 1. الإعدادات (وضعنا المفتاح الجديد هنا مباشرة لضمان العمل)
API_KEY = os.environ.get("GEMINI_API_KEY") or "AIzaSyCIbm1R7PjkoVFIrvx8MC_Woh1zzN3z4ow"
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

RSS_URL = "https://techcrunch.com/category/artificial-intelligence/feed/"

def run_bot():
    print("--- Starting Sniper Bot V6.0 (The Final Fix) ---")
    
    # 2. جلب الأخبار
    print("Step 1: Fetching News...")
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        print("No news found.")
        return

    news_text = ""
    for entry in feed.entries[:3]:
        news_text += f"Title: {entry.title}\nDescription: {entry.summary[:300]}\n\n"

    # 3. معالجة الذكاء الاصطناعي (المكتبة الجديدة)
    print("Step 2: Connecting to Gemini...")
    try:
        # ملاحظة: في النسخة الجديدة نستخدم genai.Client
        client = genai.Client(api_key=API_KEY)
        
        # تجربة gemini-1.5-flash مباشرة بالصيغة الصحيحة لعام 2026
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"لخص الأخبار التالية لمتداولي الأسهم والذهب بالعربية بأسلوب نقاط مشوق مع إيموجي:\n{news_text}"
        )
        
        summary = response.text
        print("✅ AI Summary Generated.")

        # 4. الإرسال لتليجرام
        print("Step 3: Sending to Telegram...")
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        res = requests.post(telegram_url, json={
            "chat_id": CHAT_ID,
            "text": summary,
            "parse_mode": "Markdown"
        })
        
        if res.status_code == 200:
            print("💎 SUCCESS: Message sent to your channel!")
        else:
            print(f"❌ Telegram Error: {res.text}")

    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")

if __name__ == "__main__":
    run_bot()
