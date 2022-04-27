# FlaskAngularDocker

### Angular application with a API backend and a Postgresql database

Project structure:
```
.
├── docker-compose.yaml
├── .env_docker
├── ...
├── backend
│   ├── Dockerfile
│   ├── .dockerignore
│   ...
├── postgresql
│   ├── Dockerfile
│   ├── .dockerignore
│   ...
├── frontend
│   ├── ...
│   ├── .dockerignore
│   └── Dockerfile
└── README.md
```
[_docker-compose.yaml_](docker-compose.yaml)
```
services:
  postgres:
    build: ./postgres
    ports: 5454:5432
    env_file: .env_docker
    ...
  backend:
    image: ubuntu:20.04
    build: ./backend
    ports: 8081:8081
    env_file: .env_docker
    links: postgres
    ...
  frontend:
    image: node:12.22
    build: ./frontend
    ports: 4200:4200
    env_file: .env_docker
    link: backend
...
```
## Steps
```
$ https://github.com/eusebiomarquesbenitez/FlaskAngularDocker
$ cd FlaskAngularDocker
```
## Deploy with docker-compose
```
$ sudo docker-compose build --no-cache && sudo docker-compose up -d --force-recreate
```
## Images Processed
```
$ sudo docker images
REPOSITORY TAG IMAGE ID CREATED SIZE
frontend-angular latest 815bfd3c2431 17 minutes ago 2.31GB
backend-flask latest 838264c4d440 19 minutes ago 717MB
mercadona_postgres latest 978bf016f2c4 21 minutes ago 200MB
```
## Docker Proceses in Deploy
```
$ sudo docker ps -a
CONTAINER ID IMAGE COMMAND CREATED STATUS PORTS NAMES
cfecb5b158ae frontend-angular "docker-entrypoint.s…" 10 minutes ago Up 10 minutes 0.0.0.0:4200->4200/tcp, :::4200->4200/tcp frontend-app
8e1ab4b6917d backend-flask "/bin/sh -c 'python3…" 11 minutes ago Up 11 minutes (unhealthy) 0.0.0.0:8081->8081/tcp, :::8081->8081/tcp backend-app
f593228ca3e5 mercadona_postgres "docker-entrypoint.s…" 11 minutes ago Up 11 minutes (healthy) 0.0.0.0:5454->5432/tcp, :::5454->5432/tcp postgres
```

## Stop and remove the containers
```
$ sudo docker-compose down
```
## To Access Postgre SQL
```
$ postgresql://localhost:5454
```
## To Access Angular Frontend
```
$ firefox http://localhost:4200
```
## To Access Flask Python Server Backend
```
$ firefox http://localhost:8181
```
## Project API:
```
.
├── FLASK 
      ├── [GET]: http://localhost:8181/api/data?[id]
      ├── [GET,POST]: http://localhost:8181/api/delete?[id]
      ├── [POST]: http://localhost:8181/api/add?[Product]
      ├── [POST]: http://localhost:8181/api/update?[Product]
      ├── [GET]: http://localhost:8181/api/image?[id]
      ├── [POST]: http://localhost:8181/api/exist?[id]
```
