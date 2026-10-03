#!/usr/bin/env python3
"""Lightweight on-device SEO optimizer for research articles.

It prepares search-friendly metadata without keyword stuffing or fabricated claims.
"""
import html
import re
from urllib.parse import urlparse

STOP = {
    "the","and","for","with","from","this","that","latest","today","news",
    "india","indian","gujarat","business","technology","finance"
}

def _words(text):
    text = re.sub(r"<[^>]+>", " ", text or "").lower()
    return [w for w in re.findall(r"[a-z][a-z0-9-]{2,}", text) if w not in STOP]

def optimize(topic, body, sources):
    text = re.sub(r"<[^>]+>", " ", body or "")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body or "", re.I | re.S)
    title = re.sub(r"\s+", " ", html.unescape(h1.group(1))).strip() if h1 else topic
    title = title[:60].rstrip(" -:|") or topic[:60]

    clean = re.sub(r"\s+", " ", text).strip()
    description = clean[:155].rstrip(" ,.;:-")
    if len(description) < 80:
        description = f"{title} — source-backed updates, key facts and context from Gujarat Bole Che."[:155]

    freq = {}
    for w in _words(text):
        freq[w] = freq.get(w, 0) + 1
    keywords = [w for w, _ in sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:8]]
    if topic.lower() not in [k.lower() for k in keywords]:
        keywords.insert(0, topic)
    keywords = keywords[:10]

    valid_sources = []
    for s in sources:
        u = s.get("url", "")
        if u and urlparse(u).scheme in ("http", "https"):
            valid_sources.append(u)

    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:80].strip("-")
    return {
        "title": title,
        "description": description,
        "keywords": keywords,
        "slug": slug,
        "source_count": len(valid_sources),
        "has_h1": bool(h1),
        "word_count": len(re.findall(r"\b\w+\b", clean)),
    }
