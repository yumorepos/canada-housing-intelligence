#!/usr/bin/env bash
set -euo pipefail

echo "[vercel-ignore] This repository is a Streamlit-first app (entrypoint: app/main.py)."
echo "[vercel-ignore] Vercel preview builds are intentionally skipped to avoid fake backend deployment."
# Vercel ignores deployment when ignoreCommand exits 0.
exit 0
