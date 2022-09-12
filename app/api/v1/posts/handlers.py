from fastapi import APIRouter, Request
from fastapi.params import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import List
from app.common.auth.auth import AuthToken
from app.dependencies import get_session
from app.api.v1.posts.models import Posts, CreatePost, UpdatePost
from database.tables import Posts as DBPosts
from sqlalchemy import select


routers = APIRouter(tags=["posts"], prefix="/api/v1")


@routers.get("/post", status_code=200, response_model=List[Posts])
async def list_of_posts(
    offset: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    """
    Получение отсортированного по дате создания списка постов
    """
    result = (
        (await session.execute(select(DBPosts).order_by(DBPosts.created_dt.desc()).limit(limit).offset(offset)))
        .scalars()
        .all()
    )
    return [Posts.from_orm(r) for r in result]


@routers.get("/post/{post_id}", status_code=200, response_model=Posts)
async def detail_of_posts(
    post_id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Получение всей инфы о посте
    """
    result = (await session.execute(select(DBPosts).where(DBPosts.id == post_id))).scalars().one()
    return Posts.from_orm(result)


@routers.post("/post", status_code=200)
async def add_post(
    request: Request,
    post: CreatePost,
    session: AsyncSession = Depends(get_session),
    auth=Depends(AuthToken()),
):
    """
    Добавить пост
    """
    await DBPosts.insert(session, [dict(user=request.state.user_data.id ,**post.dict())])
    await session.commit()


@routers.put("/post/{post_id}", status_code=200)
async def update_post(
    post: UpdatePost,
    post_id: int,
    session: AsyncSession = Depends(get_session),
    # auth=Depends(AuthToken()),
):
    """
    Изменить пост
    """
    result = (await DBPosts.update(session, id_=post_id, **post.dict())).first()
    await session.commit()
    return Posts.from_orm(result)


@routers.delete("/post/{post_id}", status_code=200)
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    # auth=Depends(AuthToken()),
):
    """
    Удалить пост
    """
    await DBPosts.delete_by_field(session, {"id": post_id})
    await session.commit()
    return
