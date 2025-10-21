#!/usr/bin/env python3
import pyperclip
import requests
import threading
import time
import json
from flask import Flask, request, jsonify
from datetime import datetime
import argparse

app = Flask(__name__)

clipboard_log = []
last_clipboard = ""
peer_url = None  # URL of the other machine

def log_entry(text, source):
    entry = {"text": text, "source": source, "time": datetime.now().isoformat()}
    clipboard_log.append(entry)
    with open("clipboard_log.json", "w") as f:
        json.dump(clipboard_log, f, indent=2)
    print(f"[{source}] {text}")

@app.route("/sync", methods=["POST"])
def sync():
    data = request.json
    text = data.get("text", "")
    source = data.get("source", "remote")
    pyperclip.copy(text)
    log_entry(text, source)
    return jsonify({"status": "ok"})

@app.route("/log", methods=["GET"])
def get_log():
    return jsonify(clipboard_log)

def watch_clipboard(local_name):
    global last_clipboard
    while True:
        try:
            text = pyperclip.paste()
            if text != last_clipboard and text.strip() != "":
                last_clipboard = text
                log_entry(text, local_name)
                if peer_url:
                    requests.post(f"{peer_url}/sync", json={"text": text, "source": local_name}, timeout=2)
        except Exception:
            pass
        time.sleep(1)

def start_server(port):
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shared clipboard between two computers.")
    parser.add_argument("--name", required=True, help="Name of this machine (e.g. mac or fedora)")
    parser.add_argument("--peer", required=False, help="URL of peer machine (e.g. http://192.168.1.5:5000)")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    peer_url = args.peer
    start_server(args.port)
    watch_clipboard(args.name)