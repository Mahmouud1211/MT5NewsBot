import feedparser
import requests
import os
import sys
import json
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
RSS_URL = "https://techcrunch.com/category/artificial-intelligence/feed/"
SENT_FILE = "sent_articles.json"

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent(sent):
    with open(SENT_FILE, "w") as f:
        json.dump(list(sent)[-100:], f)  # احتفظ بآخر 100 خبر فقط

def run_bot():
    print("--- Sniper Bot V8.0: Final Execution ---")
    
    if not all([API_KEY, BOT_TOKEN, CHAT_ID]):
        sys.exit("❌ خطأ: تأكد من إضافة الـ Secrets في GitHub.")

    print("Step 1: Fetching News...")
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        sys.exit("⚠️ لم يتم العثور على أخبار.")

    sent = load_sent()
    new_entries = [e for e in feed.entries if e.link not in sent]

    if not new_entries:
        print("✅ لا يوجد أخبار جديدة الآن.")
        sys.exit(0)

    # خذ أحدث 3 أخبار جديدة فقط
    news_text = ""
    for entry in new_entries[:3]:
        news_text += f"Title: {entry.title}\nDescription: {entry.summary[:300]}\n\n"

    print(f"Step 2: وُجد {len(new_entries[:3])} خبر جديد — جاري التلخيص...")
    try:
        client = genai.Client(api_key=API_KEY)
        
        prompt = (
            "أنت خبير محتوى تقني لمتداولي الأسهم والذهب في السعودية والأردن. "
            "لخص الأخبار التالية بالعربية بأسلوب نقاط مشوق مع إيموجي مناسب. "
            "استخدم <b>للعناوين</b> فقط، وبدون أي تنسيق آخر:\n\n"
            f"{news_text}"
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        
        summary = response.text
        if not summary:
            raise Exception("Empty AI response")
            
        print("✅ تم توليد الملخص بنجاح.")

        print("Step 3: Sending to Telegram...")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        res = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": summary,
            "parse_mode": "HTML"
        })
        
        if res.status_code == 200:
            # احفظ الأخبار المرسلة
            for entry in new_entries[:3]:
                sent.add(entry.link)
            save_sent(sent)
            print("💎 تمت العملية! تفقد قناتك الآن.")
        else:
            print(f"❌ خطأ تيليجرام: {res.text}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ خطأ فني: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
