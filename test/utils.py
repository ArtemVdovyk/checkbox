import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

from database import Base
from main import app
from models import Receipts, Users
from routers.auth import bcrypt_context


DB_USERNAME = "postgres"
DB_PASSWORD = "password"
DB_NAME = "TestCheckboxDatabase"
DB_HOST = "localhost"
DB_PORT = 5432

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False,
                                   autoflush=False,
                                   bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"username": "testuser", "id": 1, "is_admin": True}


client = TestClient(app)


@pytest.fixture(autouse=True)
def test_user(request):
    user = Users(
        id=1,
        username="testuser",
        email="testuser@gmail.com",
        first_name="test",
        last_name="user",
        hashed_password=bcrypt_context.hash("testpassword"),
        is_admin=True
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()


@pytest.fixture()
def test_receipt():
    db = TestingSessionLocal()
    receipt = Receipts(
        id=uuid.UUID("daafa0dc-06bb-40fd-8472-c8fa6ed47a43"),
        products=[
            {
                "name": "Bar of chocolate",
                "price": 10.38,
                "quantity": 2.0,
                "total": 20.76
            },
            {
                "name": "Bottle of sparkling water",
                "price": 5.65,
                "quantity": 3.0,
                "total": 16.95
            }
        ],
        payment={"type": "cash", "amount": 40.00},
        total=37.71,
        rest=2.29,
        created_at="2024-03-06 17:29:59.073344",
        owner_id=1
    )

    db.add(receipt)
    db.commit()
    yield receipt
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM receipts;"))
        connection.commit()
