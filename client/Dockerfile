FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Этап 2: Раздача через Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
# Копируем наш конфиг (если он есть локально) или используем дефолтный
# В нашем случае конфиг приходит из ConfigMap в K8s, поэтому здесь можно ничего не менять
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]