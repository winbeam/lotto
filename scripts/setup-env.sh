#!/bin/bash
# Lotto Auto Purchase - Environment Setup Script

set -e

SCRIPT_DIR="$(cd "$(dirname ""${BASH_SOURCE[0]}"")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo "🎰 Lotto Auto Purchase - Environment Setup"
echo "============================================"
echo ""
echo "📂 Project directory: $PROJECT_DIR"
echo ""

# Step 1: Check Python
echo "🐍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✅ Found: $PYTHON_VERSION"
echo ""

# Step 2: Create virtual environment
if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/pip" ]; then
    echo "✅ Virtual environment already exists"
else
    if [ -d "$VENV_DIR" ]; then
        echo "⚠️  Existing virtual environment is corrupted. Recreating..."
        rm -rf "$VENV_DIR"
    fi
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created at: $VENV_DIR"
fi
echo ""

# Step 3: Upgrade pip
echo "⬆️  Upgrading pip..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
echo "✅ pip upgraded"
echo ""

# Step 4: Install dependencies
echo "📥 Installing Python dependencies..."
"$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
echo "✅ Dependencies installed:"
"$VENV_DIR/bin/pip" list | grep -E "playwright|pytest-playwright|pytesseract|Pillow|python-dotenv"
echo ""

# Step 5: Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
"$VENV_DIR/bin/playwright" install chromium

# Install system dependencies on Linux (requires sudo)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detection Linux: Installing system dependencies for headless browser..."
    echo "🔑 Sudo password may be required."
    sudo "$VENV_DIR/bin/playwright" install-deps chromium
fi

 echo "✅ Playwright Chromium browser installed"
echo ""

# Step 6: Check .env file
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "📝 Creating .env from .env.example..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "✅ .env file created"
echo ""
    echo "🔧 Please edit .env and configure:"
    echo "   - USER_ID: Your dhlottery.co.kr ID"
    echo "   - PASSWD: Your password"
    echo "   - CHARGE_PIN: Your 6-digit charge PIN"
    echo "   - AUTO_GAMES: Number of auto games (optional)"
    echo "   - MANUAL_NUMBERS: Manual numbers in JSON format (optional)"
echo ""
else
    echo "✅ .env file exists"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Environment setup completed!"
echo ""
echo "📝 Next steps:"
echo "  1. Configure your .env file:"
echo "     nano $PROJECT_DIR/.env"
echo ""
echo "  2. Test the scripts:"
echo "     cd $PROJECT_DIR"
echo "     source .venv/bin/activate"
echo "     ./src/balance.py"
echo ""
echo "  3. Install systemd timer (Linux only):"
echo "     ./scripts/install-timer.sh"
echo ""