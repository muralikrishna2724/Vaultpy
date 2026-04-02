# VaultPy

VaultPy is a simple, secure, and native-feeling local password manager. Built using Python, Flask, and `pywebview`, it runs as a clean desktop app without opening a browser.

## Features

- Local storage — passwords are AES-256-GCM encrypted and stored on your machine
- Native desktop app via `pywebview` (no browser, no address bar)
- Add and delete password entries
- One master password controls access to your entire vault
- Auto-locks after 5 minutes of inactivity
- WebView2 Runtime bundled — no internet required on the target machine

## Download

Download the latest installer directly:
👉 **[Download VaultPy_Setup.exe](https://github.com/muralikrishna2724/Vaultpy/releases/latest/download/VaultPy_Setup.exe)**

Or check the [Releases page](https://github.com/muralikrishna2724/Vaultpy/releases) for all versions.

## Installation Notes

The installer bundles the Microsoft WebView2 Runtime and will install it silently if not already present on your PC. No internet connection is required on the target machine.

## Running from Source

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r files/requirements.txt
   ```
3. Run the app:
   ```
   python files/app.py
   ```
