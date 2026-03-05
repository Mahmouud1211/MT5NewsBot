import feedparser
import requests
import os
import google.generativeai as genai

# ==========================================
# 1. إعدادات المفاتيح (تُجلب من GitHub Secrets)
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ==========================================
# 2. مصادر الأخبار (RSS Feeds)
# ==========================================
RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://export.arxiv.org/rss/cs.AI" # أبحاث الذكاء الاصطناعي
]

def get_latest_news():
    news_items = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        # جلب أول خبرين من كل مصدر لتجنب الإطالة
        for entry in feed.entries[:2]:
            news_items.append({"title": entry.title, "link": entry.link, "summary": entry.get("summary", "")})
    return news_items

def summarize_news(news_items):
    genai.configure(api_key=GEMINI_API_KEY)
    # استخدام النموذج المجاني والسريع
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = "أنت محرر أخبار تقنية خبير. قم بتلخيص أخبار الذكاء الاصطناعي التالية باللغة العربية بطريقة جذابة ومختصرة تناسب قناة تيليجرام. استخدم النقاط (Bullet points) وأضف إيموجي مناسب. في النهاية ضع روابط المصادر.\n\nالأخبار:\n"
    for item in news_items:
        prompt += f"- العنوان: {item['title']}\n التفاصيل: {item['summary']}\n الرابط: {item['link']}\n\n"
        
    response = model.generate_content(prompt)
    return response.text

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("تم إرسال الملخص إلى تيليجرام بنجاح!")
    else:
        print(f"فشل الإرسال: {response.text}")

if __name__ == "__main__":
    print("جاري جلب الأخبار...")
    latest_news = get_latest_news()
    
    if latest_news:
        print("جاري التلخيص بواسطة AI...")
        arabic_summary = summarize_news(latest_news)
        
        print("جاري النشر...")
        send_to_telegram(arabic_summary)
    else:
        print("لا توجد أخبار جديدة.")
