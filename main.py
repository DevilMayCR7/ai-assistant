"""
AI 聊天助手项目的入口文件
运行命令：uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# 导入路由模块
from app.api.chat import router as chat_router
from app.api.wechat import router as wechat_router

# 创建 FastAPI 应用实例
app = FastAPI(
    title="AI 聊天助手",
    description="一个简单的 FastAPI 项目，已接入 DeepSeek AI 聊天和微信消息功能",
    version="0.1.0"
)

# 注册静态文件服务
# 把 app/static 目录挂载到 /static 路径，前端页面可以引用这里的 CSS、JS 文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 注册路由
app.include_router(chat_router)
app.include_router(wechat_router)


@app.get("/")
async def root():
    """
    根路径重定向到聊天页面
    访问 http://127.0.0.1:8000/ 自动跳转到 http://127.0.0.1:8000/chat
    """
    return RedirectResponse(url="/chat")


# 启动时的入口（直接运行 python main.py 时启动）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
