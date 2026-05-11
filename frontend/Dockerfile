FROM node:24-alpine AS builder
WORKDIR /app
COPY package*.json ./
# npm ci может быть нестабилен в Docker; используем install с очисткой кэша
RUN npm cache clean --force && \
    npm install --no-optional --legacy-peer-deps && \
    npm cache clean --force
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
