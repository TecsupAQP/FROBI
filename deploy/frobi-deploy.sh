#!/usr/bin/env bash
# The only command the GitHub Actions key may run on the server (authorized_keys: command=...).
# Installed as ~/bin/frobi-deploy (see deploy/README.md, «Despliegue automático»).
#
# stdin:                  the images (docker save frobi-web frobi-api | gzip)
# SSH_ORIGINAL_COMMAND:   the commit to deploy (40 hex characters)
set -euo pipefail

sha="${SSH_ORIGINAL_COMMAND:-}"
[[ "$sha" =~ ^[0-9a-f]{40}$ ]] || { echo "commit inválido" >&2; exit 2; }

cd "$HOME/FROBI"
gunzip | docker load
git fetch -q origin main
git checkout -q --detach "$sha"
docker compose -f deploy/compose.yml --env-file deploy/.env up -d --no-build --remove-orphans
docker image prune -f >/dev/null

for _ in $(seq 1 30); do
  if docker compose -f deploy/compose.yml --env-file deploy/.env exec -T api python -c \
      "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health', timeout=3)" \
      2>/dev/null; then
    echo "desplegado $sha"
    exit 0
  fi
  sleep 2
done
echo "la API no respondió a tiempo" >&2
exit 1
