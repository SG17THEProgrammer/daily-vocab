import os
import json
import logging
import requests
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# -------------------------
# LOGGING
# -------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# -------------------------
# GROQ CLIENT
# -------------------------

groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# -------------------------
# LLM WORD EXPLANATION
# -------------------------

def get_word_explanation(word: str) -> str:
    prompt = f"""
You are an English vocabulary coach. The user wants to learn about the word: "{word}"

Return ONLY valid JSON in this exact format, no markdown, no extra text:

{{
  "word": "",
  "meaning": "",
  "example": "",
  "antonym": [],
  "synonym": []
}}

Rules:
- Make the example sentence realistic and conversational.
- Provide atleast 3-4 synonyms and 3-4 antonyms as JSON arrays.
- Keep the meaning concise but complete.
- Always return valid JSON only.
"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    content = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    data = json.loads(content)
    return data


def format_explanation(data: dict) -> str:
    return (
        f"📘 *Word:* {data['word'].capitalize()}\n\n"
        f"📖 *Meaning:* {data['meaning']}\n\n"
        f"✏️ *Example:* {data['example']}\n\n"
        f"🔁 *Synonyms:* {', '.join(data['synonym'])}\n"
        f"🔃 *Antonyms:* {', '.join(data['antonym'])}"
    )


# -------------------------
# TELEGRAM HANDLER
# -------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    word = message.text.strip()

    # Only process single words (no spaces, no commands)
    if " " in word or word.startswith("/"):
        return

    chat_id = message.chat_id
    message_id = message.message_id

    # Delete the user's message
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logging.warning(f"Could not delete message: {e}")

    # Send a "looking up" placeholder
    placeholder = await context.bot.send_message(
        chat_id=chat_id,
        text=f"🔍 Looking up *{word}*...",
        parse_mode="Markdown"
    )

    try:
        data = get_word_explanation(word)
        reply = format_explanation(data)

        # Edit placeholder with actual explanation
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=placeholder.message_id,
            text=reply,
            parse_mode="Markdown"
        )

    except Exception as e:
        logging.error(f"Error getting explanation for '{word}': {e}")
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=placeholder.message_id,
            text=f"❌ Sorry, couldn't find an explanation for *{word}*. Please try again.",
            parse_mode="Markdown"
        )


# -------------------------
# MAIN
# -------------------------

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    app = Application.builder().token(token).build()

    # Handle all plain text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Bot is running... Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
