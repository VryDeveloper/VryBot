# Architecture

VryBot is a small set of independent parts wired together in `bot.py`. Each part has one job and can be replaced without touching the others.

```
                 ┌──────────────────────── VryBot (discord.ext.commands.Bot) ────────────────────────┐
                 │                                                                                    │
 Discord ──msg──▶│  cogs/chat.py ──▶ memory (MemoryBackend) ──▶ persona + history ──▶ llm (LLMClient)│──▶ reply
                 │       │                RAM | SQLite | …                              │              │
                 │  cogs/admin.py (help, reset, persona, status)          providers.py (registry)    │
                 └────────────────────────────────────────────────────────────────────────────────────┘
                                                                           Groq → Gemini → OpenRouter → custom
```

## Modules

| Module | Responsibility |
|---|---|
| `config.py` | Reads `.env` once into an immutable `Settings` object. Nothing else reads env vars for behavior. |
| `providers.py` | Registry of OpenAI-compatible endpoints (`PRESETS`) and `load_providers()`, which builds the ordered list from the env. |
| `llm.py` | `LLMClient.chat(messages)`: tries providers in order, puts rate-limited ones at the back for 60 s, raises `AllProvidersFailed` if nobody answers. |
| `memory/` | `MemoryBackend` abstract interface (`add`, `history`, `clear`) plus RAM and SQLite implementations, chosen by `create_memory()`. |
| `persona.py` | Loads the persona file, supports hot reload and `{bot_name}`. |
| `text.py` | Pure helpers: splitting replies over Discord's 2000-char limit, removing "BotName:" echoes. |
| `bot.py` | `VryBot` holds the shared services (`settings`, `llm`, `memory`, `persona`) and auto-loads every module in `cogs/`. |
| `cogs/chat.py` | The conversation flow (below). |
| `cogs/admin.py` | `help`, `reset`, `persona`, `status`. |

## Life of a message

1. **Filter** — ignore bots, channels outside `ALLOWED_CHANNEL_IDS`, and real commands (`v!reset` is handled by the admin cog).
2. **Clean** — mentions become `@names`, the bot's own mention and the prefix are removed.
3. **Remember** — the message is stored as `"Name: text"`, *even if the bot won't answer*. This is what lets it follow group conversations.
4. **Decide** — answer if it's a DM, a mention, a prefix, or a reply to the bot; otherwise roll `CHIME_IN_CHANCE`. Respect `USER_COOLDOWN`.
5. **Build the prompt** — `[system: persona] + last HISTORY_SIZE messages`.
6. **Generate** — `LLMClient.chat()` with fallback, while Discord shows "typing…".
7. **Post-process** — strip a leading "BotName:", store the reply in memory, split into ≤2000-char chunks and send as a reply.

## Design decisions

- **OpenAI-compatible API for everything.** Groq, Gemini, OpenRouter, Ollama and most hosted LLMs speak it, so one client and one code path cover them all. Adding a provider is data, not code.
- **Channel-wide memory, not per-user.** In a server, conversations are shared; the bot needs to see what others said to fit in.
- **Async interface for memory** even for RAM, so network stores (Redis, Postgres) drop in without changes to the chat cog.
- **Services on the bot object.** Cogs receive everything through `bot.*`, which keeps them decoupled and easy to test or replace.
- **Fail soft.** Provider errors never crash the bot; the user gets `MSG_ERROR` and the cause is logged.
