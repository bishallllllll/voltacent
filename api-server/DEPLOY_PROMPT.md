# PROMPT — Deploy the Voltacent Triad API on the Lightsail VPS

Copy everything below the line into the VPS (or hand it to whoever runs the box).
Target machine: AWS Lightsail `shuck-engine-5ers` (us-east-1, Ubuntu 24.04),
as user `ubuntu`. The shuck-engine checkout at `/home/ubuntu/shuck-engine`
must already exist with its Python deps installed (xgboost, pandas,
clickhouse-connect, pyyaml) and its ClickHouse Cloud connection working.

---

## 1. Copy the server files

From your local machine (the `voltacent-api-server.zip` is attached):

```bash
scp voltacent-api-server.zip ubuntu@<vps-ip>:/home/ubuntu/
ssh ubuntu@<vps-ip>
cd /home/ubuntu
unzip -o voltacent-api-server.zip
# -> /home/ubuntu/api-server/{app.py, triad.py, keys.py, requirements.txt, README.md, systemd/}
mv api-server voltacent-api
```

## 2. Python environment

```bash
cd /home/ubuntu/voltacent-api
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Reuse the engine's packages if already present for the ubuntu user:
# pip install xgboost pandas clickhouse-connect pyyaml   (only if missing)
```

## 3. Smoke test — load the REAL triad (fail-closed)

This imports shuck-engine's actual inference modules and loads all three
models. If anything is missing or a checksum fails, it exits non-zero —
do NOT proceed until this prints a health dict.

```bash
source .venv/bin/activate
SHUCK_ENGINE_DIR=/home/ubuntu/shuck-engine python3 -c "
from triad import TriadEngine
e = TriadEngine()
print(e.health())
print('signals:', len(e.signals(['EUR_USD'])))
"
```

Expected: a health dict with the three model versions, and 1 signal row.
If `TriadError` mentions a DataFrame column mismatch, open `triad.py` and
adjust `_col()` to the actual column names from `predict_latest_bar`.

## 4. Install as a systemd service

```bash
sudo cp /home/ubuntu/voltacent-api/systemd/voltacent-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now voltacent-api.service
systemctl status voltacent-api.service --no-pager | head -15
curl -s http://127.0.0.1:18900/v1/health
```

Expected: `{"status":"ok","models":{...},"threshold":0.62,...}`.

## 5. Issue the first API key (localhost only)

```bash
curl -s -X POST "http://127.0.0.1:18900/admin/keys?name=founder&tier=live"
```

Response contains `api_key` (starts with `vc_`) — **copy it now, it is shown
once and only the hash is stored.** Issue sandbox keys the same way with
`tier=sandbox`.

## 6. Test authenticated endpoints

```bash
KEY="vc_paste_yours_here"
curl -s -H "X-API-Key: $KEY" "http://127.0.0.1:18900/v1/signals/latest?instruments=EUR_USD,GBP_USD" | head -c 600; echo
curl -s -H "X-API-Key: $KEY" "http://127.0.0.1:18900/v1/magnitude/forecast?instruments=EUR_USD" | head -c 400; echo
curl -s -H "X-API-Key: $KEY" "http://127.0.0.1:18900/v1/volatility/forecast?instruments=EUR_USD" | head -c 400; echo
# No key -> 401. Wrong key -> 401. Hammer it -> 429 after the tier limit.
curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:18900/v1/signals/latest"
```

## 7. Public exposure (TLS)

The service binds to 127.0.0.1 only. Put Caddy in front:

```bash
sudo apt install -y caddy
sudo tee /etc/caddy/Caddyfile <<'EOF'
api.voltacent.example {
    reverse_proxy 127.0.0.1:18900
}
EOF
# Replace api.voltacent.example with the real domain, then:
sudo systemctl reload caddy
```

Caddy provisions TLS automatically. Keep `/admin/*` unreachable from the
public internet — key issuance stays localhost-only. (Caddyfile above exposes
everything; add `handle /admin/* { abort }` before the reverse_proxy if the
API shares a domain with anything else.)

## 8. Done checklist

- [ ] `systemctl is-active voltacent-api.service` → `active`
- [ ] `/v1/health` returns `status: ok` with 3 model versions
- [ ] Live key returns signals for 2 instruments
- [ ] Sandbox key returns the snapshot note, not live data
- [ ] No key → 401
- [ ] Public URL serves TLS, `/admin/keys` not reachable externally

## If something breaks

- `journalctl -u voltacent-api.service -n 50 --no-pager` — startup errors land here.
- `TriadError` at startup = a model leg failed to load; the service refuses to
  serve rather than serving partial data. Fix the leg, restart.
- Memory: if the 2GB box strains, edit the service file
  (`--workers 2` → `--workers 1`), `daemon-reload`, restart.
