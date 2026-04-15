import sys
from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
import json
import google.generativeai as genai

# הגדרת האפליקציה עבור Gunicorn
app = Flask(__name__)

# סימן זיהוי גירסה בלוגים
print("\n" + "="*50)
print("🚀 FAMILY LIST - VERSION 15.0 - THE PERFECT EDITION")
print("="*50 + "\n", flush=True)

# --- הגדרות ---
ALLOWED_GROUP_ID = '120363425281087335@g.us'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# אתחול ה-AI
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini AI Engine Ready", flush=True)
    except Exception as e:
        print(f"❌ AI Init Error: {e}", flush=True)

# רשימת הקטגוריות הרשמית
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
    print(f"🔍 Analyzing: {text}", flush=True)

    def basic_parser(text):
        cleaned = text
        for phrase in ["תביא לי", "תביא", "צריך", "לקנות", "נא לקנות", "אפשר להוסיף", "רק"]:
            cleaned = cleaned.replace(phrase, "")
        cleaned = cleaned.replace(" וגם ", ",").replace(" ו", ",").replace(";", ",").replace("\n", ",")
        parts = cleaned.split(",")
        results = []
        for part in parts:
            name = part.strip(" .-")
            if name.startswith('ו') and len(name) > 3: name = name[1:]
            if name: results.append({"name": name, "category": "כללי/אחר"})
        return results

    if not model: return basic_parser(text)

    try:
        prompt = f"""
        Extract items from Hebrew shopping list.
        RULES:
        1. Split multiple items.
        2. Assign the most logical category from this list: {CATEGORY_ORDER}.
        3. Clean product names (e.g., 'רק עמק' -> 'גבינת עמק').
        4. Return ONLY a JSON array of objects.
        
        Text: {text}
        Format: [{{"name": "product", "category": "category"}}]
        """
        response = model.generate_content(prompt)
        raw = (response.text or "").strip()
        if "
