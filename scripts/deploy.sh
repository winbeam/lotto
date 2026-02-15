#!/bin/bash
# Lotto Auto Purchase - Deployment Script

set -e

SCRIPT_DIR="$(cd "$(dirname ""${BASH_SOURCE[0]}"")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting Deployment Process..."
echo "========================================"
date "+%Y-%m-%d %H:%M:%S"
echo ""

# 1. Update Environment (Dependencies & Playwright)
echo "📦 Step 1: Updating environment..."
"$SCRIPT_DIR/setup-env.sh"
echo ""

# 2. Update Systemd Timer
# Skip systemd setup during SSH deployment (no D-Bus session available)
if command -v systemctl &> /dev/null && [ -n "$XDG_RUNTIME_DIR" ]; then
echo "⏰ Step 2: Updating systemd timer..."
    "$SCRIPT_DIR/install-systemd.sh"
else
echo "⚠️  Step 2: Skipping systemd timer setup (SSH deployment or systemd not available)"
echo "   To enable automatic scheduling, run manually on the server:"
echo "   cd $PROJECT_DIR && ./scripts/install-systemd.sh"
fi

echo ""
echo "✅ Deployment completed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
