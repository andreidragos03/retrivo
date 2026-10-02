import os
import pytest

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from collections.abc import Generator
from fastapi.testclient import TestClient

from app.models.base import Base
from app.dependencies import get_db
from app.main import app


load_dotenv()


@pytest.fixture(scope = "session")
def test_engine():
    test_database_url = os.getenv("TEST_DATABASE_URL")

    if test_database_url is None:
        raise RuntimeError("TEST_DATABASE_URL is not set")

    engine = create_engine(test_database_url)

    Base.metadata.create_all(bind = engine)

    yield engine

    engine.dispose()


@pytest.fixture
def db(test_engine) -> Generator[Session, None, None]:
    testing_session_local = sessionmaker(
        bind = test_engine,
        autoflush = False,
        autocommit = False,
    )

    session = testing_session_local()

    try:
        yield session
    finally:
        session.rollback()

        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())

        session.commit()
        session.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
