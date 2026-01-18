#!/usr/bin/env python3
"""
Web GUI for Best Buy Price Tracker
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from tracker import tracker
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route("/")
def index():
    config = tracker.get_config()
    state = tracker.get_state()
    running = tracker.is_running()
    
    # Merge SKU config with current state
    products = []
    for sku, info in config.get("skus", {}).items():
        product_state = state.get(sku, {})
        products.append({
            "sku": sku,
            "name": product_state.get("name") or info.get("name", f"SKU {sku}"),
            "enabled": info.get("enabled", True),
            "price": product_state.get("price"),
            "regular_price": product_state.get("regular_price"),
            "available": product_state.get("available"),
            "on_sale": product_state.get("on_sale"),
            "last_check": product_state.get("last_check"),
            "url": product_state.get("url", f"https://www.bestbuy.com/site/{sku}.p?skuId={sku}")
        })
    
    # Check if API key is configured
    api_configured = bool(config.get("bestbuy_api_key"))
    webhook_configured = bool(config.get("discord_webhook_url"))
    
    return render_template("index.html",
        products=products,
        config=config,
        running=running,
        api_configured=api_configured,
        webhook_configured=webhook_configured
    )


@app.route("/settings")
def settings():
    config = tracker.get_config()
    return render_template("settings.html", config=config)


@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "GET":
        config = tracker.get_config()
        # Mask sensitive values
        if config.get("bestbuy_api_key"):
            config["bestbuy_api_key"] = "***configured***"
        if config.get("discord_webhook_url"):
            config["discord_webhook_url"] = "***configured***"
        return jsonify(config)
    
    data = request.form.to_dict() if request.content_type == 'application/x-www-form-urlencoded' else (request.json or {})
    
    updates = {}
    if "bestbuy_api_key" in data and data["bestbuy_api_key"] and not data["bestbuy_api_key"].startswith("***"):
        updates["bestbuy_api_key"] = data["bestbuy_api_key"]
    if "discord_webhook_url" in data and data["discord_webhook_url"] and not data["discord_webhook_url"].startswith("***"):
        updates["discord_webhook_url"] = data["discord_webhook_url"]
    if "poll_interval" in data:
        updates["poll_interval"] = int(data["poll_interval"])
    if "notify_on_any_change" in data:
        updates["notify_on_any_change"] = data["notify_on_any_change"] in [True, "true", "on", "1"]
    if "notify_on_price_drop_only" in data:
        updates["notify_on_price_drop_only"] = data["notify_on_price_drop_only"] in [True, "true", "on", "1"]
    
    if updates:
        tracker.update_config(updates)
    
    if request.headers.get("Accept") == "application/json":
        return jsonify({"status": "ok", "updated": list(updates.keys())})
    return redirect(url_for("settings"))


@app.route("/api/sku", methods=["POST"])
def add_sku():
    data = request.json or request.form.to_dict()
    sku = data.get("sku", "").strip()
    name = data.get("name", "").strip()
    
    if not sku:
        if request.headers.get("Accept") == "application/json":
            return jsonify({"error": "SKU required"}), 400
        return redirect(url_for("index"))
    
    result = tracker.add_sku(sku, name)
    
    if request.headers.get("Accept") == "application/json":
        return jsonify(result)
    return redirect(url_for("index"))


@app.route("/api/sku/<sku>", methods=["DELETE"])
def delete_sku(sku):
    success = tracker.remove_sku(sku)
    return jsonify({"status": "ok" if success else "not_found"})


@app.route("/api/sku/<sku>/toggle", methods=["POST"])
def toggle_sku(sku):
    data = request.json or {}
    enabled = data.get("enabled", True)
    success = tracker.toggle_sku(sku, enabled)
    return jsonify({"status": "ok" if success else "not_found"})


@app.route("/api/tracker/start", methods=["POST"])
def start_tracker():
    tracker.start()
    return jsonify({"status": "started", "running": tracker.is_running()})


@app.route("/api/tracker/stop", methods=["POST"])
def stop_tracker():
    tracker.stop()
    return jsonify({"status": "stopped", "running": tracker.is_running()})


@app.route("/api/tracker/status")
def tracker_status():
    return jsonify({
        "running": tracker.is_running(),
        "state": tracker.get_state()
    })


@app.route("/api/history/<sku>")
def get_history(sku):
    limit = request.args.get("limit", 100, type=int)
    return jsonify(tracker.get_history(sku, limit))


@app.route("/api/check", methods=["POST"])
def manual_check():
    """Trigger an immediate price check."""
    try:
        tracker.check_prices()
        return jsonify({"status": "ok", "state": tracker.get_state()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/test-webhook", methods=["POST"])
def test_webhook():
    """Send a test message to Discord."""
    import requests as req
    
    config = tracker.get_config()
    webhook_url = config.get("discord_webhook_url")
    
    if not webhook_url:
        return jsonify({"status": "error", "message": "No webhook configured"}), 400
    
    payload = {
        "embeds": [{
            "title": "🧪 Test Alert",
            "description": "Your Discord webhook is working!",
            "color": 0x0099FF,
            "footer": {"text": "Best Buy Price Tracker"}
        }]
    }
    
    try:
        resp = req.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # Auto-start tracker if configured
    config = tracker.get_config()
    if config.get("bestbuy_api_key"):
        tracker.start()
    
    app.run(host="0.0.0.0", port=5000, debug=False)
