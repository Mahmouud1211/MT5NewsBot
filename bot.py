import feedparser
import requests
import os
import sys
from google import genai

# 1. جلب الإعدادات من GitHub Secrets
API_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

RSS_URL = "https://techcrunch.com/category/artificial-intelligence/feed/"

def run_bot():
    print("--- Sniper Bot V8.0: Final Execution ---")
    
    if not all([API_KEY, BOT_TOKEN, CHAT_ID]):
        sys.exit("❌ خطأ: تأكد من إضافة GEMINI_API_KEY و TELEGRAM_BOT_TOKEN و TELEGRAM_CHAT_ID في GitHub Secrets.")

    # 2. جلب الأخبار
    print("Step 1: Fetching News...")
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        sys.exit("⚠️ لم يتم العثور على أخبار جديدة.")

    news_text = ""
    for entry in feed.entries[:3]:
        news_text += f"Title: {entry.title}\nDescription: {entry.summary[:300]}\n\n"

    # 3. التلخيص باستخدام Gemini 2.0 Flash
    print("Step 2: Summarizing with Gemini 2.0 Flash...")
    try:
        client = genai.Client(api_key=API_KEY)
        
        prompt = (
            "أنت خبير محتوى تقني لمتداولي الأسهم والذهب في السعودية والأردن. "
            "لخص الأخبار التالية بالعربية بأسلوب نقاط (Bullet Points) مشوق مع إيموجي مناسب:\n\n"
            f"{news_text}"
        )
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )
        
        summary = response.text
        if not summary:
            raise Exception("Empty AI response")
            
        print("✅ تم توليد الملخص بنجاح.")

        # 4. الإرسال إلى تيليجرام
        print("Step 3: Sending to Telegram...")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        res = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": summary,
            "parse_mode": "Markdown"
        })
        
        if res.status_code == 200:
            print("💎 تمت العملية! تفقد قناتك الآن.")
        else:
            print(f"❌ خطأ تيليجرام: {res.text}")

    except Exception as e:
        error_msg = str(e)
        print(f"❌ خطأ فني: {error_msg}")
        if "403" in error_msg or "PERMISSION_DENIED" in error_msg:
            print("🚨 تنبيه عاجل: المفتاح الخاص بك تم حظره من جوجل لأنه نُشر في الدردشة. يجب استخراج مفتاح جديد.")
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
