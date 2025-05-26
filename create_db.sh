#!/bin/bash

until pg_isready -h postgres -p 5432 -U postgres; do
  echo "Aguardando o PostgreSQL ficar disponível..."
  sleep 2
done

psql -h postgres -U postgres -c "CREATE DATABASE shop-fastapi;"

# Opcional: Executa migrações ou scripts SQL adicionais
# psql -h postgres -U postgres -d meubanco -f /app/scripts/init.sql