#!/bin/bash
set -e

ollama serve > /tmp/ollama.log 2>&1 &

for i in $(seq 1 60); do
  if curl -sf http://localhost:11434 >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

ollama pull qwen3:4b || true

streamlit run My\ AI.py --server.address=0.0.0.0 --server.port=${PORT:-8080}
