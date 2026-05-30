"""
会话管理服务
负责用户、会话、消息的增删改查（CRUD）
所有数据库操作都通过 SQLAlchemy 2.0 异步会话完成
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.models import User, ChatSession, ChatMessage


# ==================== 用户操作 ====================

async def create_user(db: AsyncSession, username: str, nickname: str | None) -> User:
    """
    创建新用户

    参数:
        db: 数据库会话
        username: 用户名
        nickname: 昵称

    返回:
        新创建的用户对象
    """
    user = User(username=username, nickname=nickname)
    db.add(user)
    await db.flush()  # 刷新，让数据库生成 id
    return user


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """
    根据用户名查找用户

    参数:
        db: 数据库会话
        username: 用户名

    返回:
        用户对象，找不到返回 None
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_or_create_user(db: AsyncSession, username: str, nickname: str | None = None) -> User:
    """
    获取或创建用户
    如果用户已存在则返回，不存在则创建

    参数:
        db: 数据库会话
        username: 用户名
        nickname: 昵称

    返回:
        用户对象
    """
    user = await get_user_by_username(db, username)
    if user:
        return user
    return await create_user(db, username, nickname)


# ==================== 会话操作 ====================

async def create_session(db: AsyncSession, user_id: int, title: str) -> ChatSession:
    """
    创建新会话

    参数:
        db: 数据库会话
        user_id: 用户ID
        title: 会话标题

    返回:
        新创建的会话对象
    """
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    await db.flush()
    return session


async def get_sessions_by_user(db: AsyncSession, user_id: int) -> list[ChatSession]:
    """
    获取指定用户的所有会话

    参数:
        db: 数据库会话
        user_id: 用户ID

    返回:
        会话列表，按创建时间倒序
    """
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_time.desc())
    )
    return list(result.scalars().all())


# ==================== 消息操作 ====================

async def create_message(db: AsyncSession, session_id: int, role: str, content: str) -> ChatMessage:
    """
    创建新消息

    参数:
        db: 数据库会话
        session_id: 会话ID
        role: 角色（"user" 或 "assistant"）
        content: 消息内容

    返回:
        新创建的消息对象
    """
    msg = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(msg)
    await db.flush()
    return msg


async def get_messages_by_session(db: AsyncSession, session_id: int) -> list[ChatMessage]:
    """
    获取指定会话的所有消息

    参数:
        db: 数据库会话
        session_id: 会话ID

    返回:
        消息列表，按创建时间正序（先旧后新）
    """
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_time.asc())
    )
    return list(result.scalars().all())


async def get_messages_for_ai(db: AsyncSession, session_id: int) -> list[dict]:
    """
    获取指定会话的历史消息，格式化为 AI 接口需要的格式

    参数:
        db: 数据库会话
        session_id: 会话ID

    返回:
        [{"role": "user", "content": "..."}, ...]
    """
    messages = await get_messages_by_session(db, session_id)
    return [{"role": msg.role, "content": msg.content} for msg in messages]
