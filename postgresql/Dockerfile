FROM postgres:9.6
COPY postgresql.conf /tmp/postgresql.conf
COPY updateConfig.sh /docker-entrypoint-initdb.d
COPY init.sql /docker-entrypoint-initdb.d
