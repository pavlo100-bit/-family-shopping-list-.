import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, jsonify
import google.generativeai as genai

app = Flask(__name__)

print("\n" + "="*50)
print("🚀 FAMILY LIST - VERSION 24.0 - WEBHOOK & DESKTOP FIX")
print("="*50 + "\n", flush=True)

# --- הגדרות ---
ALLOWED_GROUP_ID = '120363425281087335@g.us'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# אתחול ה-AI
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ AI Engine Ready", flush=True)
    except Exception as e:
        print(f"❌ AI Init Error: {e}", flush=True)

CATEGORY_ORDER = [
    'מוצרי חלב וביצים', 'בשר ודגים', 'מאפייה', 'פירות וירקות',
    'יבשים ושימורים', 'קפואים', 'חטיפים ומתוקים', 'משקאות', 
    'ניקיון ותחזוקה', 'פארם והיגיינה', 'כללי/אחר'
]

def init_db():
    conn = sqlite3.connect('shopping.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT, category TEXT, status INTEGER)")
    conn.commit()
    conn.close()

init_db()

def analyze_message(text):
    print(f"🔍 Analyzing: {text}", flush=True)
    def fallback(t):
        parts = t.replace(' וגם ', ',').replace(' ו', ',').replace(';', ',').replace('\n', ',').split(',')
        return [{"name": p.strip(), "category": "כללי/אחר"} for p in parts if p.strip()]
    if not model: return fallback(text)
    try:
        prompt = f"Identify products in Hebrew. Categories: {CATEGORY_ORDER}. Return ONLY JSON list: [{{'name': 'product', 'category': 'category'}}]. Text: {text}"
        response = model.generate_content(prompt)
        raw = response.text.strip()
        if "
http://googleusercontent.com/immersive_entry_chip/0

### מה לעשות עכשיו (חשוב מאוד):
1. **עדכון קבצים:** תעדכן את שניהם בגיטהאב.
2. **בדיקת ה-URL:** כנס ל-Green API. וודא שהכתובת שם היא:
   `https://family-shopping-list-production.up.railway.app/webhook` (תבדוק שאין `/webhook/` כפול או שגיאת כתיב).
3. **בדיקת לוגים:** אחרי ששלחת הודעה, תסתכל ב-HTTP Logs ב-Railway. אם אתה רואה **200**, זה עובד! אם זה עדיין **404**, תשלח לי צילום מסך של הגדרות ה-Webhook ב-Green API.

תעדכן אותי אם אחרי העדכון הזה הוויזואלי במחשב סוף סוף הסתדר.
