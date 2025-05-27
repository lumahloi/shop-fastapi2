# Shop FastAPI
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#) [![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](#) [![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)](#) [![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](#)

## Tecnologias utilizadas
- **Backend**: Python;
  - FastAPI, Pytest, bcrypt.
- **Banco de dados**: PostgreSQL;
- **Conteinerização**: Docker.

## Funcionalidades
- Autenticação, registro e login de usuário;
- Refresh de token JWT;
- Listar todos os clientes, com suporte a paginação e filtro por nome e email;
- Criar um novo cliente, validando email e CPF únicos;
- Obter informações de um cliente específico;
- Atualizar informações de um cliente específico;
- Excluir um cliente;
- Listar todos os produtos, com suporte a paginação e filtros;
- Criar um novo produto;
- Obter informações de um produto específico;
- Atualizar informações de um produto específico;
- Excluir, deletar e atualizar imagens de produtos;
- Excluir um produto;
- Listar todos os pedidos, incluindo filtros;
- Criar um novo pedido contendo múltiplos produtos, validando estoque disponível;
- Obter informações de um pedido específico;
- Atualizar informações de um pedido específico;
- Excluir um pedido.

## Estrutura do projeto
```bash
    shop-fastapi/
    ├── app/                         
    │   ├── endpoints/                → lista de endpoints
    │   │   ├── api_client.py
    │   │   ├── api_order.py
    │   │   ├── api_product.py
    │   │   └── api_user.py
    │   │
    │   ├── models/                   → lista de models
    │   │   ├── model_client.py
    │   │   ├── model_order.py
    │   │   ├── model_product.py
    │   │   └── model_user.py
    │   │
    │   ├── utils/                    → funções auxiliares
    │   │   ├── auth.py         
    │   │   ├── custom_types.py
    │   │   ├── database.py
    │   │   ├── ddependencies.py
    │   │   ├── permissions.py
    │   │   ├── services.py       
    │   │   └── session.py
    │   │
    │   └── main.py
    │  
    ├── tests/                        → lista de testes
    │   ├── conftest.py
    │   ├── tests_clients.py
    │   ├── tests_orders.py
    │   ├── tests_products.py
    │   └── tests_users.py
    │  
    ├── create_db.sh                  
    ├── docker-compose.yml
    ├── Dockerfile
    ├── README.md
    └── requirements.txt
```

## Como rodar localmente
Passo a passo de como rodar o projeto localmente na sua máquina.
### Pré-requisitos
- **Git**: instale a versão mais recente oficial clicando [aqui](https://git-scm.com/downloads);
- **Docker**: instale a versão mais recente oficial clicando [aqui](https://www.docker.com/get-started/);


### Instalação
Clone o repositório.
```bash
git clone https://github.com/lumahloi/shop-fastapi2.git
```

### Rodando localmente
Rode o ```Docker```.
```bash
docker-compose up --build
```

## APIs
Em ```localhost:8000/docs``` é possível visualizar a documentação das APIs.

## Autora
<img src="https://github.com/lumahloi.png" width="80" align="left"/>

***Lumah Pereira***


[![LinkedIn](https://custom-icon-badges.demolab.com/badge/LinkedIn-0A66C2?logo=linkedin-white&logoColor=fff)](https://www.linkedin.com/in/lumah-pereira) [![GitHub](https://img.shields.io/badge/GitHub-%23121011.svg?logo=github&logoColor=white)](https://www.github.com/lumahloi) [![Portfolio](https://img.shields.io/badge/Portfolio-D47CBC.svg?logo=vercel&logoColor=white)](https://www.lumah-pereira.vercel.app)
