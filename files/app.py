"""
app.py — Flask application entry point
---------------------------------------
Binds to 127.0.0.1 only — never reachable from outside the machine.
Run with: python app.py
Then open: http://localhost:5000
"""

import os
import webbrowser
import threading
from flask import (Flask, render_template, request,
                   redirect, url_for, session, jsonify)
from vault_manager import VaultManager


app = Flask(__name__)
app.secret_key = os.urandom(32)   # Session encryption key, random per run

# One VaultManager instance for the whole app session
vault = VaultManager()


# ------------------------------------------------------------------ #
#  Helper                                                             #
# ------------------------------------------------------------------ #

def require_unlocked():
    """Return redirect if vault is locked, else None."""
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
            # First run — create vault
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


# API endpoint — used by JS clipboard copy button
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

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    # Open browser after short delay (server needs to start first)
    threading.Timer(1.2, open_browser).start()
    # IMPORTANT: bind to 127.0.0.1 only, never 0.0.0.0
    app.run(host="127.0.0.1", port=5000, debug=False)
