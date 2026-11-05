# Front compilado y servido por Caddy, que además pasa /api/* al backend (deploy/compose.yml).
# Front y API comparten dominio, así que la API se llama con una ruta relativa y no hace falta CORS.

FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM caddy:2-alpine
COPY --from=build /app/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile
