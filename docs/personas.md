# Writing a persona

The persona file is the bot's system prompt: the instructions the model reads before every reply. It is the single biggest factor in whether the bot sounds like a person or a help desk.

## Where it lives

- `personas/default.md` — the public example (friendly, honest, respectful).
- `personas/private/` or `*.private.md` — git-ignored; put your own here.

Select it with `PERSONA_FILE` in `.env`. After editing, send `v!persona` (bot owner only) to reload without restarting.

`{bot_name}` anywhere in the file is replaced with the bot's Discord display name.

## What the bot actually sees

```
system:    <your persona file>
user:      Ana: anyone played the new Zelda?
user:      Leo: not yet, worth it?
assistant: <a previous bot reply>
user:      Ana: @bot what do you think?
```

Every user message is prefixed with the author's display name, so the bot knows who said what in a group. Write your persona with that format in mind.

## A structure that works

1. **Identity** — one or two sentences: who the bot is and its role in the server.
2. **Personality** — 3–5 concrete traits. "Sarcastic but never cruel" beats "funny".
3. **How it talks** — length, tone, slang, language, what to avoid.
4. **Examples** — 3–5 short exchanges in exactly the style you want.

## Tips for natural replies

- **Examples beat rules.** Models imitate examples far more reliably than they follow adjectives. If replies are off, add or fix an example before adding a rule.
- **Ask for short replies explicitly.** "Most replies are 1–3 sentences" is the most effective single line against robotic walls of text.
- **Ban the assistant tics.** "No bullet lists in conversation", "don't start with 'Great question!'", "don't end offering more help".
- **Say what to do, not only what to avoid.** "Admit you don't know" works better than "don't hallucinate".
- **Cover emotional moments.** Tell it how to act when someone is upset; even a playful bot should soften then.
- **Keep it under ~600 words.** The persona is sent with every message and counts against your token quota.
- **Language:** either fix it ("always answer in Brazilian Portuguese, informal") or mirror the user ("answer in the user's language").

## Tuning with settings

- Replies too wild → lower `TEMPERATURE` (e.g. `0.6`).
- Too repetitive / bland → raise it (e.g. `0.95`).
- Forgets the conversation → raise `HISTORY_SIZE`.
- Cut off mid-sentence → raise `MAX_TOKENS`, or ask for shorter replies in the persona.

## Responsibility

The persona is yours, and so is the bot's behavior in your server. Free providers also apply their own usage policies and may refuse or filter content regardless of the persona.
