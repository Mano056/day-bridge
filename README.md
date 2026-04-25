# Day-bridge

A lightweight Python CLI assistant that connects **Notion**, **Gmail**, and **LLM-powered chat** in one place.

Day-bridge helps you:

- search your Notion workspace
- create new Notion pages
- read and summarize recent Gmail messages
- send emails through Gmail
- chat naturally when the request is not a Notion or Gmail action

---

## Overview

Day-bridge is a command-line assistant that uses an LLM to classify user requests, extract structured details, call the right helper functions, and generate a final response.

It is designed as a practical personal workflow tool: simple, modular, and easy to extend.

## Features

- Notion search
- Notion page creation
- Gmail inbox reading and summarization
- Gmail email sending
- Local conversation memory
- Structured JSON classification and extraction
- Modular helper architecture

## Project Structure

```text
Day-bridge/
├── daybridge.py
├── google_func.py
├── notion_func.py
├── memory_store.py
├── multi_agent.py
├── credentials.json      # local only
├── token.json            # local only
├── memory.json           # local only
└── .env                  # local only
```

## Tech Stack
- Python
- Groq API
- Notion API
- Gmail API
- python-dotenv
- requests

## Getting Started 

### 1. Clone Repo
```bash
git clone https://github.com/Mano056/day-bridge.git
cd day-bridge
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
```

PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install python-dotenv requests groq google-auth google-auth-oauthlib google-api-python-client
```

### 4. Create a .env file
```.env
GROQ_API_KEY=your_groq_api_key
NOTION_ACCESS_TOKEN=your_notion_access_token
NOTION_PAGE_ID=your_notion_parent_page_id
```

## Gmail Setup
To enable Gmail features:

1. Create a Google Cloud OAuth client.
2. Place the downloaded OAuth file in the project root as `credentials.json`.
3. Run the app and complete the browser authentication flow.
4. A `token.json` file will be created automatically for future sessions.

## Usage
Run the app:
```bash:
python day-bridge.py
```
Example prompts:
```text
Search Notion for my meeting notes
Create a Notion page called Weekly Review with content about project progress
Read my latest emails
Send an email to sarah@example.com with subject Update and body The draft is ready
What should I focus on today?
```

type `exit` to quit

## How It Works
1. The app receives a user request.
2. The model classifies it as one of:
    - search
    - create
    - send
    - read
    - chat
3. If needed, the app extracts structured JSON data.
4. The appropriate Notion or Gmail function runs.
5. The result is added to the conversation context.
6. The assistant returns a final response.
7. Memory is saved locally in `memory.json`.

## Security
Do not commit these files:

- .env
- credentials.json
- token.json
- memory.json
- venv/
- __pycache__/

Suggested .gitignore:
```.gitignore
.env
credentials.json
token.json
memory.json
venv/
__pycache__/
*.pyc
```
## Limitations
- Only groq is currently supported
- CLI only
- Memory is stored locally
- Error handling can still be improved

## Future Improvements
- Add OpenAI and Anthropic support
- Add automated tests
- Improve validation and logging
- Expand Notion page formatting
- Improve email summarization