from fastapi import APIRouter, Request
from fastapi.params import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.common.auth.auth import AuthToken
from app.dependencies import get_session
from database.tables import Comments as DBComments
from .models import AddComment, UpdateComment, Comment
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.sql import text


routers = APIRouter(tags=["comments"], prefix="/api/v1")


@routers.put("/comment/{comment_id}", status_code=200, response_model=Comment)
async def update_comment(
    comment_id: int,
    comment: UpdateComment,
    session: AsyncSession = Depends(get_session),
    auth=Depends(AuthToken()),
):
    """
    Редактирование комментария
    """
    result = (await DBComments.update(session, id_=comment_id, **comment.dict())).first()
    await session.commit()
    return Comment.from_orm(result)


@routers.delete("/comment/{comment_id}", status_code=200)
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_session),
    auth=Depends(AuthToken()),
):
    """
    Удалить комментарий
    """
    await DBComments.delete_by_field(session, {"id": comment_id})
    await session.commit()
    return


@routers.post("/comment", status_code=200)
async def add_comment(
    request: Request,
    comment: AddComment,
    parent_id: int = None,
    session: AsyncSession = Depends(get_session),
    auth=Depends(AuthToken()),
):
    """
    Добавить комментарий первого уровня
    """
    if not parent_id:
        comment = DBComments(user=request.state.user_data.id, **comment.dict())
        session.add(comment)
    else:
        parent = await DBComments.get(session, id_=parent_id)
        comment = DBComments(user=request.state.user_data.id, parent=parent[0], **comment.dict())
        session.add(comment)
    await session.commit()


@routers.get("/comment/{post_id}", status_code=200, response_model=List[Comment])
async def get_comments(
    post_id: int,
    limit: int = 10,
    offset: int = 2,
    parent_id: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    # auth=Depends(AuthToken()),
):
    if not parent_id:
        query = (
            select(DBComments)
            .filter(func.nlevel(DBComments.path) == 1)
            .filter(DBComments.post_id == post_id)
            .limit(limit)
            .offset(offset)
        )
        result = (await session.execute(query)).scalars()
    else:
        # TODO добработать запрос и переделать в ОРМ
        result = await session.execute(
            text(f"""SELECT * FROM "comments" WHERE path <@ '{parent_id}' LIMIT {limit} OFFSET {offset};""")
        )
        result = result.fetchall()
        # убирает родителя TODO сделать лучше
        if not offset:
            result = result[1:]

    return [Comment.from_orm(r) for r in result]
