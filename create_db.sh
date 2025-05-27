#!/bin/bash

# Aguarda o PostgreSQL ficar disponível
until pg_isready -h postgres -p 5432 -U postgres; do
  echo "Aguardando o PostgreSQL ficar disponível..."
  sleep 2
done

# Cria o banco se não existir
psql -h postgres -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'shop-fastapi'" | grep -q 1 || \
psql -h postgres -U postgres -c "CREATE DATABASE \"shop-fastapi\""

echo "Banco de dados 'shop-fastapi' verificado/criado com sucesso"