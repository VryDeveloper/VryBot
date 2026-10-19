# Configuration reference

All settings come from environment variables, usually through a `.env` file in the project root (copy `.env.example`). An empty value (`NAME=`) means "use the default".

## Discord

| Variable | Default | Description |
|---|---|---|
| `DISCORD_TOKEN` | — (**required**) | Bot token from the Developer Portal. |
| `PREFIX` | `v!` | Prefix for commands (`v!reset`) and for talking (`v! hello`). |
| `ALLOWED_CHANNEL_IDS` | *(empty = all)* | Comma-separated channel IDs the bot answers in. Threads follow their parent channel. DMs are always allowed. Get IDs with Discord *Developer Mode → right-click channel → Copy Channel ID*. |

## LLM providers

| Variable | Default | Description |
|---|---|---|
| `PROVIDERS` | `groq,gemini,openrouter` | Fallback order. Unknown names raise an error; providers without a key are skipped. Add `custom` to use your own endpoint. |
| `GROQ_API_KEY` / `GROQ_MODEL` | — / `openai/gpt-oss-120b` | |
| `GEMINI_API_KEY` / `GEMINI_MODEL` | — / `gemini-flash-latest` | |
| `OPENROUTER_API_KEY` / `OPENROUTER_MODEL` | — / `meta-llama/llama-3.3-70b-instruct:free` | |
| `CUSTOM_BASE_URL` / `CUSTOM_API_KEY` / `CUSTOM_MODEL` | — | Any OpenAI-compatible server. The key is optional for local servers. |
| `<NAME>_BASE_URL` | preset | Override the endpoint of any provider (e.g. a proxy). |
| `REASONING_EFFORT` | `low` | Only for reasoning models (`gpt-oss`): `low`, `medium` or `high`. Higher = slower, more thoughtful. |

**Choosing models:** any chat model the provider offers works. Check the provider's model list and paste the exact ID. If a model is removed, the provider returns an error and the bot falls back to the next one.

**Fallback rules:** a provider is skipped (and the next one tried) on rate limit, timeout, connection error, server error, invalid key or unknown model. A rate-limited provider goes to the back of the queue for 60 seconds.

## Personality

| Variable | Default | Description |
|---|---|---|
| `PERSONA_FILE` | `personas/default.md` | Path (relative to the project root, or absolute) of the persona file. See [personas.md](personas.md). |

## Behavior

| Variable | Default | Description |
|---|---|---|
| `HISTORY_SIZE` | `30` | Messages kept per channel (from all users plus the bot). More = better context but more tokens per request. |
| `CHIME_IN_CHANCE` | `0` | Probability (0–1) of answering a message that wasn't addressed to the bot. `0.03` ≈ once every 33 messages. Each chime-in uses quota. |
| `USER_COOLDOWN` | `3` | Minimum seconds between two replies to the same user. Protects your free quota from spam. |
| `TEMPERATURE` | `0.8` | Creativity. `0.3` = focused, `1.0` = loose. |
| `MAX_TOKENS` | `400` | Max reply length in tokens (~300 words). |

## Memory

| Variable | Default | Description |
|---|---|---|
| `MEMORY_BACKEND` | `memory` | `memory`: RAM, cleared on restart. `sqlite`: saved to disk. |
| `SQLITE_PATH` | `data/memory.db` | SQLite file when `MEMORY_BACKEND=sqlite`. |

## Canned replies

| Variable | Default |
|---|---|
| `MSG_ERROR` | "Sorry, I couldn't think of an answer right now. Try again in a moment." |
| `MSG_RESET` | "Done, I've cleared our conversation in this channel." |
| `MSG_COOLDOWN` | *(empty = ignore silently)* |

Write these in your bot's language and voice.

## Misc

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | `DEBUG` also logs which provider answered each message. |
| `DISABLED_COGS` | — | Comma-separated cog module names to skip, e.g. `admin`. |
