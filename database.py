import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://sasori:sasori@localhost:5432/telemetry_db"
)

# Engine manages the pool of raw DB connections
engine = create_engine(DATABASE_URL)

# SessionLocal is the factory for individual database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our models will inherit from
Base = declarative_base()


# Dependency to yield an isolated DB session per request, closing it afterward
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()