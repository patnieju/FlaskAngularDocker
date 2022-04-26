#stage 1
FROM node:12.22 as node
WORKDIR /app
COPY . .
EXPOSE 4200
RUN npm install --no-optional -f
RUN npm run build --prod
RUN npm install -g @angular/cli

CMD ng serve --host 0.0.0.0 --disable-host-check --proxy-config proxy.conf.json
