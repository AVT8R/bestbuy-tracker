#!/usr/bin/env python3
"""
Best Buy Price Tracker with Discord Alerts
Multi-SKU support with web GUI for management.
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from threading import Thread, Event
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

DATA_DIR = Path("/data")
CONFIG_FILE = DATA_DIR / "config.json"
STATE_FILE = DATA_DIR / "state.json"
HISTORY_FILE = DATA_DIR / "history.json"

DEFAULT_CONFIG = {
    "bestbuy_api_key": "",
    "discord_webhook_url": "",
    "poll_interval": 60,
    "notify_on_any_change": True,
    "notify_on_price_drop_only": False,
    "skus": {
        "6513602": {"name": "Epson LS800 Black", "enabled": True},
    }
}


class PriceTracker:
    def __init__(self):
        self.running = Event()
        self.thread = None
        self._ensure_data_dir()
        self.config = self._load_config()
        self.state = self._load_state()
        self.history = self._load_history()

    def _ensure_data_dir(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _load_config(self):
        if CONFIG_FILE.exists():
            try:
                config = json.loads(CONFIG_FILE.read_text())
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        return DEFAULT_CONFIG.copy()

    def _save_config(self):
        CONFIG_FILE.write_text(json.dumps(self.config, indent=2))

    def _load_state(self):
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text())
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
        return {}

    def _save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, indent=2))

    def _load_history(self):
        if HISTORY_FILE.exists():
            try:
                return json.loads(HISTORY_FILE.read_text())
            except Exception as e:
                logger.error(f"Failed to load history: {e}")
        return {}

    def _save_history(self):
        HISTORY_FILE.write_text(json.dumps(self.history, indent=2))

    def _add_history_entry(self, sku, price, available):
        if sku not in self.history:
            self.history[sku] = []
        
        self.history[sku].append({
            "timestamp": datetime.now().isoformat(),
            "price": price,
            "available": available
        })
        
        # Keep last 1000 entries per SKU
        self.history[sku] = self.history[sku][-1000:]
        self._save_history()

    def get_config(self):
        return self.config.copy()

    def update_config(self, updates):
        self.config.update(updates)
        self._save_config()
        logger.info(f"Config updated: {list(updates.keys())}")

    def add_sku(self, sku, name=""):
        if not name:
            try:
                product = self.fetch_product(sku)
                name = product.get("name", f"SKU {sku}")
            except:
                name = f"SKU {sku}"
        
        self.config["skus"][sku] = {"name": name, "enabled": True}
        self._save_config()
        logger.info(f"Added SKU: {sku} - {name}")
        return {"sku": sku, "name": name}

    def remove_sku(self, sku):
        if sku in self.config["skus"]:
            del self.config["skus"][sku]
            self._save_config()
            logger.info(f"Removed SKU: {sku}")
            return True
        return False

    def toggle_sku(self, sku, enabled):
        if sku in self.config["skus"]:
            self.config["skus"][sku]["enabled"] = enabled
            self._save_config()
            return True
        return False

    def get_state(self):
        return self.state.copy()

    def get_history(self, sku=None, limit=100):
        if sku:
            return self.history.get(sku, [])[-limit:]
        return {k: v[-limit:] for k, v in self.history.items()}

    def fetch_product(self, sku):
        api_key = self.config.get("bestbuy_api_key")
        if not api_key:
            raise ValueError("Best Buy API key not configured")

        url = f"https://api.bestbuy.com/v1/products/{sku}.json"
        params = {
            "apiKey": api_key,
            "show": "sku,name,salePrice,regularPrice,onSale,dollarSavings,percentSavings,onlineAvailability,url"
        }

        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def send_discord_alert(self, product, old_price, sku):
        webhook_url = self.config.get("discord_webhook_url")
        if not webhook_url:
            logger.warning("No Discord webhook configured")
            return

        sale_price = product.get("salePrice")
        regular_price = product.get("regularPrice")
        name = product.get("name", "Unknown Product")
        url = product.get("url", "")
        on_sale = product.get("onSale", False)
        savings = product.get("dollarSavings", 0)
        percent_off = product.get("percentSavings", 0)
        available = product.get("onlineAvailability", False)

        if old_price is None:
            color = 0x0099FF
            title = "📢 Now Tracking"
        elif sale_price < old_price:
            color = 0x00FF00
            title = "🔻 PRICE DROP"
        elif sale_price > old_price:
            color = 0xFF0000
            title = "🔺 Price Increase"
        else:
            color = 0x0099FF
            title = "📢 Status Update"

        fields = [
            {"name": "Current Price", "value": f"**${sale_price:,.2f}**", "inline": True},
            {"name": "Regular Price", "value": f"${regular_price:,.2f}", "inline": True},
        ]

        if old_price and old_price != sale_price:
            diff = old_price - sale_price
            fields.append({"name": "Change", "value": f"${diff:+,.2f}", "inline": True})

        if on_sale and savings:
            fields.append({"name": "Sale Savings", "value": f"${savings:,.2f} ({percent_off:.0f}% off)", "inline": True})

        fields.append({"name": "Available Online", "value": "✅ Yes" if available else "❌ No", "inline": True})
        fields.append({"name": "SKU", "value": sku, "inline": True})

        embed = {
            "title": title,
            "description": f"**{name}**",
            "color": color,
            "fields": fields,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Best Buy Price Tracker"}
        }

        if url:
            embed["url"] = url

        payload = {"embeds": [embed]}

        try:
            resp = requests.post(webhook_url, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info(f"Discord alert sent: {title} - {name}")
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")

    def check_prices(self):
        skus = self.config.get("skus", {})
        notify_any = self.config.get("notify_on_any_change", True)
        notify_drop_only = self.config.get("notify_on_price_drop_only", False)

        for sku, info in skus.items():
            if not info.get("enabled", True):
                continue

            try:
                product = self.fetch_product(sku)
                current_price = product.get("salePrice")
                available = product.get("onlineAvailability", False)
                name = product.get("name", info.get("name", "Unknown"))

                if name and name != info.get("name"):
                    self.config["skus"][sku]["name"] = name
                    self._save_config()

                old_price = self.state.get(sku, {}).get("price")
                first_check = old_price is None

                logger.info(f"[{sku}] {name[:40]}... | ${current_price:,.2f} | Available: {available}")

                self._add_history_entry(sku, current_price, available)

                should_alert = False
                if first_check:
                    should_alert = True
                elif current_price != old_price:
                    if notify_drop_only:
                        should_alert = current_price < old_price
                    elif notify_any:
                        should_alert = True

                if should_alert:
                    self.send_discord_alert(product, old_price, sku)

                self.state[sku] = {
                    "price": current_price,
                    "regular_price": product.get("regularPrice"),
                    "available": available,
                    "on_sale": product.get("onSale", False),
                    "name": name,
                    "last_check": datetime.now().isoformat(),
                    "url": product.get("url", "")
                }
                self._save_state()

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    logger.warning(f"[{sku}] Product not found")
                else:
                    logger.error(f"[{sku}] HTTP error: {e}")
            except Exception as e:
                logger.error(f"[{sku}] Error: {e}")

    def _run_loop(self):
        logger.info("Price tracker started")
        while self.running.is_set():
            try:
                self.check_prices()
            except Exception as e:
                logger.error(f"Error in check loop: {e}")

            interval = self.config.get("poll_interval", 60)
            for _ in range(interval):
                if not self.running.is_set():
                    break
                time.sleep(1)

        logger.info("Price tracker stopped")

    def start(self):
        if self.thread and self.thread.is_alive():
            logger.warning("Tracker already running")
            return

        if not self.config.get("bestbuy_api_key"):
            logger.error("Cannot start: Best Buy API key not configured")
            return

        self.running.set()
        self.thread = Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running.clear()
        if self.thread:
            self.thread.join(timeout=5)

    def is_running(self):
        return self.running.is_set()


# Global tracker instance
tracker = PriceTracker()
