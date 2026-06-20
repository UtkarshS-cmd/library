# news_digest.py — AI News Digest CLI
# Uses the official OpenRouter Python SDK (https://pypi.org/project/openrouter/)
import os
import argparse
from datetime import date
from pathlib import Path
import requests
from openrouter import OpenRouter
from openrouter import errors as openrouter_errors
from openrouter.types import UNSET
from dotenv import load_dotenv

# ─── Load Environment Variables ────────────────────────────────────────────
load_dotenv(override=True)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not NEWS_API_KEY or not OPENROUTER_API_KEY:
    raise EnvironmentError(
        "Missing API keys. Please ensure NEWS_API_KEY and OPENROUTER_API_KEY "
        "are set in your .env file."
    )

# ─── Free Model via OpenRouter ─────────────────────────────────────────────
FREE_MODEL = "meta-llama/llama-3.1-8b-instruct:free"

# ─── News Fetching ─────────────────────────────────────────────────────────


def fetch_articles(topic: str, count: int = 5) -> list[dict]:
    """Fetch top news articles on a topic from NewsAPI."""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": count,
        "apiKey": NEWS_API_KEY,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    articles = response.json().get("articles", [])
    print(f"[OK] Fetched {len(articles)} articles about '{topic}'")
    return articles


# ─── AI Summarisation via OpenRouter SDK ───────────────────────────────────


def summarise_article(title: str, content: str) -> str:
    """
    Summarise a news article using the official OpenRouter SDK.
    The SDK returns a ChatResult directly (res.choices[0].message.content).
    """
    if not content or len(content) < 100:
        return "Full article content not available for summarisation."

    with OpenRouter(
        api_key=OPENROUTER_API_KEY,
        http_referer="https://localhost",
        x_open_router_title="AI News Digest",
    ) as sdk:
        try:
            # sdk.chat.send() returns a ChatResult object directly (not a wrapper)
            # ChatResult.choices -> list[ChatChoice]
            # ChatChoice.message -> ChatAssistantMessage
            # ChatAssistantMessage.content -> str | list | UNSET
            res = sdk.chat.send(
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Summarise this news article in exactly 2-3 clear sentences. "
                            "Be concise and factual.\n\n"
                            f"Title: {title}\n\n"
                            f"Content: {content[:2000]}"
                        ),
                    }
                ],
                model=FREE_MODEL,
                max_tokens=200,
            )

            if not res.choices:
                return "[Summary: no choices returned by model]"

            msg_content = res.choices[0].message.content

            # content can be UNSET (sentinel), None, str, or list of content parts
            if msg_content is UNSET or msg_content is None:
                return "[Summary: empty response from model]"
            if isinstance(msg_content, list):
                # Extract text from content parts
                parts = [
                    p.get("text", "") if isinstance(p, dict) else str(p)
                    for p in msg_content
                ]
                return " ".join(parts).strip()
            return str(msg_content).strip()

        except openrouter_errors.UnauthorizedResponseError:
            return "[Auth error: invalid OPENROUTER_API_KEY. Please update your .env file.]"
        except openrouter_errors.SDKError as e:
            return f"[OpenRouter SDK error: {e}]"
        except Exception as e:
            return f"[Summary unavailable: {e}]"


# ─── Digest Generation ─────────────────────────────────────────────────────


def build_digest(topic: str, articles: list[dict]) -> str:
    """Build a Markdown-formatted digest from articles."""
    today = date.today().isoformat()
    lines = [
        f"# AI News Digest -- {topic.title()}",
        f"*Generated on {today} | {len(articles)} articles | Model: {FREE_MODEL}*",
        "",
    ]

    for i, article in enumerate(articles, start=1):
        title = article.get("title", "Untitled")
        source = article.get("source", {}).get("name", "Unknown Source")
        url = article.get("url", "")
        content = article.get("content") or article.get("description") or ""
        pub_date = article.get("publishedAt", "")[:10]

        print(f"   >> Summarising article {i}/{len(articles)}: {title[:55]}...")
        summary = summarise_article(title, content)

        lines += [
            f"## {i}. {title}",
            f"*Source: {source} | Published: {pub_date}*",
            "",
            f"**Summary:** {summary}",
            "",
            f"[Read full article]({url})",
            "",
            "---",
            "",
        ]

    return "\n".join(lines)


# ─── Save Digest ────────────────────────────────────────────────────────────


def save_digest(content: str, topic: str) -> Path:
    """Save digest to a Markdown file."""
    today = date.today().isoformat()
    filename = f"digest_{topic.replace(' ', '_')}_{today}.md"
    filepath = Path(filename)
    filepath.write_text(content, encoding="utf-8")
    return filepath


# ─── CLI Entry Point ────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description=(
            "AI News Digest -- fetch and summarise news articles "
            "using a free LLM via the official OpenRouter Python SDK."
        )
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="artificial intelligence",
        help="Topic to search news for (default: 'artificial intelligence')",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of articles to fetch (default: 5)",
    )
    args = parser.parse_args()

    print(f"\n[*] Fetching news about: '{args.topic}'")
    articles = fetch_articles(args.topic, args.count)

    if not articles:
        print("[!] No articles found. Try a different topic.")
        return

    print(f"\n[AI] Generating summaries using {FREE_MODEL} via OpenRouter SDK...")
    digest = build_digest(args.topic, articles)

    filepath = save_digest(digest, args.topic)
    print(f"\n[DONE] Digest saved to: {filepath}")
    print("\n--- First 500 characters of your digest ---")
    print(digest[:500])


if __name__ == "__main__":
    main()
