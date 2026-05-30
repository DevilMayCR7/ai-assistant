"""
聊天服务的业务逻辑
封装 DeepSeek API 的调用，支持多轮对话记忆和系统提示词
"""

import httpx
from app.config.settings import settings


class ChatService:
    """
    聊天服务类
    封装所有与聊天相关的业务操作，支持多轮对话上下文记忆
    """

    # 最多保存的历史消息条数（user + assistant 各算一条，system 不计入）
    MAX_HISTORY = 50

    def __init__(self):
        """
        初始化聊天服务
        从配置中读取 API 地址和模型名称，并设置系统提示词（只初始化一次）
        """
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL

        # 用于保存用户和 AI 的多轮对话历史记录（不含 system 提示词）
        self.chat_history: list[dict] = []

        # 系统提示词：只初始化一次，定义 AI 的角色和背景
        # 每次请求时自动附加在 messages 最前面，不会重复追加
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
- 优先提供具体建议而不是空泛鼓励。
"""

    def _add_message(self, role: str, content: str):
        """
        添加一条用户或 AI 的消息到历史记录，并自动控制长度

        参数:
            role: 消息发送者角色，"user" 或 "assistant"
            content: 消息内容
        """
        # 追加新消息到列表末尾
        self.chat_history.append({"role": role, "content": content})

        # 如果超出最大条数，从头部删除最早的消息（先进先出）
        # system 提示词不存于此列表，所以不会被误删
        while len(self.chat_history) > self.MAX_HISTORY:
            self.chat_history.pop(0)

    def _build_messages(self) -> list[dict]:
        """
        构造发送给 DeepSeek API 的完整消息列表

        格式：第一条是 system 提示词，后面紧跟用户和 AI 的历史对话
        这样 AI 既能知道自己是"谁"，又能理解当前对话上下文

        返回:
            完整的 messages 列表
        """
        system_msg = {"role": "system", "content": self.system_prompt}
        # system 放在最前面，后面接 user/assistant 历史记录
        return [system_msg] + self.chat_history.copy()

    async def chat_with_ai(self, user_message: str) -> str:
        """
        调用 DeepSeek API 进行对话（支持系统提示词 + 多轮记忆）

        流程：
            1. 保存用户消息到历史记录
            2. 构造完整消息（system + 历史）发送给 DeepSeek
            3. 收到回复后保存 AI 消息到历史记录
            4. 返回 AI 回复

        参数:
            user_message: 用户发送的消息内容

        返回:
            AI 的回复文本

        异常:
            网络异常、API 密钥缺失、API 返回错误等
        """
        # 检查 API 密钥是否配置
        if not self.api_key or self.api_key == "sk-your-api-key-here":
            raise ValueError("DeepSeek API 密钥未配置，请在 .env 文件中设置 DEEPSEEK_API_KEY")

        # 第 1 步：把用户消息追加到历史记录
        self._add_message("user", user_message)

        # 构造请求地址
        url = f"{self.base_url}/chat/completions"

        # 构造请求头
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 第 2 步：构造请求体，messages 包含 system 提示词 + 完整历史记录
        payload = {
            "model": self.model,
            "messages": self._build_messages()   # system 在最前，后面是 user/assistant 历史
        }

        # 使用 httpx 发送异步 HTTP POST 请求
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)

                # 检查 HTTP 状态码
                response.raise_for_status()

                # 解析 JSON 响应
                data = response.json()

                # 提取 AI 的回复内容
                # DeepSeek 返回格式：choices[0].message.content
                answer = data["choices"][0]["message"]["content"]

                # 第 3 步：把 AI 的回复也保存到历史记录
                self._add_message("assistant", answer)

                return answer

            except httpx.HTTPStatusError as e:
                # HTTP 状态码错误（如 401 密钥无效、429 请求过多）
                error_msg = f"DeepSeek API 请求失败: HTTP {e.response.status_code}"
                try:
                    error_detail = e.response.json()
                    error_msg += f", 详情: {error_detail}"
                except Exception:
                    pass
                raise RuntimeError(error_msg) from e

            except httpx.RequestError as e:
                # 网络连接错误（如断网、DNS 解析失败）
                raise RuntimeError(f"网络请求异常: {e}") from e

            except (KeyError, IndexError) as e:
                # API 返回的数据格式不符合预期
                raise RuntimeError(f"API 响应格式异常: {e}") from e

    def get_history(self) -> list:
        """
        获取用户和 AI 的聊天历史记录（不含 system 提示词）

        返回:
            包含 user 和 assistant 消息的列表
        """
        return self.chat_history.copy()   # 返回副本，防止外部直接修改内部列表

    def clear_history(self):
        """
        清空用户和 AI 的聊天记录
        system 提示词不会被清除，始终保留
        """
        self.chat_history = []


# 创建单例实例
chat_service = ChatService()
