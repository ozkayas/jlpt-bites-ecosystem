#!/bin/bash
cd "$(dirname "$0")"

# Check for venv and activate if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check for service account key
if [ ! -f "service-account-key.json" ]; then
    echo "❌ Error: service-account-key.json not found in firestore/scripts/"
    echo "Please place your Firebase Service Account key file here and name it 'service-account-key.json'."
    exit 1
fi

python3 upload_passages.py "$@"
