# Daily Vocab

This repository automatically generates and publishes a new English vocabulary word every day. The goal is to provide a simple, consistent way to learn and expand one's vocabulary.

## How It Works

A GitHub Actions workflow is scheduled to run daily. This workflow executes the `generate.py` script, which performs the following steps:

1.  **Word Generation**: Calls the Groq API using the `llama-3.3-70b-versatile` model to generate a new vocabulary word. The response is a JSON object containing the word, its meaning, an example sentence, difficulty level, pronunciation, and a synonym.
2.  **Duplicate Check**: The script checks against `used_words.txt` to ensure the generated word has not been used before. If a duplicate is found, it retries until a unique word is generated.
3.  **File Creation**: A new markdown file for the word is created in the `words/` directory, named with the current date (e.g., `words/YYYY-MM-DD.md`).
4.  **Notification**: A formatted message with the new word is sent to a designated Telegram channel.
5.  **Commit**: The workflow commits the new word file and the updated `used_words.txt` back to the repository.

## Word Archive

You can browse the complete archive of daily words in the [`words/`](./words) directory. Each word is stored in a separate markdown file for easy access.

## Core Components

-   **`generate.py`**: The main Python script that orchestrates the word generation, file creation, and notification process. It uses the `openai` library to interact with the Groq API and `requests` to send Telegram messages.
-   **`.github/workflows/daily-word.yml`**: The GitHub Actions workflow that automates the daily execution of the `generate.py` script. It runs on a schedule (`cron`) and manages dependencies and environment secrets.
-   **`words/`**: A directory containing the archive of all vocabulary words generated, with each word saved as a separate markdown file.
-   **`used_words.txt`**: A simple text file that maintains a list of all previously generated words to prevent repetition.
