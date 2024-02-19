from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import getDb
from models import User
from schemas import createUser, loginUser

router = APIRouter(prefix='/user')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


@router.post('/login')
async def loginUser(request:loginUser,db:AsyncSession = Depends(getDb)):

    qry = await db.execute(select(User).where(User.email==request.email))
    executequery = qry.scalars().first()

    if not executequery:
        raise HTTPException(status_code=404, detail="not found")

    verify = pwd_context.verify(request.password,executequery.password)
    if not verify:
        raise HTTPException(status_code=404, detail="password not found")
    return executequery

