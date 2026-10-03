#!/usr/bin/env python3
"""24/7 research-to-article generator. Publishing stays disabled until Blogger OAuth is configured."""

import html
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import requests
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "auto_config.json").read_text(encoding="utf-8"))
OUT = ROOT / "generated"
OUT.mkdir(exist_ok=True)
UA = "GujaratBoleChe-AutoResearch/1.0"


def google_news(query):
    url = "https://news.google.com/rss/search?q=" + quote(query) + "&hl=en-IN&gl=IN&ceid=IN:en"
    r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    items = []
    for item in root.findall(".//item")[:8]:
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        pub = item.findtext("pubDate") or ""
        source = item.findtext("source") or ""
        if title and link:
            items.append({"title": title, "url": link, "published": pub, "source": source})
    return items


def market_snapshot():
    symbols = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "USD/INR": "INR=X",
        "BTC": "BTC-USD",
    }
    result = {}
    for name, symbol in symbols.items():
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/" + quote(symbol, safe="")
            data = requests.get(url, headers={"User-Agent": UA}, timeout=15).json()["chart"]["result"][0]
            meta = data.get("meta", {})
            price = meta.get("regularMarketPrice")
            prev = meta.get("previousClose")
            change = None if price is None or not prev else ((price - prev) / prev) * 100
            result[name] = {"symbol": symbol, "price": price, "previous_close": prev, "change_pct": change}
        except Exception as exc:
            result[name] = {"symbol": symbol, "error": str(exc)}
    return result


def llm_draft(topic, articles, market):
    prompt = f"""Write an original factual news-style article for Gujarat Bole Che.
Topic: {topic}
Time: {datetime.now(timezone.utc).isoformat()}
Market data: {json.dumps(market)}
Research sources: {json.dumps(articles)}
Do not copy source wording. Do not invent facts. Clearly label market data.
Use a headline, introduction, H2 sections, useful bullets and a Sources section.
Mention that market prices can change and this is not investment advice.
Return only HTML."""
    base = CONFIG["local_llm"]["base_url"].rstrip("/")
    r = requests.post(
        base + "/completions",
        json={
            "model": CONFIG["local_llm"]["model"],
            "prompt": prompt,
            "temperature": 0.2,
            "n_predict": 300,
            "stream": False,
        },
        timeout=40,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["text"]


def fallback_draft(topic, articles, market):
    rows = []
    for name, data in market.items():
        if data.get("price") is not None:
            change = data.get("change_pct")
            suffix = f" ({change:+.2f}%)" if change is not None else ""
            rows.append(
                f"<li><strong>{html.escape(name)}</strong>: "
                f"{data['price']:.4f}{suffix}</li>"
            )
    source_rows = "".join(
        f'<li><a href="{html.escape(a["url"], quote=True)}">'
        f'{html.escape(a["title"])}</a> — '
        f'{html.escape(a.get("source", ""))}</li>'
        for a in articles[:8]
    )
    return (
        f"<h1>{html.escape(topic)}</h1>"
        "<p>This research update was generated from the sources listed below. "
        "Verify time-sensitive information before acting on it.</p>"
        f"<h2>Market snapshot</h2><ul>{''.join(rows) or '<li>Market data unavailable.</li>'}</ul>"
        f"<h2>Latest source signals</h2><ul>{source_rows or '<li>No source items available.</li>'}</ul>"
        "<h2>Important note</h2><p>Market prices change continuously. "
        "This article is informational and is not investment advice.</p>"
        f"<h2>Sources</h2><ul>{source_rows or '<li>No sources recorded.</li>'}</ul>"
    )


def run_once():
    topic = CONFIG["topics"][int(time.time() // 3600) % len(CONFIG["topics"])]
    articles = []
    for query in topic["queries"]:
        try:
            articles.extend(google_news(query))
        except Exception as exc:
            print("RSS error:", query, exc)
    seen = set()
    unique = []
    for article in articles:
        if article["url"] not in seen:
            seen.add(article["url"])
            unique.append(article)
    articles = unique[:12]
    market = market_snapshot()

    try:
        body = llm_draft(topic["name"], articles, market)
        generation_mode = "local_llm"
    except Exception as exc:
        print("LLM unavailable; using structured fallback:", exc)
        body = fallback_draft(topic["name"], articles, market)
        generation_mode = "fallback"

    now = datetime.now(timezone.utc)
    slug = re.sub(r"[^a-z0-9]+", "-", topic["name"].lower()).strip("-")
    path = OUT / f"{now.strftime('%Y%m%dT%H%M%SZ')}-{slug}.html"
    path.write_text(body, encoding="utf-8")
    path.with_suffix(".json").write_text(
        json.dumps(
            {
                "topic": topic,
                "created_at": now.isoformat(),
                "generation_mode": generation_mode,
                "sources": articles,
                "market": market,
                "publish_status": "dry_run" if CONFIG["dry_run"] else "pending_blogger",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"article": str(path), "sources": len(articles), "mode": generation_mode}, indent=2))


if __name__ == "__main__":
    run_once()
