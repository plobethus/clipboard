#!/bin/bash
# setup_clipboard.sh
set -e

echo "Installing Python and dependencies..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install python3 || true
else
    sudo dnf install -y python3 python3-pip
fi

pip3 install flask requests pyperclip

echo "Setup complete."
echo "Usage:"
echo "  python3 shared_clipboard.py --name <this_name> --peer http://<peer_ip>:5000 --port 5000"