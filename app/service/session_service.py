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
    """
    user = User(username=username, nickname=nickname)
    db.add(user)
    await db.flush()
    return user


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """
    根据用户名查找用户
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """
    根据用户ID查找用户
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_or_create_user(db: AsyncSession, username: str, nickname: str | None = None) -> User:
    """
    获取或创建用户
    """
    user = await get_user_by_username(db, username)
    if user:
        return user
    return await create_user(db, username, nickname)


# ==================== 会话操作 ====================

async def create_session(db: AsyncSession, user_id: int, title: str) -> ChatSession:
    """
    创建新会话
    """
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    await db.flush()
    return session


async def get_session_by_id(db: AsyncSession, session_id: int) -> ChatSession | None:
    """
    根据会话ID查找会话
    """
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    return result.scalar_one_or_none()


async def get_sessions_by_user(db: AsyncSession, user_id: int) -> list[ChatSession]:
    """
    获取指定用户的所有会话，按创建时间倒序
    """
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_time.desc())
    )
    return list(result.scalars().all())


async def get_latest_session_by_user(db: AsyncSession, user_id: int) -> ChatSession | None:
    """
    获取用户最近一个会话
    """
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_time.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


# ==================== 消息操作 ====================

async def create_message(db: AsyncSession, session_id: int, role: str, content: str) -> ChatMessage:
    """
    创建新消息
    """
    msg = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(msg)
    await db.flush()
    return msg


async def get_messages_by_session(db: AsyncSession, session_id: int) -> list[ChatMessage]:
    """
    获取指定会话的所有消息，按创建时间正序
    """
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_time.asc())
    )
    return list(result.scalars().all())


async def get_messages_for_ai(db: AsyncSession, session_id: int, limit: int = 20) -> list[dict]:
    """
    获取指定会话的历史消息，格式化为 AI 接口需要的格式

    逻辑：
        1. 按时间倒序取最近 N 条（默认20条）
        2. 再按时间正序排列，保证对话顺序正确
        3. 格式化为 {"role": "user|assistant", "content": "..."}

    参数:
        db: 数据库会话
        session_id: 会话ID
        limit: 最多取多少条历史消息，默认20条

    返回:
        [{"role": "user", "content": "..."}, ...]
    """
    # 子查询：先按时间倒序取最近 limit 条
    subquery = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_time.desc())
        .limit(limit)
        .subquery()
    )

    # 外层查询：按时间正序排列，保证对话顺序
    result = await db.execute(
        select(ChatMessage)
        .select_from(subquery)
        .order_by(ChatMessage.created_time.asc())
    )

    messages = list(result.scalars().all())
    return [{"role": msg.role, "content": msg.content} for msg in messages]
