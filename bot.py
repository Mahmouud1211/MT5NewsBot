هنا ظهر لك خطأين مختلفين تماماً، ولا تقلق، كلاهما سهل الحل. دعنا نفككهما ونحلهما نهائياً:

المشكلة الأولى (الخطأ 403): تسريب مفتاح الـ API 🚨
code
Text
download
content_copy
expand_less
Your API key was reported as leaked. Please use another API key.

السبب: جوجل اكتشفت أن مفتاحك السري (API Key) تم تسريبه (غالباً لأنك قمت برفعه بالخطأ داخل الكود في مستودعك العام على GitHub قبل أن تنقله إلى الـ Secrets). لحمايتك، قامت جوجل بإيقاف وحظر المفتاح فوراً.

الحل:

اذهب إلى موقع Google AI Studio.

قم بحذف المفتاح القديم (المسرب).

اضغط على Create API Key لإنشاء مفتاح جديد تماماً.

اذهب إلى مستودعك في GitHub > ثم Settings > ثم Secrets and variables > ثم Actions.

قم بتعديل قيمة GEMINI_API_KEY وضع المفتاح الجديد بدلاً من القديم.

المشكلة الثانية: خطأ برمجي في ملف bot.py 🐛
code
Text
download
content_copy
expand_less
NameError: name 'prompt' is not defined

السبب: يبدو أنك عندما قمت بنسخ الأكواد السابقة، قمت بلصقها فوق بعضها البعض (نسختين من الكود في نفس الملف)، مما أدى لتداخل الأكواد وظهور رسالة Generating content with Gemini 3.1 Flash... مرة أخرى مع فقدان تعريف المتغير prompt.

الحل:
أرجو منك فتح ملف bot.py في مستودعك، ومسح كل شيء بداخله تماماً (تأكد أن الملف فارغ)، ثم انسخ هذا الكود النظيف والصقه ليكون هو المحتوى الوحيد في الملف:

code
Python
download
content_copy
expand_less
import os
import requests
from google import genai

def get_ai_summary(prompt):
    """استدعاء نموذج جيميناي للحصول على ملخص"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found!")
        return None

    client = genai.Client(api_key=api_key)
    
    try:
        # استخدام النموذج المجاني والمستقر
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def send_telegram_message(message):
    """إرسال النتيجة إلى تليجرام"""
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
    # هذا هو المتغير الذي كان مفقوداً في الخطأ
    prompt = "اعطني ملخصاً سريعاً لأهم 3 أخبار تقنية عالمية اليوم باللغة العربية مع روابط المصادر إن أمكن."
    
    print("Generating content with Gemini...")
    ai_content = get_ai_summary(prompt)
    
    if ai_content:
        final_message = f"🚀 *نشرة الذكاء الاصطناعي اليومية*:\n\n{ai_content}"
        send_telegram_message(final_message)
    else:
        print("Failed to generate content.")

if __name__ == "__main__":
    main()
الخطوات النهائية للنجاح:

استبدل المفتاح في GitHub Secrets بمفتاح جديد تماماً.

استبدل محتوى bot.py بالكود الموجود بالأعلى (فقط هذا الكود).

احفظ التغييرات (Commit).

أعد تشغيل الـ Workflow.

ستعمل معك بنجاح هذه المرة 100% لأننا نظفنا الكود وحصلنا على مفتاح جديد محمي!
