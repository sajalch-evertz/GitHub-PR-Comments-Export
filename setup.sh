#!/bin/bash

# Exit on error, treat unset vars as errors, and fail on pipeline errors
set -euo pipefail

echo "🔧 Setting up GitHub PR Comments Fetcher..."

# Ensure script is run from the directory where it's located
cd "$(dirname "$0")"

# Check for Python 3.12
echo "🔍 Checking for Python 3.12..."
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12 not found. Installing python3.12 and python3.12-venv..."
    sudo apt update
    sudo apt install -y python3.12 python3.12-venv
else
    echo "✅ Python 3.12 is installed."
fi

# Step 1: Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment with Python 3.12..."
    python3.12 -m venv .venv
else
    echo "✅ Virtual environment already exists."
fi

# Step 2: Activate virtual environment
echo "⚙️  Activating virtual environment..."
# shellcheck disable=SC1091
source .venv/bin/activate

# Step 3: Install dependencies
echo "📥 Installing Python packages..."
pip install --upgrade pip
pip install requests openpyxl

echo ""
echo "🎉 Setup complete!"
echo "👉 To activate the environment in future sessions, run:"
echo "   source .venv/bin/activate"
echo "👉 Then you can run the script:"
echo "   python fetch_pr_comments.py --org your-org --repo your-repo"
