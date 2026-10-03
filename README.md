# Gujarat Bole Che

Modern Blogger publication platform for Gujarat, India, with a source-backed research and content pipeline.

## v2 phase

- Mobile-first Blogger theme with search, dark mode, categories and responsive article cards.
- Research -> local Qwen draft -> source metadata -> quality gate -> optional Blogger publishing.
- 12-hour cadence by default; one article per cycle.
- Publishing remains disabled unless PUBLISH_ENABLED=true and valid Blogger OAuth credentials are supplied.
- Quality gate blocks short/empty articles, missing sources and several unsafe promotional claims.
- Credentials, tokens, logs and generated runtime data are excluded from Git.

## Safety

- No Blogger credentials or OAuth tokens are stored in this repository.
- Market data is time-sensitive and informational, not investment advice.
- No article copying, fake prices, unverified claims, artificial traffic or ad-click manipulation.

## Layout

- blogger/theme.xml — Blogger-compatible theme
- blogger/theme-upgrade.css / .js — interactive design layer
- automation/auto_generator.py — research and generation
- automation/quality_gate.py — publication safety/quality gate
- automation/publish_blogger.py — Blogger API publisher
- automation/run_24x7.sh — long-running scheduler
- config/topic_registry.json — editorial topics
