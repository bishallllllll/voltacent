# Deploy the Voltacent Triad API on Render

## What this is

The API runs on Render (starter web service, ~$7/mo + ~$0.10/mo for the key
disk) instead of the Lightsail VPS. The trading engine stays untouched on
Lightsail — public API and live trading never share a box.

## Your steps (nothing here needs the terminal)

### 1. Create the repo

Create a **private** GitHub repo `bishallllllll/voltacent-api` and upload the
contents of `voltacent-api-render.zip` to it (all files at the repo root).

### 2. Create a Render account

Sign up at render.com. Connect your GitHub account when prompted.

### 3. Create a read-only GitHub token

GitHub → Settings → Developer settings → Personal access tokens →
Fine-grained tokens → Generate new token:
- Repository access: **only** `bishallllllll/shuck-engine`
- Permissions: Contents → **Read-only**
- Copy the token (starts with `github_pat_`). You will paste it into Render,
  never into chat.

### 4. Deploy via Blueprint

Render dashboard → New → Blueprint → select the `voltacent-api` repo.
Render reads `render.yaml` and creates the web service + persistent disk.

### 5. Set secret env vars

In the service's Environment tab, fill in:
- `GITHUB_TOKEN` — the token from step 3
- `CLICKHOUSE_HOST`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD` — your
  ClickHouse Cloud credentials (same values the engine uses on Lightsail)
- Any other env vars the engine's loader needs (copy from the VPS setup)

Then **Manual Deploy → Deploy latest commit**.

### 6. Verify

- `https://<your-service>.onrender.com/v1/health` → `{"status":"ok",...}`
  with all three model versions.
- Issue your first key from the Render **Shell** tab:
  `curl -s -X POST "http://localhost:10000/admin/keys?name=founder&tier=live"`
  (Render sets `$PORT`; the shell listens on localhost. Copy the `vc_` key —
  shown once.)
- Authenticated test:
  `curl -H "X-API-Key: vc_..." "http://localhost:10000/v1/signals/latest?instruments=EUR_USD"`

### 7. Custom domain (later)

Render dashboard → service → Settings → Custom Domain. Point your DNS at
Render; TLS is automatic.

## Costs

- Web service (starter): ~$7/mo, no sleep
- Persistent disk 1 GB (SQLite key DB): ~$0.10/mo
- No Postgres needed at this scale

## Notes

- The build clones `shuck-engine` fresh on every deploy, so engine updates
  reach the API automatically — but model files also redeploy, which takes
  a few minutes on Render's build.
- Keys live on the persistent disk at `/var/data/keys.db` and survive
  deploys. If you ever delete the disk, all keys are gone — reissue them.
- `/admin/*` has no auth gate beyond being unlisted; do not add a public
  route to it. Key issuance stays via the Render Shell.
