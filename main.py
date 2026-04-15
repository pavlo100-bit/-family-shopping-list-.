def analyze_message(text):
    print(f"🔍 Analyzing: {text}", flush=True)

    def basic_parser(text):
        cleaned = text
        for phrase in ["תביא לי", "תביא", "צריך", "לקנות", "נא לקנות", "אפשר להוסיף"]:
            cleaned = cleaned.replace(phrase, "")

        cleaned = cleaned.replace(" וגם ", ",")
        cleaned = cleaned.replace(" ו", ",")
        cleaned = cleaned.replace(";", ",")
        cleaned = cleaned.replace("\n", ",")

        parts = cleaned.split(",")
        results = []

        for part in parts:
            name = part.strip(" .-")
            if name:
                results.append({
                    "name": name,
                    "category": "כללי/אחר"
                })

        return results

    if not model:
        print("⚠️ Gemini model not available, using fallback parser", flush=True)
        return basic_parser(text)

    try:
        prompt = f"""
You are an assistant that extracts shopping list items from Hebrew text.

Rules:
1. Return ONLY valid JSON.
2. No markdown.
3. No explanation text.
4. Output must be a JSON array.
5. Each item must have:
   - "name"
   - "category"
6. Category must be one of:
{json.dumps(CATEGORY_ORDER, ensure_ascii=False)}

Example output:
[
  {{"name": "חלב", "category": "מוצרי חלב וביצים"}},
  {{"name": "עגבניות", "category": "פירות וירקות"}}
]

Text:
{text}
"""

        response = model.generate_content(prompt)
        raw = (response.text or "").strip()

        if not raw:
            raise ValueError("Empty response from Gemini")

        print(f"🤖 Gemini raw response: {raw}", flush=True)

        if raw.startswith("```json"):
            raw = raw.replace("```json", "").replace("```", "").strip()
        elif raw.startswith("```"):
            raw = raw.replace("```", "").strip()

        items = json.loads(raw)

        if not isinstance(items, list):
            raise ValueError("Gemini response is not a list")

        seen = set()
        clean_items = []

        for item in items:
            if not isinstance(item, dict):
                continue

            name = str(item.get("name", "")).strip()
            category = str(item.get("category", "כללי/אחר")).strip()

            if not name:
                continue

            if category not in CATEGORY_ORDER:
                category = "כללי/אחר"

            key = (name, category)
            if key in seen:
                continue
            seen.add(key)

            clean_items.append({
                "name": name,
                "category": category
            })

        if not clean_items:
            print("⚠️ No valid items after cleanup, using fallback parser", flush=True)
            return basic_parser(text)

        return clean_items

    except Exception as e:
        print(f"❌ Analyze error: {e}", flush=True)
        return basic_parser(text)
