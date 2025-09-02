# Shop FastAPI
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#) [![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](#) [![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)](#) [![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](#)

## Technologies
- **Backend**: Python;
- FastAPI, Pytest.
- **Database**: PostgreSQL;
- **Containerization**: Docker.

## Functionalities
- User authentication, registration, and login;
- JWT token refresh;
- List all customers, with support for paging and filtering by name and email;
- Create a new customer, validating unique email and CPF numbers;
- Get information for a specific customer;
- Update information for a specific customer;
- Delete a customer;
- List all products, with support for paging and filters;
- Create a new product;
- Get information for a specific product;
- Update information for a specific product;
- Delete, delete, and update product images;
- Delete a product;
- List all orders, including filters;
- Create a new order containing multiple products, validating available inventory;
- Get information for a specific order;
- Update information for a specific order;
- Delete an order.

## Structure
```bash
    shop-fastapi/
    ├── app/                         
    │   ├── endpoints/                → endpoints list
    │   │   ├── api_client.py
    │   │   ├── api_order.py
    │   │   ├── api_product.py
    │   │   └── api_user.py
    │   │
    │   ├── models/                   → models list
    │   │   ├── model_client.py
    │   │   ├── model_order.py
    │   │   ├── model_product.py
    │   │   └── model_user.py
    │   │
    │   ├── utils/                    → auxiliar functions
    │   │   ├── auth.py         
    │   │   ├── custom_types.py
    │   │   ├── database.py
    │   │   ├── dependencies.py
    │   │   ├── permissions.py
    │   │   ├── services.py       
    │   │   └── session.py
    │   │
    │   └── main.py
    │  
    ├── tests/                        → test list
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

## How to Run Locally
Step-by-step instructions on how to run the project locally on your machine.
### Prerequisites
- **Git**: Install the latest official version by clicking [here](https://git-scm.com/downloads);
- **Docker**: Install the latest official version by clicking [here](https://www.docker.com/get-started/);


### Installation
Clone the repository.
```bash
git clone https://github.com/lumahloi/shop-fastapi2.git
```

### Running Locally
Run ```Docker```.
```bash
docker-compose up --build
```

## APIs
In ```localhost:8000/docs``` you can view the API documentation.

## Author
<img src="https://github.com/lumahloi.png" width="80" align="left"/>

***Lumah Pereira***


[![LinkedIn](https://custom-icon-badges.demolab.com/badge/LinkedIn-0A66C2?logo=linkedin-white&logoColor=fff)](https://www.linkedin.com/in/lumah-pereira) [![GitHub](https://img.shields.io/badge/GitHub-%23121011.svg?logo=github&logoColor=white)](https://www.github.com/lumahloi) [![Portfolio](https://img.shields.io/badge/Portfolio-D47CBC.svg?logo=vercel&logoColor=white)](https://www.lumah-pereira.vercel.app)
