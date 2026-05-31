"""
聊天相关的 API 路由
定义客户端可以调用的接口，包括 AI 聊天、会话管理、消息查询
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

# 导入数据模型
from app.model.schemas import (
    ChatMessageRequest,
    ChatAnswerResponse,
    SessionCreate,
    SessionResponse,
    SessionListResponse,
    MessageListResponse,
    ChatMessageResponse,
    HelloResponse,
)

# 导入数据库会话
from app.model.database import get_db

# 导入服务层
from app.service.chat_service import chat_service
from app.service.session_service import (
    get_or_create_user,
    create_session,
    get_sessions_by_user,
    get_messages_by_session,
)

# 创建路由实例
router = APIRouter(prefix="/chat", tags=["聊天"])

# 配置模板引擎
templates = Jinja2Templates(directory="app/templates")


# ==================== 页面路由 ====================

@router.get("")
async def chat_page(request: Request):
    """
    聊天页面入口
    """
    return templates.TemplateResponse("chat.html", {"request": request})


# ==================== 测试接口 ====================

@router.get("/hello", response_model=HelloResponse)
async def hello():
    """
    测试接口：返回 hello world
    """
    return {"message": "hello world"}


# ==================== 核心聊天接口 ====================

@router.post("", response_model=ChatAnswerResponse)
async def chat(request: ChatMessageRequest, db: AsyncSession = Depends(get_db)):
    """
    发送消息并获取 AI 回复（自动会话管理 + 消息持久化）

    功能：
        1. 如果传了 session_id，继续该会话
        2. 如果没传 session_id，自动获取用户最近会话；没有则创建新会话
        3. 保存用户消息到数据库（role="user"）
        4. 调用 DeepSeek API
        5. 保存 AI 回复到数据库（role="assistant"）
        6. 返回 AI 回复和当前会话ID

    请求示例 - 方式1（指定会话）：
        {
            "user_id": 1,
            "session_id": 1,
            "message": "你好"
        }

    请求示例 - 方式2（自动会话）：
        {
            "user_id": 1,
            "message": "你好"
        }

    响应示例：
        {
            "answer": "你好！有什么可以帮你的吗？",
            "session_id": 1
        }
    """
    try:
        answer, session_id = await chat_service.chat_with_ai(
            db,
            user_id=request.user_id,
            user_message=request.message,
            session_id=request.session_id,
        )
        return ChatAnswerResponse(answer=answer, session_id=session_id)

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {e}")


# ==================== 会话管理接口 ====================

@router.post("/session/create", response_model=SessionResponse)
async def create_chat_session(request: SessionCreate, db: AsyncSession = Depends(get_db)):
    """
    创建新的聊天会话

    请求示例：
        {
            "user_id": 1,
            "title": "第一次聊天"
        }

    响应示例：
        {
            "id": 1,
            "user_id": 1,
            "title": "第一次聊天",
            "created_time": "2026-05-31T10:00:00"
        }
    """
    try:
        session = await create_session(db, request.user_id, request.title)
        return SessionResponse.model_validate(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败: {e}")


@router.get("/session/list", response_model=SessionListResponse)
async def list_sessions(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取指定用户的所有会话列表

    访问示例：
        GET /chat/session/list?user_id=1

    响应示例：
        {
            "sessions": [
                {
                    "id": 1,
                    "user_id": 1,
                    "title": "第一次聊天",
                    "created_time": "2026-05-31T10:00:00"
                }
            ]
        }
    """
    try:
        sessions = await get_sessions_by_user(db, user_id)
        return SessionListResponse(
            sessions=[SessionResponse.model_validate(s) for s in sessions]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {e}")


# ==================== 消息查询接口 ====================

@router.get("/message/list", response_model=MessageListResponse)
async def list_messages(session_id: int, db: AsyncSession = Depends(get_db)):
    """
    获取指定会话的所有消息列表

    访问示例：
        GET /chat/message/list?session_id=1

    响应示例：
        {
            "messages": [
                {
                    "id": 1,
                    "session_id": 1,
                    "role": "user",
                    "content": "你好",
                    "created_time": "2026-05-31T10:00:00"
                },
                {
                    "id": 2,
                    "session_id": 1,
                    "role": "assistant",
                    "content": "你好！有什么可以帮你的吗？",
                    "created_time": "2026-05-31T10:00:01"
                }
            ]
        }
    """
    try:
        messages = await get_messages_by_session(db, session_id)
        return MessageListResponse(
            messages=[ChatMessageResponse.model_validate(m) for m in messages]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息列表失败: {e}")


# ==================== 用户接口（辅助）====================

@router.post("/user/get_or_create", response_model=dict)
async def get_or_create_user_api(
    username: str, nickname: str | None = None, db: AsyncSession = Depends(get_db)
):
    """
    获取或创建用户
    如果用户已存在则返回，不存在则创建

    访问示例：
        POST /chat/user/get_or_create?username=zhangchunran&nickname=春然

    响应示例：
        {
            "id": 1,
            "username": "zhangchunran",
            "nickname": "春然",
            "message": "用户已创建"
        }
    """
    try:
        from app.service.session_service import get_user_by_username

        existing = await get_user_by_username(db, username)
        if existing:
            return {
                "id": existing.id,
                "username": existing.username,
                "nickname": existing.nickname,
                "message": "用户已存在"
            }

        user = await get_or_create_user(db, username, nickname)
        return {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "message": "用户已创建"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用户操作失败: {e}")
