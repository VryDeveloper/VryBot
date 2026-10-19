# VryBot 🤖

[![CI](https://github.com/VryDeveloper/vrybot/actions/workflows/ci.yml/badge.svg)](https://github.com/VryDeveloper/vrybot/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)
![discord.py](https://img.shields.io/badge/discord.py-2.7-5865F2?logo=discord)
![License](https://img.shields.io/badge/License-MIT-yellow)

**A Discord chatbot with a personality you write yourself — running entirely on free LLM tiers.**

VryBot talks like a member of your server, not like a help desk. You describe who it is in a plain Markdown file, add one free API key, and it joins the conversation: it follows the context of the channel, replies naturally, and switches AI providers on its own when one hits its free limit.

---

## Features

- 🆓 **Zero API cost** — uses the free tiers of Groq, Google Gemini and OpenRouter, or a local model via Ollama.
- 🔁 **Automatic fallback** — if a provider is rate-limited or down, the next one answers. Users never notice.
- 🎭 **Personality as a file** — edit `personas/*.md`, run `v!persona`, done. No code, no restart.
- 👥 **Group-aware memory** — remembers the last messages of the channel from *everyone*, so it can follow and join group conversations.
- 🧩 **Modular** — providers, memory backends and features (cogs) are independent and pluggable.
- 💾 **RAM or SQLite memory** — one setting to make memory survive restarts.
- 🐳 **Docker-ready**, with tests and CI.

## Quick start

> Requires **Python 3.10+**. Full walkthrough with screenshots-level detail: [docs/discord-setup.md](docs/discord-setup.md).

**1. Get the code and install**

```bash
git clone https://github.com/VryDeveloper/vrybot.git
cd vrybot
python -m venv venv
```

| Linux / macOS | Windows (PowerShell) |
|---|---|
| `source venv/bin/activate` | `.\venv\Scripts\Activate.ps1` |

```bash
python -m pip install -r requirements.txt
```

**2. Create the Discord bot** — in the [Developer Portal](https://discord.com/developers/applications): *New Application → Bot → Reset Token* (copy it) and turn on **Message Content Intent**.

**3. Get one free AI key** — [Groq](https://console.groq.com/keys) is the recommended start (no credit card).

**4. Configure**

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

Open `.env` and fill in at least:

```env
DISCORD_TOKEN=your_bot_token
GROQ_API_KEY=your_groq_key
```

**5. Invite and run** — Developer Portal → *OAuth2 → URL Generator* → scope `bot`, permissions *View Channels, Send Messages, Read Message History* → open the generated URL. Then:

```bash
python -m vrybot
```

When the log says `Online as YourBot#1234`, say hi in your server. 🎉

## Talking to the bot

| How | Example |
|---|---|
| Mention it | `@VryBot what should I play tonight?` |
| Use the prefix | `v! explain recursion like I'm five` |
| Reply to one of its messages | just hit reply |
| Direct message | any message |

| Command | Who | What it does |
|---|---|---|
| `v!help` | everyone | How to talk to the bot |
| `v!reset` | Manage Messages (anyone in DMs) | Clear this channel's memory |
| `v!persona` | bot owner | Reload the persona file |
| `v!status` | bot owner | Active providers, models and memory |

## Make it yours

Create your own personality and keep it private (that folder is git-ignored):

```bash
mkdir personas/private
cp personas/default.md personas/private/my-bot.md
```

```env
PERSONA_FILE=personas/private/my-bot.md
```

Edit the file, then send `v!persona` in Discord. Tips on writing a persona that sounds human: [docs/personas.md](docs/personas.md).

## Configuration

Everything is set in `.env`; every option has a sensible default. The most useful ones:

| Variable | Default | Description |
|---|---|---|
| `PROVIDERS` | `groq,gemini,openrouter` | Fallback order. Providers without a key are skipped. |
| `PERSONA_FILE` | `personas/default.md` | Personality file. |
| `ALLOWED_CHANNEL_IDS` | *(all)* | Restrict the bot to some channels. |
| `HISTORY_SIZE` | `30` | Messages remembered per channel. |
| `CHIME_IN_CHANCE` | `0` | Chance (0–1) of joining a conversation uninvited. |
| `USER_COOLDOWN` | `3` | Seconds between replies to the same user. |
| `MEMORY_BACKEND` | `memory` | `memory` (RAM) or `sqlite` (persistent). |

Full reference: [docs/configuration.md](docs/configuration.md).

## Free providers

| Provider | Default model | Get a key |
|---|---|---|
| Groq | `openai/gpt-oss-120b` | [console.groq.com/keys](https://console.groq.com/keys) |
| Google Gemini | `gemini-flash-latest` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| OpenRouter | `meta-llama/llama-3.3-70b-instruct:free` | [openrouter.ai/keys](https://openrouter.ai/keys) |
| Custom (Ollama, LM Studio, any OpenAI-compatible API) | you choose | — |

Free-tier limits change often and differ per account — check each provider's dashboard. Some free tiers may use your prompts to improve their models, so don't send sensitive data.

## Project structure

```
vrybot/
├── vrybot/
│   ├── bot.py           # Entry point: builds services, auto-loads cogs
│   ├── config.py        # Settings from .env
│   ├── providers.py     # Provider registry (add new LLM APIs here)
│   ├── llm.py           # Chat client with automatic fallback
│   ├── persona.py       # Loads the personality file
│   ├── text.py          # Pure text helpers
│   ├── memory/          # Pluggable memory backends (RAM, SQLite)
│   └── cogs/            # Features — every file here is loaded automatically
│       ├── chat.py      #   the conversation
│       └── admin.py     #   help / reset / persona / status
├── personas/            # Personality files (private/ is git-ignored)
├── docs/                # Documentation
├── tests/
├── Dockerfile
└── docker-compose.yml
```

How it all fits together: [docs/architecture.md](docs/architecture.md).

## Deploy & scale

- **Docker:** `docker compose up -d --build` (memory persists in a volume). See [docs/deployment.md](docs/deployment.md) for VPS, free hosting options and keeping the bot online 24/7.
- **Extend it:** new providers, memory backends (Redis, Postgres) and features (slash commands, images...) plug in without touching the core — see [docs/extending.md](docs/extending.md).

## Development

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
ruff check .
```

## Documentation

| Doc | What's inside |
|---|---|
| [Discord setup](docs/discord-setup.md) | Step-by-step: create the bot, get keys, invite, run (Windows & Linux), troubleshooting |
| [Configuration](docs/configuration.md) | Every `.env` variable |
| [Personas](docs/personas.md) | Writing a personality that sounds human |
| [Architecture](docs/architecture.md) | How a message becomes a reply |
| [Deployment](docs/deployment.md) | Docker, VPS, 24/7 hosting |
| [Extending](docs/extending.md) | Adding providers, memory backends and cogs; scaling |

## License

MIT — see [LICENSE](LICENSE).

Made with 💜 by [VryDeveloper](https://github.com/VryDeveloper)
