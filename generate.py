import os
import json
import requests
from datetime import date
from openai import OpenAI

# -------------------------
# GROQ CLIENT
# -------------------------

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# -------------------------
# TELEGRAM CONFIG
# -------------------------

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# -------------------------
# PROMPT
# -------------------------

prompt = """
You are an English vocabulary coach helping me improve my English day by day.

Every day, give me exactly ONE English vocabulary word. The word should vary in difficulty over time — sometimes beginner, sometimes intermediate, sometimes advanced — so I gradually build a strong vocabulary.

Requirements:
- Choose a different and useful word every day.
- Avoid repeating previously used words.
- Include:
  1. The word
  2. A simple and clear meaning
  3. One natural example sentence showing correct usage
  4. Difficulty level (Beginner / Intermediate / Advanced)
  5. A short pronunciation guide
  6. Optional synonym

The explanations should be easy to understand for someone improving their English through reading.

Return ONLY valid JSON in this exact format:

{
  "word": "",
  "meaning": "",
  "example": "",
  "difficulty": "",
  "pronunciation": "",
  "synonym": ""
}

Rules:
- Do not include markdown.
- Do not include extra text outside JSON.
- Keep meanings concise and beginner-friendly.
- Make example sentences realistic and conversational.
- Ensure the JSON is always valid.
"""

# -------------------------
# AI GENERATION
# -------------------------

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": prompt}
    ],
    temperature=1
)

content = response.choices[0].message.content

print(content)

data = json.loads(content)

word = data["word"]
meaning = data["meaning"]
example = data["example"]
difficulty = data["difficulty"]
pronunciation = data["pronunciation"]
synonym = data["synonym"]

# -------------------------
# CREATE MARKDOWN FILE
# -------------------------

today = str(date.today())

markdown = f"""# Word of the Day

## {word}

### Meaning
{meaning}

### Example
{example}

### Difficulty
{difficulty}

### Pronunciation
{pronunciation}

### Synonym
{synonym}
"""

# Create folder if missing
os.makedirs("words", exist_ok=True)

filename = f"words/{today}.md"

with open(filename, "w", encoding="utf-8") as f:
    f.write(markdown)

print(f"Created {filename}")

# -------------------------
# TELEGRAM MESSAGE
# -------------------------

message = f"""
📘 Word of the Day

🔤 {word}

📖 Meaning: {meaning}

✏️ Example: {example}

🛞 Difficulty : {difficulty}

🔈 Pronunciation : {pronunciation}

🧮 Synonym : {synonym}

"""

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": message
}

requests.post(url, data=payload)

print("Telegram message sent!")