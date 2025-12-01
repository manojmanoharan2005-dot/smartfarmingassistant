#!/usr/bin/env bash
# Simple script to add, commit and push project changes.
# Usage: ./scripts/git_push.sh "Commit message" [branch]

set -euo pipefail

MSG="${1:-}"
BRANCH="${2:-}"

if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "This is not a git repository. Initialize with: git init"
  exit 1
fi

if [ -z "$BRANCH" ]; then
  BRANCH="$(git rev-parse --abbrev-ref HEAD)"
fi

echo "Staging all changes..."
git add -A

if [ -z "$MSG" ]; then
  echo "Opening editor for commit message..."
  git commit || { echo "Nothing to commit."; exit 0; }
else
  git commit -m "$MSG" || { echo "Nothing to commit."; exit 0; }
fi

echo "Pushing to origin/$BRANCH..."
git push origin "$BRANCH"
echo "Push completed successfully to origin/$BRANCH"
