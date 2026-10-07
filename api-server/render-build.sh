#!/usr/bin/env bash
# Render build: install deps, clone shuck-engine, download model binaries
# from Hugging Face (they are gitignored by design and never live in git).
#
# Required env vars (set in Render dashboard, never committed):
#   GITHUB_TOKEN  - fine-grained PAT, read-only on bishallllllll/shuck-engine
#   HF_REPO_ID    - Hugging Face repo holding the model files, e.g. bishallllllll/voltacent-models
#   HF_TOKEN      - (optional) Hugging Face token, only if the repo is private
set -euo pipefail

pip install -r requirements.txt

# --- engine code -------------------------------------------------------
: "${GITHUB_TOKEN:?GITHUB_TOKEN is not set}"
ENGINE_DIR="${SHUCK_ENGINE_DIR:-/opt/shuck-engine}"
if [ -d "$ENGINE_DIR/.git" ]; then
  echo "Updating existing shuck-engine checkout..."
  git -C "$ENGINE_DIR" pull --ff-only
else
  echo "Cloning shuck-engine..."
  git clone "https://x-access-token:${GITHUB_TOKEN}@github.com/bishallllllll/shuck-engine.git" "$ENGINE_DIR"
fi

# --- model binaries from Hugging Face ----------------------------------
: "${HF_REPO_ID:?HF_REPO_ID is not set}"
AUTH=()
if [ -n "${HF_TOKEN:-}" ]; then AUTH=(-H "Authorization: Bearer ${HF_TOKEN}"); fi

dl() { # dl <hf-filename> <dest-path> [expected-sha256]
  local src="$1" dest="$2" want="${3:-}"
  echo "Downloading ${src} ..."
  curl -sfL "${AUTH[@]}" \
    "https://huggingface.co/${HF_REPO_ID}/resolve/main/${src}" -o "$dest"
  if [ -n "$want" ]; then
    local got
    got=$(sha256sum "$dest" | cut -d' ' -f1)
    if [ "$got" != "$want" ]; then
      echo "ERROR: SHA256 mismatch for ${dest}" >&2
      echo "  expected: ${want}" >&2
      echo "  got:      ${got}" >&2
      exit 1
    fi
    echo "SHA256 OK: ${dest}"
  else
    echo "Downloaded: ${dest} ($(du -h "$dest" | cut -f1))"
  fi
}

mkdir -p "$ENGINE_DIR/models"
# Model downloads are best-effort for now — the service runs without models
# (degraded) and they are added later via HF. Nothing here fails the build.
dl "xgboost_fold11_20260904_094734.pkl" "$ENGINE_DIR/models/xgboost_fold11.pkl" \
  || echo "WARNING: classifier not on HF yet — direction leg disabled."
dl "xgboost_reg.pkl" "$ENGINE_DIR/models/xgboost_reg.pkl" \
  "8aa938f601f42d5ab3681fcef4f3268d110ef023b73660b9fe8ee59f067ddf8c" \
  || echo "WARNING: xgboost_reg.pkl not on HF yet — magnitude leg disabled."
dl "xgboost_vol.pkl" "$ENGINE_DIR/models/xgboost_vol.pkl" \
  "f2dcdbf1427122ff44d4484e4217fec698f70791ecbdc9e8206f23d75c1fa12a" \
  || echo "WARNING: xgboost_vol.pkl not on HF yet — volatility leg disabled."

echo "Build OK."
