# Personas

A persona is a plain Markdown file that becomes the bot's system prompt. Pick one with `PERSONA_FILE` in `.env`.

| File | Description |
|---|---|
| `default.md` | Friendly, honest, respectful chat member. Answers in the user's language. |

**Private personas:** anything inside `personas/private/` and any file ending in `.private.md` is git-ignored, so you can keep your own personality out of the public repo:

```env
PERSONA_FILE=personas/private/my-bot.md
```

See [docs/personas.md](../docs/personas.md) for how to write a good one.
