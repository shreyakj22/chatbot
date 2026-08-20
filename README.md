# Parampara – AI Local Culture Storytelling Bot

An AI-powered chatbot that generates culturally relevant, localized stories using context-aware conversational workflows — built to preserve and share local culture through storytelling.



## Features
- Context-aware conversation flow for natural, ongoing storytelling
- Generates culturally relevant, localized stories based on user input
- Built using NLP concepts to understand and respond to user prompts

## Tech Stack
- **Language:** Python
- **Core:** NLP (Natural Language Processing)
- **API:** Google (Generative AI)

## Getting Started

### Prerequisites
- Python installed (see `.python-version` for the exact version used)
- A Google API key (for the generative AI model)
- [uv](https://github.com/astral-sh/uv) package manager (or use `requirements.txt` with pip as an alternative)

### Setup

1. Clone the repo
   ```bash
   git clone https://github.com/shreyakj22/chatbot.git
   cd chatbot
   ```

2. Install dependencies

   Using uv (recommended, matches `uv.lock`):
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables
   Copy `.env.example` to `.env` and add your own Google API key:
   ```bash
   cp .env.example .env
   ```

4. Build the memory/vectorstore (run once before first use)
   ```bash
   python create_memory_for_llm.py
   ```

5. Run the bot
   ```bash
   python main.py
   ```

## How It Works
The bot takes a user's prompt or topic, maintains conversational context across the interaction, and generates a localized story shaped by cultural context rather than generic output.


## What I Built
Designed and built the chatbot's conversational logic in Python, using NLP concepts to keep responses context-aware and to shape output toward culturally relevant, localized storytelling.
