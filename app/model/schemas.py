"""
Pydantic v2 数据模型（Schema）
定义请求和响应的数据结构，自动做类型校验

注意：SQLAlchemy ORM 模型和 Pydantic Schema 是分开的：
    - ORM 模型(models.py): 定义数据库表结构
    - Pydantic Schema(schemas.py): 定义 API 请求/响应的数据格式
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# ==================== 用户相关 ====================

class UserCreate(BaseModel):
    """
    创建用户的请求模型
    """
    username: str = Field(..., min_length=1, max_length=64, description="用户名")
    nickname: str | None = Field(None, max_length=64, description="昵称")


class UserResponse(BaseModel):
    """
    用户信息的响应模型
    """
    # ConfigDict(from_attributes=True): 允许从 ORM 对象自动转换
    # SQLAlchemy 模型对象可以直接传给这个 Pydantic 模型
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str | None
    created_time: datetime


# ==================== 会话相关 ====================

class SessionCreate(BaseModel):
    """
    创建会话的请求模型
    """
    user_id: int = Field(..., description="用户ID")
    title: str = Field(..., min_length=1, max_length=255, description="会话标题")


class SessionResponse(BaseModel):
    """
    会话信息的响应模型
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    created_time: datetime


class SessionListResponse(BaseModel):
    """
    会话列表响应模型
    """
    sessions: list[SessionResponse]


# ==================== 消息相关 ====================

class ChatMessageRequest(BaseModel):
    """
    发送聊天消息的请求模型
    """
    session_id: int = Field(..., description="会话ID")
    message: str = Field(..., min_length=1, description="用户消息内容")


class ChatMessageResponse(BaseModel):
    """
    聊天消息的响应模型（单条消息）
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    role: str
    content: str
    created_time: datetime


class ChatAnswerResponse(BaseModel):
    """
    AI 回复的响应模型
    """
    answer: str = Field(..., description="AI 回复内容")


class MessageListResponse(BaseModel):
    """
    消息列表响应模型
    """
    messages: list[ChatMessageResponse]


# ==================== 保留原有的 Hello 响应 ====================

class HelloResponse(BaseModel):
    """
    测试响应模型
    """
    message: str
