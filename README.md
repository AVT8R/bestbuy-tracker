# Best Buy Price Tracker

Get Discord alerts when Best Buy prices drop.

---

## Part 1: Install the Tracker

Run these commands **one at a time**, pressing Enter after each:

```bash
mkdir bestbuy-tracker
```

```bash
cd bestbuy-tracker
```

```bash
git clone https://github.com/AVT8R/bestbuy-tracker.git .
```

⚠️ **Don't forget the space and period (` .`) at the end!**

Now start it:

```bash
docker compose up -d
```

Wait about 30 seconds. You'll see text scrolling by.

**When it's done, you'll see:**
```
✔ Container bestbuy-tracker Started
```

Now open a web browser and go to:

```
http://YOUR_SERVER_IP:5000
```

Replace `YOUR_SERVER_IP` with your server's actual IP address (e.g., `http://192.168.1.100:5000`).

You should see the Price Tracker dashboard.

**🎉 The tracker is installed! Now we need to set up the API keys.**

---

## Part 2: Get a Best Buy API Key

The Best Buy API is free. This lets the tracker check prices.

### Step 1: Go to the Best Buy developer site

Open this link in your browser:

👉 **https://developer.bestbuy.com**

### Step 2: Click "Get API Key"

Look for a button that says "Get API Key" in the top-right area. Click it.

### Step 3: Create an account

Fill out the form:
- **Email**: Your email address
- **Password**: Make up a password
- **First Name**: Your first name
- **Last Name**: Your last name
- **Company** (optional): You can put anything here or leave it blank

Click the "Create Account" button.

### Step 4: Check your email

Best Buy will send you an email. Open it and click the activation link.

### Step 5: Copy your API key

After clicking the link, you'll see a page with your API key. It looks something like this:

```
A1b2C3d4E5f6G7h8I9j0
```

**Copy this key** - you'll need it in Part 4.

---

## Part 3: Create a Discord Webhook

A webhook lets the tracker send messages to your Discord channel.

### Step 1: Open Discord

Open the Discord app or go to https://discord.com in your browser. Log in if needed.

### Step 2: Go to your server

Click on the server where you want to receive price alerts. If you don't have a server, create one first (click the + button on the left sidebar).

### Step 3: Create a channel (optional)

If you want alerts in a specific channel:
1. Right-click on the channel list
2. Click "Create Channel"
3. Name it something like "price-alerts"
4. Click "Create Channel"

### Step 4: Open channel settings

Right-click on the channel where you want alerts (or the one you just created).

Click **"Edit Channel"**.

### Step 5: Go to Integrations

In the left sidebar of the settings window, click **"Integrations"**.

### Step 6: Create a webhook

Click **"Webhooks"**.

Click **"New Webhook"**.

### Step 7: Customize the webhook (optional)

- Click on the webhook name to change it (e.g., "Price Alerts")
- Click the icon to upload a custom avatar if you want

### Step 8: Copy the webhook URL

Click the **"Copy Webhook URL"** button.

The URL looks something like this:
```
https://discord.com/api/webhooks/1234567890123456789/aBcDeFgHiJkLmNoPqRsTuVwXyZ...
```

**Save this URL** - you'll need it in Part 4.

Click "Save Changes" at the bottom, then close the settings.

---

## Part 4: Configure the Tracker

### Step 1: Open the tracker settings

Go back to the tracker in your web browser:

```
http://YOUR_SERVER_IP:5000
```

Click the **"⚙️ Settings"** button in the top right.

### Step 2: Add your Best Buy API key

1. Find the "Best Buy API Key" field
2. Paste the API key you copied in Part 2
3. Click **"Save API Key"**

### Step 3: Add your Discord webhook

1. Find the "Discord Webhook URL" field
2. Paste the webhook URL you copied in Part 3
3. Click **"Save Webhook"**

### Step 4: Test the webhook

Click the **"Test Webhook"** button.

Check your Discord channel. You should see a message that says "🧪 Test Alert - Your Discord webhook is working!"

**If you don't see the message:**
- Make sure you copied the full webhook URL
- Make sure there are no extra spaces
- Try creating a new webhook and using that URL instead

### Step 5: Go back to the dashboard

Click **"← Back to Dashboard"** at the top.

### Step 6: Start the tracker

Click the green **"Start"** button.

The status should change from "● Stopped" to "● Running".

**🎉 You're done! The tracker is now monitoring prices.**

---

## Part 5: Adding Products to Track

The tracker comes with one product already added (Epson LS800). Here's how to add more:

### Finding a product's SKU

The SKU is a 7-digit number that identifies a Best Buy product.

1. Go to bestbuy.com
2. Find the product you want to track
3. Look at the URL - the SKU is in there:

```
https://www.bestbuy.com/site/some-product-name/6513602.p?skuId=6513602
                                                 ^^^^^^^
                                                 This is the SKU
```

Or scroll down on the product page and look for "SKU" in the specifications.

### Adding a product

1. On the tracker dashboard, scroll down to "Add Product"
2. Type the SKU number (e.g., `6513602`)
3. Leave the name blank (it will auto-fill)
4. Click **"Add"**

### Removing a product

Click the 🗑️ (trash can) icon next to the product you want to remove.

---

## Common Commands

Run these in your terminal while connected to your server and in the `bestbuy-tracker` folder.

**Check if it's running:**
```bash
docker compose ps
```

**View the logs (see what it's doing):**
```bash
docker compose logs -f
```
Press `Ctrl + C` to stop watching logs.

**Stop the tracker:**
```bash
docker compose down
```

**Start the tracker:**
```bash
docker compose up -d
```

**Restart the tracker:**
```bash
docker compose restart
```

**Update to the latest version:**
```bash
git pull
docker compose up -d --build
```

---

## Troubleshooting

### "I can't open the web page"

- Make sure you're using `http://` not `https://`
- Make sure you're using port `5000`
- Check that the container is running: `docker compose ps`
- Make sure your firewall allows port 5000

### "I don't see Discord messages"

1. Go to Settings and click "Test Webhook"
2. If the test works but you don't get price alerts, make sure the tracker is "Running"
3. Click "Check Now" on the dashboard to force an immediate check

### "Product not found" error

- Double-check the SKU number
- Make sure the product exists on bestbuy.com
- Some products are region-restricted

### The tracker stopped working

Restart it:
```bash
cd ~/bestbuy-tracker
docker compose restart
```

### I messed something up and want to start over

```bash
cd ~/bestbuy-tracker
docker compose down
rm -rf data
docker compose up -d
```

This deletes all your settings. You'll need to add your API key and webhook again.

---

## How It Works

- Every 60 seconds, the tracker checks the price of each product
- If the price changed since the last check, it sends you a Discord message
- Green message = price dropped 🎉
- Red message = price went up 😢
- Blue message = initial tracking started


