
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env
load_dotenv()

# PostgreSQL configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# Validate required environment variables
required_variables = {
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_NAME": DB_NAME,
}

missing_variables = [
    name for name, value in required_variables.items() if not value
]

if missing_variables:
    raise RuntimeError(
        f"Missing database environment variables: {', '.join(missing_variables)}"
    )

# Build PostgreSQL connection URL safely
from sqlalchemy.engine import URL

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

# Create database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for database models
Base = declarative_base()


# Dependency for FastAPI database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
