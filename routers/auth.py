
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Annotated
from jose import jwt, JWTError


from database import SessionLocal
from models import Users


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    email: EmailStr = Field(max_length=50)
    username: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=10, max_length=50)
    is_admin: bool = Field(default=False)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "test@gmail.com",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "password": "testpassword",
                "is_admin": False
            }
        }
    )


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return False

    if not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


def create_access_token(username: str, user_id: int,
                        is_admin: bool, expires_delta: timedelta):
    encode = {
        "sub": username,
        "id": user_id,
        "is_admin": is_admin
    }
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        is_admin: bool = payload.get("is_admin")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate the user")

        return {"username": username, "id": user_id, "is_admin": is_admin}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate the user")


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_admin=create_user_request.is_admin
    )

    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def get_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                           db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate the user")

    token = create_access_token(
        user.username, user.id, user.is_admin, timedelta(minutes=20))

    return {"access_token": token, "token_type": "bearer"}