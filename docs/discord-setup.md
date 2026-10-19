# Discord setup — step by step

From zero to a bot talking in your server in about 10 minutes.

## 1. Install Python

You need **Python 3.10 or newer**. Check with:

```bash
python --version      # Windows: py --version
```

If it's missing, install it from [python.org](https://www.python.org/downloads/). On Windows, tick **"Add python.exe to PATH"** during installation.

## 2. Download VryBot and install dependencies

```bash
git clone https://github.com/VryDeveloper/vrybot.git
cd vrybot
```

(No Git? Use *Code → Download ZIP* on GitHub and extract it.)

Create an isolated environment and install the packages. **Run every command from the `vrybot` folder that contains `requirements.txt`.**

**Linux / macOS**
```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

**Windows (PowerShell)**
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

When the environment is active your prompt starts with `(venv)`. Activate it again every time you open a new terminal.

## 3. Create the Discord application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**. The name you pick is the bot's name.
2. Open the **Bot** tab:
   - Click **Reset Token** and copy the token. It is shown only once; if you lose it, reset again.
   - Under **Privileged Gateway Intents**, turn on **Message Content Intent** and save. Without this the bot can't read messages.
3. Optional: upload an avatar in the same tab.

> ⚠️ The token is a password. Anyone who has it controls your bot. Never commit it or paste it in public chats. If it leaks, click **Reset Token** immediately.

## 4. Get a free AI key

You need at least one. Groq is the easiest start.

| Provider | Where | Notes |
|---|---|---|
| Groq | [console.groq.com/keys](https://console.groq.com/keys) | Sign in with Google/GitHub → *Create API Key*. Fast, no card. |
| Google Gemini | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Sign in → *Create API key*. |
| OpenRouter | [openrouter.ai/keys](https://openrouter.ai/keys) | Use models ending in `:free`. |

Adding more than one gives you automatic fallback when a free quota runs out.

## 5. Configure `.env`

```bash
cp .env.example .env          # Windows: copy .env.example .env
```

Open `.env` in any editor (Windows: `notepad .env`) and paste values right after `=`, with **no quotes and no spaces**:

```env
DISCORD_TOKEN=MTQx...your.token
GROQ_API_KEY=gsk_...
```

Leave everything else as is for now.

## 6. Invite the bot to your server

1. Developer Portal → your app → **OAuth2 → URL Generator**.
2. **Scopes:** `bot`.
3. **Bot Permissions:** *View Channels*, *Send Messages*, *Read Message History*.
4. Copy the URL at the bottom, open it in your browser and pick your server (you need *Manage Server* there).

## 7. Run it

```bash
python -m vrybot
```

You should see:

```
INFO    vrybot: Online as YourBot#1234 | providers: groq:openai/gpt-oss-120b | memory: memory
```

Test in Discord with `v! hi` or by mentioning the bot. Stop it with `Ctrl+C`.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `LoginFailure: Improper token has been passed` (401) | Wrong token. Copy it from **Bot → Reset Token** — not the Application ID, Public Key or Client Secret. No quotes or spaces in `.env`. |
| Bot is online but never answers | **Message Content Intent** is off, the bot can't see the channel, or `ALLOWED_CHANNEL_IDS` excludes it. |
| `PrivilegedIntentsRequired` | Same: enable **Message Content Intent**. |
| `No LLM provider configured` | No `*_API_KEY` filled in `.env`, or `.env` isn't in the project root. |
| Bot replies with the error message | Check the terminal: it logs which provider failed and why (invalid key, rate limit, unknown model). |
| `No module named discord` / `dotenv` | The venv isn't active, or you installed packages in another folder. Activate it and reinstall. |
| `Could not open requirements file` | You're in the wrong folder. `cd` into the one that contains `requirements.txt`. |
| Windows: `Fatal error in launcher` when using `pip` | A broken `pip.exe`. Always use `python -m pip ...` (or `py -m pip ...`). |
| Windows: `Activate.ps1 cannot be loaded` | Run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. |
| Windows: `Unable to copy venvlauncher.exe` | An old/locked `venv` folder in the same place. Run `deactivate`, delete the folder, create it again. |
