"""
AI 聊天助手项目的入口文件
运行命令：uvicorn main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# 导入路由模块
from app.api.chat import router as chat_router
from app.api.wechat import router as wechat_router

# 导入数据库初始化函数
from app.model.database import init_db


# ==================== 应用生命周期管理 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 应用生命周期管理
    启动时自动创建数据库表，关闭时清理资源
    """
    # 启动时：创建数据库表
    print("正在初始化数据库...")
    await init_db()
    print("数据库初始化完成，服务启动成功！")

    yield  # 应用运行期间

    # 关闭时：清理资源
    print("服务正在关闭...")


# ==================== 创建 FastAPI 应用 ====================

app = FastAPI(
    title="AI 聊天助手",
    description="FastAPI + DeepSeek + MySQL 智能聊天系统",
    version="0.2.0",
    lifespan=lifespan,  # 注册生命周期管理
)

# 注册静态文件服务
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 注册路由
app.include_router(chat_router)
app.include_router(wechat_router)


@app.get("/")
async def root():
    """
    根路径重定向到聊天页面
    """
    return RedirectResponse(url="/chat")


# 启动时的入口（直接运行 python main.py 时启动）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
