#!/usr/bin/env bash
# scripts/github-setup.sh
# Führe dieses Script AUS NACHDEM du dich mit `gh auth login` angemeldet hast.
set -euo pipefail

REPO_NAME="TakiOS"
REPO_DESC="TakiOS – AI-powered bilingual learning platform (FastAPI + Next.js + Multi-Agent)"
GITHUB_USER=$(gh api user --jq .login)

echo "🔐 Eingeloggt als: ${GITHUB_USER}"

# ── Prüfen ob Repo schon existiert ───────────────────────────────────────────
if gh repo view "${GITHUB_USER}/${REPO_NAME}" &>/dev/null; then
  echo "📦 Repo existiert bereits: github.com/${GITHUB_USER}/${REPO_NAME}"
else
  echo "📦 Erstelle GitHub Repo: ${REPO_NAME}..."
  gh repo create "${REPO_NAME}" \
    --description "${REPO_DESC}" \
    --private \
    --source=. \
    --remote=origin
  echo "✅ Repo erstellt"
fi

# ── Remote setzen ─────────────────────────────────────────────────────────────
REMOTE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
if git remote get-url origin &>/dev/null; then
  git remote set-url origin "${REMOTE_URL}"
else
  git remote add origin "${REMOTE_URL}"
fi

echo "🔗 Remote: ${REMOTE_URL}"

# ── Pushen ────────────────────────────────────────────────────────────────────
echo "🚀 Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Fertig! Dein Code ist auf GitHub:"
echo "   https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo ""
echo "📌 Codespaces aktivieren:"
echo "   https://github.com/${GITHUB_USER}/${REPO_NAME}/settings → Codespaces"
echo ""
echo "🔑 Codespaces Secrets hinzufügen:"
echo "   https://github.com/settings/codespaces"
echo "   → ANTHROPIC_API_KEY, OPENAI_API_KEY, SECRET_KEY"
