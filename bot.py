import feedparser
import requests
import os
import sys
import time
from email.utils import parsedate_to_datetime
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://finance.yahoo.com/news/rssindex",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://www.marketwatch.com/rss/topstories",
]

KEYWORDS = [
    "gold","market","fed","federal reserve","nvidia","apple","microsoft",
    "google","amazon","meta","oil","inflation","rate","stock","AI",
    "artificial intelligence","bitcoin","crypto","dollar","nasdaq","s&p",
    "dow","earnings","gdp","recession","interest rate","openai","anthropic",
    "gemini","tesla","semiconductor","chip","war","sanctions","opec",
    "crude","palantir","iran","ukraine"
]

def fetch_news():
    jordan_hour = (time.gmtime().tm_hour + 3) % 24
    if jordan_hour >= 20 or jordan_hour < 10:
        print(f"ساعة الصمت ({jordan_hour}:00) لا ارسال.")
        return []
    six_hours_ago = time.time() - (6 * 60 * 60)
    all_entries = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            all_entries.extend(feed.entries)
        except Exception as e:
            print(f"warning: {url} - {e}")
    recent = []
    for e in all_entries:
        try:
            pub = parsedate_to_datetime(e.get("published","")).timestamp()
            if pub > six_hours_ago:
                recent.append(e)
        except:
            pass
    filtered = [e for e in recent if any(k.lower() in (e.title + e.get("summary","")).lower() for k in KEYWORDS)]
    seen_titles = set()
    unique = []
    for e in filtered:
        title_key = e.title[:50].lower().strip()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique.append(e)
    return unique

def build_news_text(entries):
    news_text = ""
    for entry in entries[:5]:
        title = entry.title
        summary = entry.get("summary","")[:400]
        source = entry.get("source",{}).get("title","")
        news_text += f"Source: {source}\nTitle: {title}\nSummary: {summary}\n\n"
    return news_text

def run_bot():
    print("--- Sniper Bot V10.0 ---")
    if not all([API_KEY, BOT_TOKEN, CHAT_ID]):
        sys.exit("Error: Secrets missing.")
    print("Step 1: جلب الاخبار...")
    entries = fetch_news()
    if not entries:
        print("لا يوجد اخبار - انهاء.")
        sys.exit(0)
    print(f"Step 2: وجد {len(entries)} خبر - جاري التحليل...")
    news_text = build_news_text(entries)
    try:
        client = genai.Client(api_key=API_KEY)
        prompt = (
            "انت محلل مالي وتقني متخصص لمتداولي الذهب والاسهم في السعودية والاردن.\n\n"
            "مهمتك تحليل الاخبار التالية وتقديمها بهذا الشكل الثابت:\n\n"
            "لكل خبر مهم:\n"
            "   <b>عنوان الخبر</b> + ايموجي معبر\n"
            "   ملخص سريع بجملتين\n"
            "   التاثير المتوقع: [صعود / هبوط / ترقب] على الذهب او الاسهم\n\n"
            "في النهاية:\n"
            "   <b>توصية المتداول اليوم:</b> جملة واحدة واضحة وعملية\n\n"
            "قواعد:\n"
            "- استخدم <b> للعناوين فقط\n"
            "- لا تذكر اخبارا غير مؤثرة على الاسواق\n"
            "- العربية فقط\n\n"
            f"الاخبار:\n{news_text}"
        )
        response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
        summary = response.text
        if not summary:
            raise Exception("Empty AI response")
        print("Step 3: الارسال...")
        res = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": summary, "parse_mode": "HTML"}
        )
        if res.status_code == 200:
            print("Done!")
        else:
            print(f"Telegram error: {res.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_bot()
