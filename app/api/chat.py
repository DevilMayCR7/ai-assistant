"""
聊天相关的 API 路由
定义客户端可以调用的接口，包括 API 接口和聊天页面
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

# 导入数据模型
from app.model.schemas import ChatMessageRequest, ChatMessageResponse, HelloResponse

# 导入聊天服务（封装了 DeepSeek API 调用）
from app.service.chat_service import chat_service

# 创建路由实例
# prefix="/chat" 表示所有接口路径前自动加 /chat
# tags=["聊天"] 用于 Swagger 文档分组
router = APIRouter(prefix="/chat", tags=["聊天"])

# 配置模板引擎，指定模板文件存放目录
templates = Jinja2Templates(directory="app/templates")


# ==================== 页面路由 ====================

@router.get("")
async def chat_page(request: Request):
    """
    聊天页面入口
    访问地址：http://127.0.0.1:8000/chat
    返回渲染后的 HTML 聊天页面
    """
    return templates.TemplateResponse("chat.html", {"request": request})


# ==================== 测试接口 ====================

@router.get("/hello", response_model=HelloResponse)
async def hello():
    """
    测试接口：返回 hello world
    访问地址：http://127.0.0.1:8000/chat/hello
    """
    return {"message": "hello world"}


@router.get("/hello/{name}", response_model=HelloResponse)
async def hello_name(name: str):
    """
    带参数的测试接口：返回个性化的问候
    例如访问：http://127.0.0.1:8000/chat/hello/小明
    """
    return {"message": f"hello {name}"}


# ==================== 核心聊天接口 ====================

@router.post("", response_model=ChatMessageResponse)
async def chat(request: ChatMessageRequest):
    """
    聊天接口：接收用户消息，调用 DeepSeek AI 返回回复

    请求示例：
        POST /chat
        {
            "message": "你好"
        }

    响应示例：
        {
            "answer": "你好！很高兴见到你。"
        }
    """
    try:
        # 调用服务层的 chat_with_ai 方法
        # await 是因为这个方法内部发送了异步 HTTP 请求
        answer = await chat_service.chat_with_ai(request.message)

        # 返回统一的响应格式
        return ChatMessageResponse(answer=answer)

    except ValueError as e:
        # 配置类错误（如 API 密钥未设置）
        # 返回 500 状态码，并在响应体中携带错误信息
        raise HTTPException(status_code=500, detail=str(e))

    except RuntimeError as e:
        # 运行时错误（如网络异常、API 返回错误）
        raise HTTPException(status_code=502, detail=str(e))

    except Exception as e:
        # 捕获所有未预料到的异常，防止服务器崩溃
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {e}")
