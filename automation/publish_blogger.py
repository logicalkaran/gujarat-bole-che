#!/usr/bin/env python3
"""Publish one generated HTML article to Blogger using OAuth refresh-token credentials.

Required environment variables:
BLOGGER_BLOG_ID
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REFRESH_TOKEN
"""

import json
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "auto_config.json").read_text(encoding="utf-8"))


def required(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def access_token():
    r = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": required("GOOGLE_CLIENT_ID"),
            "client_secret": required("GOOGLE_CLIENT_SECRET"),
            "refresh_token": required("GOOGLE_REFRESH_TOKEN"),
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def publish(html_body, title):
    blog_id = required("BLOGGER_BLOG_ID")
    token = access_token()
    r = requests.post(
        f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"kind": "blogger#post", "title": title, "content": html_body},
        timeout=45,
    )
    r.raise_for_status()
    return r.json()


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: publish_blogger.py ARTICLE.html 'POST TITLE'")
    article = Path(sys.argv[1])
    title = sys.argv[2]
    result = publish(article.read_text(encoding="utf-8"), title)
    print(json.dumps({
        "id": result.get("id"),
        "url": result.get("url"),
        "status": result.get("status"),
        "published": result.get("published"),
    }, indent=2))


if __name__ == "__main__":
    main()
