
import os

import pytest
import app.models
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from main import app


load_dotenv()


@pytest.fixture(scope="session")
def test_engine():
    """Create a dedicated engine for the testing database."""

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))
    test_db_name = "filmlog_test"

    if not db_user or not db_password:
        raise RuntimeError(
            "DB_USER dan DB_PASSWORD harus tersedia di .env"
        )

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=test_db_name,
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    # Ensure that destructive setup operations target only the test database.
    if engine.url.database != "filmlog_test":
        raise RuntimeError("Testing database tidak valid.")

    # Reset only the dedicated testing database.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """Provide an isolated database transaction for each test."""

    connection = test_engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        bind=connection,
        autocommit=False,
        autoflush=False,
        join_transaction_mode="create_savepoint",
    )

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    """Provide a FastAPI test client using the testing database."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
