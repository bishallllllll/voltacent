#!/usr/bin/env bash
# Render build script: install deps, then clone the private shuck-engine repo
# for its inference modules and model artifacts.
#
# Requires GITHUB_TOKEN env var: a fine-grained personal access token with
# read-only access to bishallllllll/shuck-engine. Set it in the Render
# dashboard (never commit it).
set -euo pipefail

pip install --upgrade pip
pip install -r requirements.txt

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "ERROR: GITHUB_TOKEN is not set. Cannot clone shuck-engine." >&2
  exit 1
fi

ENGINE_DIR="${SHUCK_ENGINE_DIR:-/opt/shuck-engine}"
if [ -d "$ENGINE_DIR/.git" ]; then
  echo "Updating existing shuck-engine checkout..."
  git -C "$ENGINE_DIR" pull --ff-only
else
  echo "Cloning shuck-engine..."
  git clone "https://x-access-token:${GITHUB_TOKEN}@github.com/bishallllllll/shuck-engine.git" "$ENGINE_DIR"
fi

# Fail the build early if the production model legs are missing.
test -f "$ENGINE_DIR/models/xgboost_reg.pkl" || { echo "ERROR: regression model missing in checkout" >&2; exit 1; }
echo "Build OK."
