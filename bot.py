import os
import requests
from google import genai

def get_ai_summary(prompt):
    """استدعاء نموذج جيميناي للحصول على ملخص أو محتوى"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found!")
        return None

    client = genai.Client(api_key=api_key)
    
    try:
        # gemini-2.5-flash هو النموذج المستقر والمجاني المتاح حالياً
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def send_telegram_message(message):
    """إرسال النتيجة النهائية إلى تليجرام"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Error: Telegram credentials not found!")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Message sent to Telegram successfully!")
        else:
            print(f"Telegram Error: {response.text}")
    except Exception as e:
        print(f"Telegram Connection Error: {e}")

def main():
    prompt = "اعطني ملخصاً سريعاً لأهم 3 أخبار تقنية عالمية اليوم باللغة العربية مع روابط المصادر إن أمكن."
    
    print("Generating content with Gemini 2.5 Flash...")
    ai_content = get_ai_summary(prompt)
    
    if ai_content:
        final_message = f"🚀 *نشرة الذكاء الاصطناعي اليومية*:\n\n{ai_content}"
        send_telegram_message(final_message)
    else:
        print("Failed to generate content.")

if __name__ == "__main__":
    main()
    
    print("Generating content with Gemini 3.1 Flash...")
    ai_content = get_ai_summary(prompt)
    
    if ai_content:
        # إضافة عنوان جميل للمسج
        final_message = f"🚀 *نشرة الذكاء الاصطناعي اليومية*:\n\n{ai_content}"
        send_telegram_message(final_message)
    else:
        print("Failed to generate content.")

if __name__ == "__main__":
    main()
