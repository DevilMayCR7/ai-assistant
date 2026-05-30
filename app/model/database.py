"""
SQLAlchemy 2.0 数据库配置
负责创建异步引擎、会话工厂和表创建
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import settings


# ==================== 声明性基类 ====================

class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 声明性基类
    所有 ORM 模型都继承这个类
    """
    pass


# ==================== 异步数据库引擎 ====================

# create_async_engine: 创建异步数据库引擎
# pool_size: 连接池大小
# echo: 是否打印 SQL 语句（调试用）
async_engine = create_async_engine(
    settings.database_url,
    pool_size=settings.DB_POOL_SIZE,
    echo=settings.DB_ECHO,
)

# ==================== 异步会话工厂 ====================

# async_sessionmaker: 创建异步会话的工厂函数
# autocommit=False: 不自动提交，需要手动调用 commit()
# autoflush=False: 不自动 flush，减少不必要的数据库操作
# class_=AsyncSession: 使用异步会话类
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # 提交后不过期对象，避免异步中的延迟加载问题
)


# ==================== 依赖注入函数 ====================

async def get_db():
    """
    获取数据库会话的异步上下文管理器
    用于 FastAPI 的 Depends 依赖注入

    用法:
        @router.get("/xxx")
        async def xxx(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # 正常结束时自动提交
        except Exception:
            await session.rollback()  # 异常时回滚
            raise
        finally:
            await session.close()  # 确保会话始终关闭


# ==================== 自动创建表 ====================

async def init_db():
    """
    初始化数据库：自动创建所有表
    在应用启动时调用一次

    注意：
        - 不会删除已有表
        - 不会修改已有表结构（如新增字段）
        - 生产环境建议使用 Alembic 做数据库迁移
    """
    # 导入所有模型，确保 Base.metadata 能感知到它们
    # 必须在这里导入，否则 create_all 不知道有哪些表要创建
    from app.model import models  # noqa: F401

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表初始化完成")
