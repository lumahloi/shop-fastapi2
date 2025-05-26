from sqlmodel import SQLModel, create_engine
from sqlalchemy import text

postgresql_file_name = "shop-fastapi"
port = 5432
host = 'localhost'
user = 'postgres'
password = 1234567890

postgresql_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{postgresql_file_name}"
engine = create_engine(postgresql_url)


def create_db_and_tables():
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.commit()
    SQLModel.metadata.create_all(bind=engine)