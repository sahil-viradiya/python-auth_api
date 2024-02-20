from datetime import timedelta, timezone, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database import getDb
from models import User
from schemas import createUser, loginUser, TokenData, Token

router = APIRouter(prefix='/user')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "80c54b84fe327a5d41de9e40e4e5a86c98ba980c183fca2bf472725b0c6fdf95"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post('/create')
async def createUser(request: createUser, db: AsyncSession = Depends(getDb)):
    hasPass = pwd_context.hash(request.password)
    user = User(name=request.name, email=request.email, password=hasPass)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


oauth2_scheme = HTTPBearer()


@router.post('/login')
async def loginUser(request: Annotated[OAuth2PasswordRequestForm, Depends()],
                    db: AsyncSession = Depends(getDb)):
    qry = await db.execute(select(User).where(User.email == request.username))
    executequery = qry.scalars().first()

    if not executequery:
        raise HTTPException(status_code=404, detail="not found")

    verify = pwd_context.verify(request.password, executequery.password)
    if not verify:
        raise HTTPException(status_code=404, detail="password not found")
    access_token = create_access_token(
        data={"sub": executequery.email})
    return Token(access_token=access_token, token_type="bearer")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(getDb)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    qry = await db.execute(select(User).where(User.email == token_data.username))
    executequery = qry.scalars().first()
    if executequery is None:
        raise credentials_exception
    return executequery


@router.get("/me")
async def read_user(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
