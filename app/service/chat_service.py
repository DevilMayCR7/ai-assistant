"""
聊天服务的业务逻辑
封装 DeepSeek API 的调用，支持数据库存储和系统提示词
"""

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.service.session_service import get_messages_for_ai, create_message


class ChatService:
    """
    聊天服务类
    封装所有与聊天相关的业务操作
    """

    def __init__(self):
        """
        初始化聊天服务
        从配置中读取 API 地址和模型名称
        """
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL

        # 系统提示词：只初始化一次，定义 AI 的角色和背景
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

        参数:
            history: 数据库中的历史消息列表 [{"role": "...", "content": "..."}, ...]

        返回:
            完整的 messages 列表
        """
        system_msg = {"role": "system", "content": self.system_prompt}
        return [system_msg] + history

    async def chat_with_ai(self, db: AsyncSession, session_id: int, user_message: str) -> str:
        """
        调用 DeepSeek API 进行对话（完整流程）

        流程：
            1. 保存用户消息到数据库
            2. 从数据库读取完整历史记录
            3. 调用 DeepSeek API
            4. 保存 AI 回复到数据库
            5. 返回 AI 回复

        参数:
            db: 数据库会话
            session_id: 会话ID
            user_message: 用户发送的消息内容

        返回:
            AI 的回复文本
        """
        # 检查 API 密钥是否配置
        if not self.api_key or self.api_key == "sk-your-api-key-here":
            raise ValueError("DeepSeek API 密钥未配置，请在 .env 文件中设置 DEEPSEEK_API_KEY")

        # ========== 第 1 步：保存用户消息到数据库 ==========
        await create_message(db, session_id, "user", user_message)

        # ========== 第 2 步：从数据库读取历史记录 ==========
        history = await get_messages_for_ai(db, session_id)

        # ========== 第 3 步：调用 DeepSeek API ==========
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

        # ========== 第 4 步：保存 AI 回复到数据库 ==========
        await create_message(db, session_id, "assistant", answer)

        return answer


# 创建单例实例
chat_service = ChatService()
