# Deployment

The bot only needs outbound internet: no open ports, no domain, very little RAM (~100 MB). It must keep running for the bot to stay online.

## Option 1 — Your own computer

`python -m vrybot` in a terminal. Simplest, but the bot goes offline when the computer sleeps or the terminal closes. Good for testing.

## Option 2 — Docker (recommended for servers)

```bash
cp .env.example .env     # fill it in
docker compose up -d --build
docker compose logs -f   # watch the logs
```

What the compose file does:

- Restarts the bot automatically if it crashes or the machine reboots (`restart: unless-stopped`).
- Uses **SQLite memory** by default, stored in the `vrybot-data` volume, so conversations survive restarts.
- Mounts `./personas` read-only: edit a persona on the host, then `v!persona` — no rebuild.

Update to a new version:

```bash
git pull
docker compose up -d --build
```

## Option 3 — A Linux VPS without Docker (systemd)

```bash
git clone https://github.com/VryDeveloper/vrybot.git /opt/vrybot
cd /opt/vrybot
python3 -m venv venv && venv/bin/pip install -r requirements.txt
cp .env.example .env && nano .env
```

`/etc/systemd/system/vrybot.service`:

```ini
[Unit]
Description=VryBot Discord bot
After=network-online.target

[Service]
WorkingDirectory=/opt/vrybot
ExecStart=/opt/vrybot/venv/bin/python -m vrybot
Restart=always
RestartSec=5
User=vrybot

[Install]
WantedBy=multi-user.target
```

```bash
sudo useradd --system vrybot && sudo chown -R vrybot /opt/vrybot
sudo systemctl enable --now vrybot
journalctl -u vrybot -f
```

## Where to host for free or cheap

Free tiers change often; check current terms before choosing.

- **Oracle Cloud Always Free** — small ARM/AMD VMs; works well with Docker or systemd.
- **Google Cloud** free-tier e2-micro — enough for this bot.
- **A Raspberry Pi or old PC at home** — free and fully under your control.
- **Container platforms** (Railway, Fly.io, Render background workers…) — deploy straight from the Dockerfile; free allowances vary. Choose a *worker/background* service, not a web service, since the bot has no HTTP port.

## Production checklist

- [ ] `.env` is not committed, and file permissions restrict who can read it.
- [ ] `MEMORY_BACKEND=sqlite` (or a persistent volume) if you want memory across restarts.
- [ ] More than one provider key, for fallback.
- [ ] `USER_COOLDOWN` set to protect your free quota.
- [ ] `ALLOWED_CHANNEL_IDS` set if the bot should stay in specific channels.
- [ ] Logs are being kept (`docker compose logs`, `journalctl`).
