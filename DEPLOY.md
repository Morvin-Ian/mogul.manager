# Deploying mogul.manager alongside kenyan-fantasy-league

Both stacks share one VPS. KFL owns the public edge; mogul.manager binds
nothing public and is reached through KFL's nginx at
`https://mogul.fantasykenya.com`.

## Port map

| Host binding     | mogul.manager | kenyan-fantasy-league |
|------------------|---------------|-----------------------|
| `0.0.0.0:80/443` | —             | `nginx`               |
| `127.0.0.1:8080` | `mogul-web`   | —                     |
| `127.0.0.1:8001` | `mogul-api`   | —                     |
| `127.0.0.1:5433` | `mogul-db`    | —                     |
| `127.0.0.1:5432` | —             | `postgres-db`         |
| `127.0.0.1:4444` | —             | `selenium`            |

Nothing overlaps. Mogul's three bindings are loopback-only — they exist for
debugging over an SSH tunnel, not for serving traffic:

```sh
ssh -L 8080:localhost:8080 -L 5433:localhost:5433 <vps>
```

Container names (`mogul-api`, `mogul-web`, `mogul-db`), the compose project
(`mogul-prod`, pinned) and its volumes (`mogul-prod_pgdata`,
`mogul-prod_embed_cache`) are all distinct from KFL's, so `docker compose
down` on one stack cannot touch the other's data.

## How traffic flows

```
internet :443 ──> [KFL nginx] ──┬── fantasykenya.com       -> KFL api + Vue
                                └── mogul.fantasykenya.com -> mogul-web:80
                                                              ├── /api/ -> mogul-api:8000
                                                              └── /     -> built Vue SPA
```

The SPA calls a relative `/api`, so it is same-origin with the API — no CORS
preflights and the refresh cookie just works. `mogul-web` joins KFL's
`fpl-vue` network (declared as the external `edge` network in
`docker-compose.prod.yml`), which is how KFL's nginx resolves `mogul-web`.

## First deploy

**1. Clone and configure**

```sh
git clone <repo> ~/mogul.manager && cd ~/mogul.manager
cp .env.prod.example .env.prod
chmod 600 .env.prod
```

Fill in `.env.prod`. Generate each secret separately:

```sh
openssl rand -hex 32   # SECRET_KEY
openssl rand -hex 32   # REFRESH_SECRET_KEY  (must differ)
openssl rand -hex 24   # POSTGRES_PASSWORD   (also goes in DATABASE_URL)
```

The S3 block has no defaults in `config.py` — the API will refuse to start
until `S3_ACCOUNT_ID`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`,
`S3_BUCKET_NAME` and `S3_CUSTOM_DOMAIN` are all set.

**2. Confirm the shared network name**

```sh
docker network ls | grep fpl-vue
```

If it isn't `kenyan-fantasy-league_fpl-vue`, set `EDGE_NETWORK` in `.env.prod`
to the real name. The KFL stack must be up first — mogul declares that
network as external and will not create it.

**3. Bring the stack up**

Always pass `--env-file`. Compose interpolation (the `${POSTGRES_USER}` in
`docker-compose.prod.yml`) reads that flag, *not* the `env_file:` key:

```sh
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

Migrations run automatically — `/start` does `alembic upgrade head` before
launching the server.

**4. Verify before touching the edge**

```sh
curl -s localhost:8080/health          # {"status":"ok"}
curl -sI localhost:8080/ | head -1     # 200, the SPA
```

**5. Wire up KFL's nginx**

DNS first: an `A` record for `mogul.fantasykenya.com` pointing at the VPS.
Then follow the header of [`deploy/kfl-nginx-mogul.conf`](deploy/kfl-nginx-mogul.conf)
— copy the file into KFL's `docker/production/nginx/`, add one volume mount
to KFL's nginx service, issue the cert through the existing certbot webroot,
and reload. KFL's certbot container renews it on the same 12h loop as
`fantasykenya.com`; no second certbot is needed.

## Updating

```sh
cd ~/mogul.manager && git pull
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

The API image rebuild re-downloads the embedding model only if
`pyproject.toml`/`uv.lock` changed; otherwise that layer is cached, and the
`embed_cache` volume keeps the runtime copy across container replacements.

## Monitoring (maajun)

`maajun add-repo` registers a repo but writes no `[github.repos.deployment]`
block, so the daemon has no idea where the app runs, which containers are its
own, or where to read logs — it can only react to what shows up on GitHub.
`scripts/maajun-register.py` fills that in. Run it on the VPS:

```sh
./scripts/maajun-register.py \
  --repo Morvin-Ian/mogul.manager \
  --path /root/mogul.manager \
  --runs "docker compose --env-file .env.prod -f docker-compose.prod.yml" \
  --stack "FastAPI + Uvicorn (single worker), Vue 3 SPA built static and served by nginx, PostgreSQL 17 + pgvector" \
  --port 8080 \
  --container mogul-web --container mogul-api --container mogul-db
```

Add `--dry-run` first to see the diff. It backs up the config, writes
atomically, and re-parses the result before replacing the original.

Three values differ from the kenyan-fantasy-league entry, deliberately:

- `--runs` carries `--env-file .env.prod -f docker-compose.prod.yml`. A bare
  `docker compose` in that directory picks up the *dev* compose file and
  interpolates blank Postgres credentials.
- `--port 8080`, not 80. Nothing here binds a public port; `mogul-web` is on
  `127.0.0.1:8080`, where `/health` answers.
- No `--log-file`. This stack logs to stdout, captured by Docker; there are no
  on-disk logs like KFL's `celery.log`. It reads logs via the container names.

`mode` is left at `suggest`. Fix mode wants a `--test-command` to gate on, and
this repo has no test suite yet; until it does, the daemon would be proposing
patches with nothing to check them against — on a stack that shares an nginx
edge with fantasykenya.com.

---

## Notes

- **The API runs a single worker, deliberately.** `main.py`'s lifespan owns
  process-local state that does not survive a fork: the periodic document
  requeue loop, the in-memory write rate limiter, and the SSE subscriber
  registry behind `/api/notifications/stream`. Extra workers would each
  requeue the same documents and would only see events raised in their own
  process. Put a shared broker behind those before scaling out.
- **`COOKIE_SECURE=true`** is set explicitly. `config.py` would otherwise
  infer it from the `FRONTEND_URL` scheme; being explicit means a typo in
  that URL cannot silently drop the `Secure` flag from auth cookies.
- **Uploads cap at 5 MiB** (`MAX_UPLOAD_SIZE_BYTES`). Both nginx hops allow
  8 MiB to leave room for the multipart envelope. Raise all three together.
- **Backups.** Mogul's data lives in the `mogul-prod_pgdata` volume:
  ```sh
  docker exec mogul-db pg_dump -U mogul mogul_manager | gzip > mogul-$(date +%F).sql.gz
  ```
