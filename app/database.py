import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your PostgreSQL credentials in .env or update this string
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# def get_db():
#     import time

#     start = time.perf_counter()

#     db = SessionLocal()

#     print(
#         f"SessionLocal(): {(time.perf_counter() - start) * 1000:.2f} ms"
#     )

#     try:
#         yield db
#     finally:
#         start = time.perf_counter()

#         db.close()

#         print(
#             f"db.close(): {(time.perf_counter() - start) * 1000:.2f} ms"
#         )
