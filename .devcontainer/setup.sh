#!/usr/bin/env bash
# .devcontainer/setup.sh
# Post-create setup for GitHub Codespaces
# Runs once after the container is created.
set -euo pipefail

echo "🚀 TakiOS Codespaces Setup starting..."

# ── 1. Environment file ───────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
  echo "📄 Creating .env from .env.example..."
  cp .env.example .env

  # Inject Codespaces secrets if available
  [ -n "${ANTHROPIC_API_KEY:-}" ] && sed -i "s|ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}|" .env
  [ -n "${OPENAI_API_KEY:-}" ]    && sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=${OPENAI_API_KEY}|" .env
  [ -n "${SECRET_KEY:-}" ]        && sed -i "s|SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" .env

  echo "✅ .env created"
fi

# ── 2. Python backend dependencies ───────────────────────────────────────────
echo "🐍 Installing Python dependencies..."
cd backend
pip install --quiet --upgrade pip
pip install --quiet -e ".[dev]"
cd ..
echo "✅ Python deps installed"

# ── 3. Node.js frontend dependencies ─────────────────────────────────────────
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install --silent
cd ..
echo "✅ Node deps installed"

# ── 4. Git config convenience helpers ────────────────────────────────────────
git config --global --add safe.directory /workspaces/TakiOS 2>/dev/null || true

# Configure git credential helper using GITHUB_PAT_TOKEN (if available)
# This allows Copilot agents to commit and push from inside Codespaces
if [ -n "${GITHUB_PAT_TOKEN:-}" ]; then
  REPO_URL=$(git remote get-url origin 2>/dev/null || echo "")
  if [ -n "$REPO_URL" ]; then
    # Inject PAT into remote URL for passwordless push
    AUTH_URL=$(echo "$REPO_URL" | sed "s|https://|https://x-access-token:${GITHUB_PAT_TOKEN}@|")
    git remote set-url origin "$AUTH_URL"
    echo "✅ Git remote configured with PAT token for agent commits"
  fi
  # Also configure gh CLI with the PAT
  echo "${GITHUB_PAT_TOKEN}" | gh auth login --hostname github.com --git-protocol https --with-token 2>/dev/null && \
    echo "✅ GitHub CLI authenticated via GITHUB_PAT_TOKEN"
fi

echo ""
echo "✅ TakiOS Codespaces Setup complete!"
echo ""
echo "Available commands:"
echo "  make dev-backend   → Start FastAPI backend (uvicorn)"
echo "  make dev-frontend  → Start Next.js frontend"
echo "  make test          → Run all tests"
echo "  docker compose up  → Start full stack in Docker"
