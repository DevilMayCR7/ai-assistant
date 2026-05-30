"""
项目配置文件
集中管理所有可配置项
从 .env 文件读取敏感配置（如 API 密钥）
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
# 这行代码执行后，.env 里的配置就可用 os.getenv 读取了
load_dotenv()


class Settings:
    """
    项目设置类
    所有配置项都在这里定义
    """

    # 应用名称
    APP_NAME: str = "AI 聊天助手"

    # 应用版本
    APP_VERSION: str = "0.1.0"

    # 调试模式（开发时设为 True，生产环境设为 False）
    DEBUG: bool = True

    # 服务监听地址
    HOST: str = "0.0.0.0"

    # 服务端口
    PORT: int = 8000

    # ==================== DeepSeek API 配置 ====================

    # DeepSeek API 密钥（从 .env 文件读取）
    # 如果 .env 里没有配置，返回 None
    DEEPSEEK_API_KEY: str | None = os.getenv("DEEPSEEK_API_KEY")

    # DeepSeek API 地址（使用兼容 OpenAI 格式的接口）
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"

    # 使用的模型名称
    DEEPSEEK_MODEL: str = "deepseek-chat"


# 创建全局配置实例
settings = Settings()
