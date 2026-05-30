"""
SQLAlchemy 2.0 ORM 模型定义
对应数据库中的 users、chat_session、chat_message 三张表
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model.database import Base


# ==================== 用户表 ====================

class User(Base):
    """
    用户表
    存储系统用户的基本信息
    """
    # 表名
    __tablename__ = "users"

    # id: 主键，自增整数
    # Mapped[int]: SQLAlchemy 2.0 的类型注解写法
    # mapped_column(primary_key=True): 声明为主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="用户ID")

    # username: 用户名，唯一，不允许为空
    # String(64): VARCHAR(64)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="用户名")

    # nickname: 昵称，可以为空
    nickname: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="昵称")

    # created_time: 创建时间，自动填充当前时间
    # server_default=func.now(): 数据库层面的默认值
    created_time: Mapped[datetime] = mapped_column(
        default=datetime.now,
        server_default=func.now(),
        comment="创建时间"
    )

    # relationship: 定义与 ChatSession 的关系
    # "ChatSession": 关联的模型类名（字符串形式，避免循环导入）
    # back_populates="user": 双向关联，ChatSession 中也有 user 属性
    sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan",  # 删除用户时级联删除其所有会话
        lazy="selectin",  # 异步加载策略，避免 N+1 问题
    )


# ==================== 聊天会话表 ====================

class ChatSession(Base):
    """
    聊天会话表
    每个用户可以有多个会话，每个会话包含多条消息
    """
    __tablename__ = "chat_session"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="会话ID")

    # user_id: 外键，关联 users 表的 id
    # ForeignKey("users.id", ondelete="CASCADE"): 用户删除时级联删除
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID"
    )

    # title: 会话标题，如"第一次聊天"
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="会话标题")

    created_time: Mapped[datetime] = mapped_column(
        default=datetime.now,
        server_default=func.now(),
        comment="创建时间"
    )

    # 关联用户
    user: Mapped[User] = relationship("User", back_populates="sessions")

    # 关联消息：一个会话有多条消息
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ChatMessage.id",  # 按消息ID排序，确保顺序正确
    )


# ==================== 聊天消息表 ====================

class ChatMessage(Base):
    """
    聊天消息表
    存储每条聊天的具体内容
    """
    __tablename__ = "chat_message"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="消息ID")

    # session_id: 外键，关联 chat_session 表的 id
    session_id: Mapped[int] = mapped_column(
        ForeignKey("chat_session.id", ondelete="CASCADE"),
        nullable=False,
        comment="会话ID"
    )

    # role: 消息角色，只能是 "user" 或 "assistant"
    # String(16): 足够存储这两个值
    role: Mapped[str] = mapped_column(String(16), nullable=False, comment="角色: user/assistant")

    # content: 消息内容，可能很长，用 Text 类型
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")

    created_time: Mapped[datetime] = mapped_column(
        default=datetime.now,
        server_default=func.now(),
        comment="创建时间"
    )

    # 关联会话
    session: Mapped[ChatSession] = relationship("ChatSession", back_populates="messages")
