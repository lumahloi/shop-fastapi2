from sqlmodel import SQLModel, create_engine

postgresql_file_name = "shop-fastapi"
port = 5432
host = 'localhost'
user = 'postgres'
password = 1234567890

postgresql_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{postgresql_file_name}"
engine = create_engine(postgresql_url)


def create_db_and_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)