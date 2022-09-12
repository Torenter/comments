from .service import authenticate_user, create_access_token
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.dependencies import get_session
from .models import Token
from datetime import timedelta
from app.settings import settings
from .models import CreateUser, AuthUser
from database.tables import Users as DBUsers


routers = APIRouter(tags=["auth"], prefix="/api/v1")


@routers.post("/token", response_model=Token)
async def login_for_access_token(form_data: AuthUser, session: AsyncSession = Depends(get_session)):
    """
    Получение токена для дальнейших запросов
    """
    user = await authenticate_user(form_data.login, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token}


@routers.post("/register")
async def register(user: CreateUser, session: AsyncSession = Depends(get_session)):
    """
    Регистрация нового пользователя 
    """
    await DBUsers.insert(session, [user.dict()])
    try:
        await session.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="non-unique login"
        )