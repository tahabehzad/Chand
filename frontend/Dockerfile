FROM node:22-alpine AS build

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@9.15.9 --activate

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# Production serve stage using nginx
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY --from=build /app/public /usr/share/nginx/html

RUN echo 'server { \
    listen 5273; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index chand.html index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /api/ { \
        proxy_pass http://backend:8000/api/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
    location /health/ { \
        proxy_pass http://backend:8000/health/; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 5273

CMD ["nginx", "-g", "daemon off;"]
