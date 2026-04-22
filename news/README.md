# AI News Digest

A Python CLI tool that fetches the latest news articles on any topic using [NewsAPI](https://newsapi.org/) and generates AI-powered summaries using a **free LLM via the official [OpenRouter Python SDK](https://pypi.org/project/openrouter/)** (`meta-llama/llama-3.1-8b-instruct:free`).

---

## Prerequisites

- Python 3.10 or higher
- A [NewsAPI](https://newsapi.org/register) API key
- An [OpenRouter](https://openrouter.ai/) API key (free tier is sufficient)

---

## Setup Instructions

### 1. Navigate to the project directory

```powershell
cd path\to\project
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure your API keys

Open the `.env` file and fill in your keys:

```env
NEWS_API_KEY=your_newsapi_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

> **Warning**: Never commit your `.env` file to version control. Add it to `.gitignore`.

---

## Running the Script

### Default (searches "artificial intelligence", fetches 5 articles):

```powershell
.\venv\Scripts\python.exe news_digest.py
```

### Custom topic:

```powershell
.\venv\Scripts\python.exe news_digest.py --topic "climate change"
```

### Custom topic and article count:

```powershell
.\venv\Scripts\python.exe news_digest.py --topic "space exploration" --count 10
```

---

## Output

The script generates a Markdown file named:

```
digest_<topic>_<YYYY-MM-DD>.md
```

Example: `digest_artificial_intelligence_2026-04-21.md`

---

## AI Model Used

This tool uses **`meta-llama/llama-3.1-8b-instruct:free`** via the official OpenRouter Python SDK — a completely free model with no cost per request.

---

## Dependencies

| Package          | Purpose                                      |
|------------------|----------------------------------------------|
| `openrouter`     | Official OpenRouter Python SDK               |
| `requests`       | HTTP requests to NewsAPI                     |
| `python-dotenv`  | Load API keys from `.env`                    |

---

## Project Structure

```
.
├── news_digest.py      # Main script
├── requirements.txt    # Python dependencies
├── .env                # API keys (do NOT commit to git)
├── README.md           # This file
└── venv/               # Virtual environment (auto-created)
```
