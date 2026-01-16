# Best Buy Price Tracker

A self-hosted price tracking tool with a web GUI and Discord alerts. Track multiple Best Buy products and get notified when prices drop.

![Dashboard Preview](https://via.placeholder.com/800x400?text=Dashboard+Preview)

## Features

- 📊 **Web Dashboard** - Clean UI to manage tracked products
- 🔔 **Discord Alerts** - Get notified on price changes with rich embeds
- 📉 **Price History** - Track price changes over time
- 🐳 **Docker Ready** - One command to deploy
- ⚙️ **Configurable** - Adjust polling intervals and notification preferences

---

## Quick Start

```bash
# Clone or download
git clone <your-repo> bestbuy-tracker
cd bestbuy-tracker

# Start it up
docker compose up -d

# Open the dashboard
open http://localhost:5000
```

Then configure your API keys in the Settings page.

---

## Setup Guide

### 1. Get a Best Buy API Key

The Best Buy API is **free** and takes about 2 minutes to set up.

1. Go to [developer.bestbuy.com](https://developer.bestbuy.com)
2. Click **"Get API Key"** in the top right
3. Sign up with your email address
4. Check your email and click the activation link
5. Your API key will be displayed - copy it

**Rate Limits:** 5 requests per second (plenty for personal use)

### 2. Create a Discord Webhook

Webhooks let the tracker send messages to your Discord channel.

1. Open **Discord** and go to your server
2. Right-click the channel where you want price alerts
3. Click **"Edit Channel"**
4. Go to **"Integrations"** in the left sidebar
5. Click **"Webhooks"**
6. Click **"New Webhook"**
7. Give it a name like "Price Alerts" and optionally set an avatar
8. Click **"Copy Webhook URL"**

The URL will look like:
```
https://discord.com/api/webhooks/1234567890/abcdefghijklmnop...
```

### 3. Configure the Tracker

1. Open the dashboard at `http://localhost:5000`
2. Click **"⚙️ Settings"**
3. Paste your **Best Buy API Key**
4. Paste your **Discord Webhook URL**
5. Click **"Test Webhook"** to verify it works
6. Go back to the dashboard and click **"Start"**

---

## Finding Best Buy SKUs

The SKU is a 7-digit number that identifies a product. You can find it:

**From the URL:**
```
https://www.bestbuy.com/site/epson-ls800-.../6513602.p?skuId=6513602
                                            ^^^^^^^
                                            This is the SKU
```

**From the product page:**
- Scroll down to "Specifications"
- Look for "SKU" in the list

**Example SKUs:**
| Product | SKU |
|---------|-----|
| Epson LS800 Black | 6513602 |
| Epson LS800 White | 6513640 |
| PS5 Console | 6523167 |

---

## Configuration Options

All settings are configurable via the web UI, but you can also edit `data/config.json` directly:

```json
{
  "bestbuy_api_key": "your-api-key",
  "discord_webhook_url": "https://discord.com/api/webhooks/...",
  "poll_interval": 60,
  "notify_on_any_change": true,
  "notify_on_price_drop_only": false,
  "skus": {
    "6513602": {"name": "Epson LS800 Black", "enabled": true}
  }
}
```

| Setting | Description | Default |
|---------|-------------|---------|
| `poll_interval` | Seconds between price checks | 60 |
| `notify_on_any_change` | Alert on any price change | true |
| `notify_on_price_drop_only` | Only alert on price drops | false |

---

## Docker Commands

```bash
# Start
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down

# Rebuild after code changes
docker compose up -d --build
```

---

## Data Persistence

All data is stored in the `./data` directory:

- `config.json` - API keys and settings
- `state.json` - Current price state for each SKU
- `history.json` - Price history (last 1000 entries per SKU)

This directory is mounted as a volume, so your data persists across container restarts.

---

## API Endpoints

The web UI uses a REST API that you can also call directly:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/config` | GET/POST | Get or update configuration |
| `/api/sku` | POST | Add a new SKU to track |
| `/api/sku/<sku>` | DELETE | Remove a SKU |
| `/api/sku/<sku>/toggle` | POST | Enable/disable a SKU |
| `/api/tracker/start` | POST | Start the price checker |
| `/api/tracker/stop` | POST | Stop the price checker |
| `/api/tracker/status` | GET | Get tracker status |
| `/api/check` | POST | Trigger immediate price check |
| `/api/test-webhook` | POST | Send test Discord message |
| `/api/history/<sku>` | GET | Get price history for a SKU |

---

## Troubleshooting

### "Best Buy API key not configured"
Go to Settings and add your API key from developer.bestbuy.com

### "Product not found" errors
- Verify the SKU is correct (7 digits)
- Check if the product is still available on bestbuy.com
- Some products may be region-restricted

### Discord alerts not working
1. Go to Settings and click "Test Webhook"
2. Verify the webhook URL is correct
3. Make sure the webhook hasn't been deleted in Discord
4. Check that the channel still exists

### Container won't start
```bash
# Check logs for errors
docker compose logs

# Rebuild
docker compose up -d --build
```

---

## License

MIT - Do whatever you want with it.
