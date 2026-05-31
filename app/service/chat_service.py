"""
聊天服务的业务逻辑
封装 DeepSeek API 的调用，支持数据库存储、系统提示词、自动会话管理
"""

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.service.session_service import (
    get_messages_for_ai,
    create_message,
    get_session_by_id,
    create_session,
    get_user_by_id,
    create_user,
)


class ChatService:
    """
    聊天服务类
    封装所有与聊天相关的业务操作，包括自动创建会话和消息持久化
    """

    def __init__(self):
        """
        初始化聊天服务
        """
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL

        # 系统提示词：只初始化一次
        self.system_prompt = """你是张春然和他女朋友金苗的生活助手。

背景信息：

张春然：
- 大数据开发工程师
- 正在学习 AI 开发
- 正在健身减脂
- 年龄 31，身高 177cm，体重 80kg，体脂 18%
- 喜欢给女朋友做饭

金苗：
- 京东白酒类产品运营
- 正在努力让自己运营的白酒品牌销量增加
- 正在健身减脂
- 年龄 25，身高 162cm，体重 49kg

两个人：
- 喜欢一起或者隔空健身
- 喜欢一起玩双人游戏
- 喜欢一起吃好吃的、玩好玩的
- 2026 年 3 月 24 日是两个人谈恋爱的第一天
- 兴趣相投，低山臭水遇知音

回答要求：
- 简洁
- 友好
- 实用
- 适当幽默
- 不要编造用户没有明确提供的信息。
- 如果不知道，请直接说明不知道。
- 优先提供具体建议而不是空泛鼓励。"""

    def _build_messages(self, history: list[dict]) -> list[dict]:
        """
        构造发送给 DeepSeek API 的完整消息列表

        格式：第一条是 system 提示词，后面紧跟历史对话
        """
        system_msg = {"role": "system", "content": self.system_prompt}
        return [system_msg] + history

    async def _ensure_session(
        self, db: AsyncSession, user_id: int, session_id: int | None, message: str
    ) -> int:
        """
        确保有可用会话，返回 session_id

        逻辑：
            1. 如果传了 session_id 且存在，直接返回（继续当前会话）
            2. 如果没传 session_id，自动创建新会话

        参数:
            db: 数据库会话
            user_id: 用户ID
            session_id: 客户端传来的会话ID（可能为None）
            message: 用户消息（用于生成会话标题）

        返回:
            可用的 session_id
        """
        # 情况1：传了 session_id，检查是否存在，存在则续接当前会话
        if session_id is not None:
            existing = await get_session_by_id(db, session_id)
            if existing:
                return session_id
            # 传了但不存在，走创建新会话逻辑

        # 情况2：没传 session_id，或传了但不存在，创建新会话
        # 先确保用户存在
        user = await get_user_by_id(db, user_id)
        if not user:
            user = await create_user(db, username=f"user_{user_id}", nickname=None)
            user_id = user.id

        # 创建新会话，标题取消息前20字
        title = message[:20] if len(message) <= 20 else message[:20] + "..."
        new_session = await create_session(db, user_id, title)
        return new_session.id

    async def chat_with_ai(
        self, db: AsyncSession, user_id: int, user_message: str, session_id: int | None = None
    ) -> tuple[str, int]:
        """
        调用 DeepSeek API 进行对话（完整流程，含自动会话管理和消息持久化）

        流程：
            1. 确保有可用会话（自动创建或续接）
            2. 保存用户消息到数据库（role="user"）
            3. 从数据库读取完整历史记录
            4. 调用 DeepSeek API
            5. 保存 AI 回复到数据库（role="assistant"）
            6. 返回 AI 回复和当前会话ID

        参数:
            db: 数据库会话
            user_id: 用户ID
            user_message: 用户发送的消息内容
            session_id: 会话ID（可选），不传则自动获取或创建

        返回:
            (AI回复文本, 当前会话ID)
        """
        # 检查 API 密钥是否配置
        if not self.api_key or self.api_key == "sk-your-api-key-here":
            raise ValueError("DeepSeek API 密钥未配置，请在 .env 文件中设置 DEEPSEEK_API_KEY")

        # ========== 第 1 步：确保有可用会话 ==========
        actual_session_id = await self._ensure_session(db, user_id, session_id, user_message)

        # ========== 第 2 步：保存用户消息到数据库 ==========
        await create_message(db, actual_session_id, "user", user_message)

        # ========== 第 3 步：从数据库读取历史记录 ==========
        history = await get_messages_for_ai(db, actual_session_id)

        # ========== 第 4 步：调用 DeepSeek API ==========
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": self._build_messages(history)
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                answer = data["choices"][0]["message"]["content"]

            except httpx.HTTPStatusError as e:
                error_msg = f"DeepSeek API 请求失败: HTTP {e.response.status_code}"
                try:
                    error_detail = e.response.json()
                    error_msg += f", 详情: {error_detail}"
                except Exception:
                    pass
                raise RuntimeError(error_msg) from e

            except httpx.RequestError as e:
                raise RuntimeError(f"网络请求异常: {e}") from e

            except (KeyError, IndexError) as e:
                raise RuntimeError(f"API 响应格式异常: {e}") from e

        # ========== 第 5 步：保存 AI 回复到数据库 ==========
        await create_message(db, actual_session_id, "assistant", answer)

        return answer, actual_session_id


# 创建单例实例
chat_service = ChatService()
