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
You are an English vocabulary coach who will be helping me to improve my English day by day.

Generate exactly ONE English vocabulary word.

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
- Make example sentences realistic and conversational.
- Ensure the JSON is always valid.
"""

# -------------------------
# CHECK IF WORD ALREADY EXISTS OR NOT AND LOAD IN FILE IF NOT
# -------------------------

USED_WORDS_FILE = "used_words.txt"

def load_used_words():
    if not os.path.exists(USED_WORDS_FILE):
        return set()

    with open(USED_WORDS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip().lower() for line in f.readlines())

def save_word(word):
    with open(USED_WORDS_FILE, "a", encoding="utf-8") as f:
        f.write(word.lower() + "\n")

# -------------------------
# AI GENERATION
# -------------------------

used_words = load_used_words()

MAX_RETRIES = 20

data = None
messages =[
        {"role": "user", "content": prompt}
    ]

for attempt in range(MAX_RETRIES):

    if attempt > 0:
        messages.append({
        "role": "user",
        "content": f'The word "{word}" was already used. Generate a completely different word with all the other things'
    })
        
    response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages= messages,
    temperature=1
)
    
    content = response.choices[0].message.content

# print(content)
    try :
        data = json.loads(content)

        word = data["word"].strip().lower()
        meaning = data["meaning"]
        example = data["example"]
        difficulty = data["difficulty"]
        pronunciation = data["pronunciation"]
        synonym = data["synonym"]

        if word in used_words:
            # print(f"Duplicate word found: {word}")
            continue

        save_word(word)

        break

    except Exception as e:
        print("Error:", e)
        continue


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