"""
项目配置文件
集中管理所有可配置项
从 .env 文件读取敏感配置（如 API 密钥、数据库密码）
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()


class Settings:
    """
    项目设置类
    所有配置项都在这里定义
    """

    # 应用名称
    APP_NAME: str = "AI 聊天助手"

    # 应用版本
    APP_VERSION: str = "0.2.0"

    # 调试模式（开发时设为 True，生产环境设为 False）
    DEBUG: bool = True

    # 服务监听地址
    HOST: str = "0.0.0.0"

    # 服务端口
    PORT: int = 8000

    # ==================== DeepSeek API 配置 ====================

    # DeepSeek API 密钥（从 .env 文件读取）
    DEEPSEEK_API_KEY: str | None = os.getenv("DEEPSEEK_API_KEY")

    # DeepSeek API 地址
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"

    # 使用的模型名称
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # ==================== MySQL 数据库配置 ====================

    # 数据库主机地址
    DB_HOST: str = os.getenv("DB_HOST", "localhost")

    # 数据库端口
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))

    # 数据库用户名
    DB_USER: str = os.getenv("DB_USER", "root")

    # 数据库密码（从 .env 读取，如果没有则使用默认值）
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # 数据库名
    DB_NAME: str = os.getenv("DB_NAME", "ai_chat")

    # 数据库连接池大小
    DB_POOL_SIZE: int = 10

    # 是否打印 SQL 语句（调试用）
    DB_ECHO: bool = False

    @property
    def database_url(self) -> str:
        """
        构造异步 MySQL 数据库连接字符串

        格式: mysql+asyncmy://用户名:密码@主机:端口/数据库名?charset=utf8mb4
        """
        return (
            f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )


# 创建全局配置实例
settings = Settings()
