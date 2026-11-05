# Despliegue en un VPS

Todo FROBI en un servidor con Docker: Caddy sirve el front y pasa `/api/*` al backend, con
HTTPS automático si tienes dominio. Postgres y Redis no se exponen a internet.

```
internet ──80/443──▶ Caddy (web) ──/api, /docs──▶ api (FastAPI) ──▶ postgres, redis
                         └── todo lo demás: el front (Vue)
```

## Requisitos

- Un VPS con Linux y al menos 1 GB de RAM (2 GB es más cómodo para compilar).
- Docker con el plugin Compose: <https://docs.docker.com/engine/install/>
- Los puertos 80 y 443 abiertos en el firewall del VPS.
- Opcional: un dominio con un registro **A** apuntando a la IP del VPS.

## Primera vez

```bash
git clone https://github.com/TecsupAQP/FROBI.git
cd FROBI
cp deploy/.env.example deploy/.env
nano deploy/.env
```

En `deploy/.env` llena:

| Variable | Qué poner |
| --- | --- |
| `FROBI_DOMAIN` | Tu dominio (`frobi.midominio.com`). Vacío = http con la IP del VPS. |
| `POSTGRES_PASSWORD` | Una contraseña larga. Genera una con `openssl rand -hex 24`. |
| `FROBI_LLM_API_KEY` | Tu clave de la API de Claude (`sk-ant-…`). Vacía = respaldos sin IA. |
| `FROBI_ENVIRONMENT` | `demo` para la presentación (acceso demo activo) o `production`. |

Levanta todo (la primera vez tarda unos minutos en compilar):

```bash
docker compose -f deploy/compose.yml --env-file deploy/.env up -d --build
```

La API aplica las migraciones sola al arrancar. Carga los datos de la clase demo una vez:

```bash
docker compose -f deploy/compose.yml --env-file deploy/.env exec api python -m frobi.demo
```

Abre `https://tu-dominio` (o `http://IP-del-VPS`). La documentación de la API queda en `/docs` y
el estado en `/api/v1/health`.

## Actualizar

```bash
git pull
docker compose -f deploy/compose.yml --env-file deploy/.env up -d --build
```

## VPS pequeño (menos de 2 GB de RAM)

Compilar el front en el servidor puede quedarse sin memoria. Construye las imágenes en tu compu y
pásalas por SSH (`combi` es el nombre del host en `~/.ssh/config`):

```bash
# En tu compu (Git Bash), desde la raíz del repo
POSTGRES_PASSWORD=solo-para-construir docker compose -f deploy/compose.yml build
docker save frobi-web:latest frobi-api:latest | gzip -1 | ssh combi 'gunzip | docker load'

# En el servidor
cd ~/FROBI && git pull
docker compose -f deploy/compose.yml --env-file deploy/.env up -d --no-build
```

Esa contraseña solo sirve para que Compose acepte construir y no queda en las imágenes: la
contraseña y la clave reales se leen del `deploy/.env` del servidor al levantar. Cada contenedor tiene un tope de memoria
(`mem_limit`); en total FROBI usa unos 150 MB.

## Despliegue automático (GitHub Actions)

[`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) despliega cada push a `main`
cuando el CI pasa (y a mano desde la pestaña **Actions → Deploy → Run workflow**). Construye las
imágenes en GitHub, las manda por SSH y el servidor las levanta. La clave de Claude y la
contraseña de la base se quedan en `deploy/.env` del servidor: GitHub no las ve nunca.

Se configura una sola vez:

1. **Llave de despliegue.** En tu compu: `ssh-keygen -t ed25519 -N "" -C github-actions-frobi-deploy -f ~/.ssh/frobi_deploy`.
2. **En el servidor**, instala el script y autoriza esa llave *solo* para ejecutarlo:

   ```bash
   cd ~/FROBI && git pull && install -D -m 700 deploy/frobi-deploy.sh ~/bin/frobi-deploy
   echo 'command="/home/azureuser/bin/frobi-deploy",no-port-forwarding,no-X11-forwarding,no-agent-forwarding,no-pty,no-user-rc <contenido de frobi_deploy.pub>' >> ~/.ssh/authorized_keys
   ```

   Con `command=` esa llave no abre una terminal ni ejecuta otra cosa que el despliegue.
3. **En GitHub:** *Settings → Secrets and variables → Actions → New repository secret*, nombre
   `DEPLOY_SSH_KEY`, valor: el contenido completo de `~/.ssh/frobi_deploy` (la privada).

Si cambias de servidor, actualiza `DEPLOY_HOST` y `DEPLOY_HOST_KEY` en el workflow
(`ssh-keyscan -t ed25519 <ip>`). Si cambias `deploy/frobi-deploy.sh`, vuelve a correr el
`install` del paso 2.

## Comandos útiles

```bash
# Estado y registros
docker compose -f deploy/compose.yml --env-file deploy/.env ps
docker compose -f deploy/compose.yml --env-file deploy/.env logs -f api

# Reiniciar la clase demo desde cero
docker compose -f deploy/compose.yml --env-file deploy/.env exec api python -m frobi.demo --reset

# Respaldo de la base
docker compose -f deploy/compose.yml --env-file deploy/.env exec postgres pg_dump -U frobi frobi > respaldo.sql
```

## Seguridad

- `deploy/.env` tiene la clave de Claude y la contraseña de la base: no lo subas nunca al repo
  (ya está en `.gitignore`). Si la clave se filtra, revócala en la consola de Anthropic.
- Cambiar la clave de Claude: edita `deploy/.env` y vuelve a correr el `up -d`.
- No cambies `POSTGRES_PASSWORD` después de la primera vez: la base ya se creó con ella.
- `FROBI_ENVIRONMENT=demo` deja entrar a cualquiera como docente demo (`POST /sessions/demo`).
  Está bien para la hackatón; para un uso real pon `production`.
