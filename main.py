import sys
from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
import json

# הדפסה שתופיע בראש הלוגים לווידוא שהעדכון עבר
print("\n" + "="*60, flush=True)
print("###  SUCCESS: FAMILY LIST VERSION 10.0 IS ONLINE      ###", flush=True)
print("="*60 + "\n", flush=True)

try:
    import google.generativeai as genai
    print("✅ AI Library Loaded", flush=True)
except ImportError:
    print("❌ Error: google-generativeai missing", flush=True)

app = Flask(__name__)

# הגדרות - וודא שה-API KEY נמצא ב-Variables ב-Railway
ALLOWED_GROUP_ID = '120363425281087335@g.us'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# אתחול ה-AI
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("🤖 Gemini AI Engine Ready", flush=True)
    except Exception as e:
        print(f"❌ AI Init Error: {e}", flush=True)

CATEGORY_ORDER = [
    'יבשים ושימורים', 'מוצרי חלב וביצים', 'בשר ודגים', 'פירות וירקות',
    'מאפייה', 'קפואים', 'חטיפים ומתוקים', 'משקאות', 'ניקיון ותחזוקה',
    'פארם והיגיינה', 'כללי/אחר'
]

def init_db():
    conn = sqlite3.connect('shopping.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, status INTEGER)''')
    conn.commit()
    conn.close()

init_db()

def analyze_message_logic(text):
    print(f"🔍 Analyzing: {text}", flush=True)
    if model:
        try:
            prompt = f"Identify shopping products in Hebrew. Split items by commas or 'and'. Clean prefixes like 'bring me'. Categories: {CATEGORY_ORDER}. Return JSON list: [{{'name': 'product', 'category': 'cat'}}]. Text: '{text}'"
            response = model.generate_content(prompt)
            raw = response.text.strip()
            if "
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

### מה לעשות עכשיו (בסדר הזה):
1. **GitHub:** תעדכן את שלושת הקבצים (אל תשכח את ה-Commit changes).
2. **Railway:** כנס ללשונית **Deployments**. חכה שהשורה העליונה תהפוך לירוקה (**Active**). אם היא נתקעת, לחץ על שלוש הנקודות ובצע **Redeploy**.
3. **בדיקה:** שלח הודעה בוואטסאפ: **"ורסק עגבניות, בננה, תפוח"**.

זה אמור לעבוד עכשיו חלק ולהיראות מעולה. תעדכן אותי אם הצלחת!
