from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, BOOLEAN
from sqlalchemy.orm import relationship, remote, foreign
from sqlalchemy import func
from sqlalchemy import Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import LtreeType, Ltree
from sqlalchemy import Sequence
from .database import sunc_engine
from datetime import datetime

from .crud import BaseCrud

id_seq = Sequence("comments_id_seq")
Base = declarative_base()


class Posts(Base, BaseCrud):
    __tablename__ = "posts"

    id = Column(Integer, nullable=False, unique=True, primary_key=True)
    text = Column(Text, nullable=False, comment="Текст поста")
    likes = Column(Integer, nullable=True, comment="Лаки")
    user = Column(Integer, ForeignKey("users.id"), nullable=False, comment="Пользователь написавший пост")
    created_dt = Column(DateTime, nullable=False, default=datetime.utcnow(), comment="Дата публикации")


class Users(Base, BaseCrud):
    __tablename__ = "users"

    id = Column(Integer, nullable=False, unique=True, primary_key=True)
    name = Column(String, nullable=False, comment="имя пользака")
    login = Column(String, nullable=False, unique=True, comment="Уникальный логин пользака")
    password_hash = Column(Text, nullable=False)
    disabled = Column(BOOLEAN, comment="")


class Comments(Base, BaseCrud):
    __tablename__ = "comments"

    id = Column(Integer, id_seq, primary_key=True)
    user = Column(Integer, ForeignKey("users.id"), nullable=False, comment="Пользователь оставивший коммент")
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, comment="Пост к которому оставили коммент")

    text = Column(Text, nullable=False, comment="Текст комментария")
    likes = Column(Integer, nullable=True, comment="Лаки")
    created_dt = Column(DateTime, nullable=False, default=datetime.utcnow(), comment="Дата публикации")
    path = Column(LtreeType)
    parent = relationship(
        "Comments",
        primaryjoin=remote(path) == foreign(func.subpath(path, 0, -1)),
        backref="children",
        viewonly=True,
    )
    __table_args__ = (Index("ix_nodes_path", path, postgresql_using="gist"),)
    # XXX комменты как на харбе
    # parent_id = Column(Integer, ForeignKey('comments.id'))
    # children = relationship(
    #     "Comments",
    #     remote_side=[id],
    #     lazy="joined",
    #     join_depth=2
    # )
    def __init__(self, text=None, post_id=None, user=None, parent=None):
        _id = sunc_engine.execute(id_seq)
        self.id = _id
        self.post_id = post_id
        self.text = text
        self.user = user
        ltree_id = Ltree(str(_id))
        self.path = ltree_id if parent is None else parent.path + ltree_id
        self.created_dt = datetime.utcnow()


metadata = Base.metadata
