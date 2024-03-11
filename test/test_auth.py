import pytest
from datetime import timedelta
from fastapi import HTTPException, status
from jose import jwt

from routers.auth import (
    authenticate_user,
    create_access_token,
    get_db,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
    Token
)
from .utils import *


app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user_valid_credentials(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(test_user.username,
                                           "testpassword", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username


def test_authenticate_user_invalid_username(test_user):
    db = TestingSessionLocal()
    non_existent_user = authenticate_user("invalid_username",
                                          "testpassword", db)
    assert non_existent_user is False


def test_authenticate_user_invalid_password(test_user):
    db = TestingSessionLocal()
    invalid_password_user = authenticate_user(test_user.username,
                                              "invalid_password", db)
    assert invalid_password_user is False


def test_authenticate_user_empty_username(test_user):
    db = TestingSessionLocal()
    user = authenticate_user("", "testpassword", db)
    assert user is False


def test_authenticate_user_empty_password(test_user):
    db = TestingSessionLocal()
    user = authenticate_user(test_user.username, "", db)
    assert user is False


def test_create_access_token():
    username = "testuser"
    user_id = 1
    is_admin = False
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, is_admin, expires_delta)

    decoded_token = jwt.decode(token,
                               SECRET_KEY,
                               algorithms=[ALGORITHM],
                               options={"verify_signature": False})
    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id
    assert decoded_token["is_admin"] == is_admin


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {
        "sub": "testuser",
        "id": 1,
        "is_admin": True
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token=token)
    assert user == {"username": "testuser", "id": 1, "is_admin": True}


@pytest.mark.asyncio
async def test_get_current_user_missing_username_in_payload():
    encode = {
        "id": 1,
        "is_admin": True
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Could not validate the user"


@pytest.mark.asyncio
async def test_get_current_user_missing_user_id_in_payload():
    encode = {
        "sub": "testuser",
        "is_admin": True
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Could not validate the user"


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {
        "is_admin": True
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Could not validate the user"


def test_create_user():
    request_data = {
        "email": "email@gmail.com",
        "username": "username",
        "first_name": "firstname",
        "last_name": "lastname",
        "password": "testpassword",
        "is_admin": False,
    }
    response = client.post("/auth/create_user", json=request_data)
    print(response.text)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.username == "username").first()
    assert model.email == request_data.get("email")
    assert model.username == request_data.get("username")
    assert model.first_name == request_data.get("first_name")
    assert model.last_name == request_data.get("last_name")
    assert model.is_admin == request_data.get("is_admin")


def test_create_user_missing_required_fields():
    invalid_request_data = {}

    response = client.post("/auth/create_user", json=invalid_request_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_user_invalid_data():
    invalid_request_data = {
        "email": "emailgmail.com",
        "username": "username",
        "first_name": "firstname",
        "last_name": "lastname",
        "password": "testpassword",
        "is_admin": False,
    }

    response = client.post("/auth/create_user", json=invalid_request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_access_token():
    request_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/auth/token", data=request_data)

    token_response = Token(**response.json())

    assert response.status_code == status.HTTP_200_OK
    assert token_response.access_token is not None
    assert token_response.token_type == "bearer"


def test_get_access_token_invalid_credentials():
    invalid_request_data = {
        "username": "testuser",
        "password": "invalid_password"
    }

    response = client.post("/auth/token", data=invalid_request_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_access_token_user_not_found():
    invalid_request_data = {
        "username": "invaild_username",
        "password": "invalid_password"
    }

    response = client.post("/auth/token", data=invalid_request_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
