"""
数据模型定义（Schema）
使用 Pydantic 定义请求和响应的数据结构
自动做类型校验和文档生成
"""

from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    """
    聊天请求模型
    定义客户端发送消息时需要传入的数据格式

    示例请求：
        {
            "message": "你好"
        }
    """
    message: str   # 用户输入的消息内容

    # Pydantic 会自动校验：message 必须是字符串，且不能为空


class ChatMessageResponse(BaseModel):
    """
    聊天响应模型
    定义服务器返回给客户端的数据格式

    示例响应：
        {
            "answer": "你好！有什么可以帮你的吗？"
        }
    """
    answer: str    # AI 的回复内容


class HelloResponse(BaseModel):
    """
    测试响应模型
    用于 /hello 接口返回的数据格式
    """
    message: str   # 问候消息


class ErrorResponse(BaseModel):
    """
    错误响应模型
    接口出错时返回的统一格式
    """
    error: str     # 错误描述信息
