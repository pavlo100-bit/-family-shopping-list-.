import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, jsonify
import google.generativeai as genai

app = Flask(__name__)

print("\n" + "="*50)
print("🚀 FAMILY LIST - VERSION 20.0 - THE BIG RESET")
print("="*50 + "\n", flush=True)

ALLOWED_GROUP_ID = '120363425281087335@g.us'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ AI Ready", flush=True)
    except Exception as e:
        print(f"❌ AI Error: {e}", flush=True)

CATEGORY_ORDER = [
    'מוצרי חלב וביצים', 'בשר ודגים', 'מאפייה', 'פירות וירקות',
    'יבשים ושימורים', 'קפואים', 'חטיפים ומתוקים', 'משקאות', 
    'ניקיון ותחזוקה', 'פארם והיגיינה', 'כללי/אחר'
]

def init_db():
    conn = sqlite3.connect('shopping.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, status INTEGER)''')
    conn.commit()
    conn.close()

init_db()

def analyze_message(text):
    def fallback(t):
        parts = t.replace(' וגם ', ',').replace(' ו', ',').replace(';', ',').replace('\n', ',').split(',')
        return [{"name": p.strip(), "category": "כללי/אחר"} for p in parts if p.strip()]
    if not model: return fallback(text)
    try:
        prompt = f"Identify products. Split items. Categories: {CATEGORY_ORDER}. Return ONLY JSON: [{{'name': 'item', 'category': 'cat'}}]. Text: '{text}'"
        response = model.generate_content(prompt)
        raw = response.text.strip()
        if "
http://googleusercontent.com/immersive_entry_chip/0

### למה זה יעבוד הפעם?
1.  **CSS מקומי**: הכנסתי תגיות `<style>` בתוך הקובץ. גם אם שירות העיצוב (`Tailwind`) לא נטען בגלל חסימה או אינטרנט איטי, האתר עדיין יקבל את הפונטים הגדולים והצבעים.
2.  **רוחב 100%**: ביטלתי את כל מה שיכול היה לגרום לזה להיראות קטן.
3.  **פונטים ענקיים**: הגדרתי גדלים של `1.8rem` ו-`3rem` – זה ייראה ענק גם על מסך של טלוויזיה.

**תעדכן את שני הקבצים, תעשה רענון (Refresh) בדפדפן בנייד, ותגיד לי אם סוף סוף אנחנו רואים "אפליקציה" ולא "דף טקסט".** אגב, ה-AI יחזור לעבוד ברגע שנעדכן את ה-`main.py` התקין.
