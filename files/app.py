"""
app.py — Flask application entry point
---------------------------------------
Runs locally on 127.0.0.1 inside a native pywebview window.
Run with: python app.py
"""

import os
import sys
import threading
import time
import webview
from flask import (Flask, render_template, request,
                   redirect, url_for, session, jsonify)
from vault_manager import VaultManager


# ------------------------------------------------------------------ #
#  Resource path helper (needed when running as PyInstaller .exe)     #
# ------------------------------------------------------------------ #

def resource_path(rel):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, rel)
    return os.path.join(os.path.abspath("."), rel)


# ------------------------------------------------------------------ #
#  Flask app setup                                                     #
# ------------------------------------------------------------------ #

app = Flask(__name__,
            template_folder=resource_path("templates"),
            static_folder=resource_path("static"))

app.secret_key = os.urandom(32)

vault = VaultManager()


# ------------------------------------------------------------------ #
#  Helper                                                             #
# ------------------------------------------------------------------ #

def require_unlocked():
    if not vault.is_unlocked:
        return redirect(url_for("unlock"))
    return None


# ------------------------------------------------------------------ #
#  Routes                                                             #
# ------------------------------------------------------------------ #

@app.route("/")
def index():
    if vault.is_unlocked:
        return redirect(url_for("dashboard"))
    return redirect(url_for("unlock"))


@app.route("/unlock", methods=["GET", "POST"])
def unlock():
    if request.method == "POST":
        password = request.form.get("master_password", "")
        if not vault.vault_exists():
            vault.create_vault(password)
            session["unlocked"] = True
            return redirect(url_for("dashboard"))
        success = vault.unlock(password)
        if success:
            session["unlocked"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("unlock.html",
                                   error="Wrong master password. Try again.",
                                   is_new=False)
    is_new = not vault.vault_exists()
    return render_template("unlock.html", is_new=is_new)


@app.route("/dashboard")
def dashboard():
    guard = require_unlocked()
    if guard:
        return guard
    entries = vault.get_entries()
    return render_template("dashboard.html", entries=entries)


@app.route("/add", methods=["GET", "POST"])
def add_entry():
    guard = require_unlocked()
    if guard:
        return guard
    if request.method == "POST":
        vault.add_entry(
            title    = request.form.get("title", ""),
            username = request.form.get("username", ""),
            password = request.form.get("password", ""),
            url      = request.form.get("url", ""),
            notes    = request.form.get("notes", "")
        )
        return redirect(url_for("dashboard"))
    return render_template("add_entry.html")


@app.route("/delete/<entry_id>", methods=["POST"])
def delete_entry(entry_id):
    guard = require_unlocked()
    if guard:
        return guard
    vault.delete_entry(entry_id)
    return redirect(url_for("dashboard"))


@app.route("/lock")
def lock():
    vault.lock()
    session.clear()
    return redirect(url_for("unlock"))


@app.route("/api/password/<entry_id>")
def get_password(entry_id):
    if not vault.is_unlocked:
        return jsonify({"error": "locked"}), 403
    entry = vault.get_entry(entry_id)
    if not entry:
        return jsonify({"error": "not found"}), 404
    return jsonify({"password": entry["password"]})


# ------------------------------------------------------------------ #
#  Launch                                                             #
# ------------------------------------------------------------------ #

def start_flask():
    """Run Flask in a background thread."""
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    # Start Flask in background thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Wait briefly for Flask to be ready
    time.sleep(1)

    # Open native desktop window — no browser, no address bar
    window = webview.create_window(
        title     = "VaultPy — Password Manager",
        url       = "http://127.0.0.1:5000",
        width     = 1024,
        height    = 700,
        min_size  = (800, 600),
        resizable = True
    )
    webview.start()