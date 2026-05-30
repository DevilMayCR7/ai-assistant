"""
微信消息回调路由
接收 Gewechat 服务端推送的微信消息，解析并打印
"""

from fastapi import APIRouter, Request

# 创建路由实例
# prefix="/wechat" 表示所有接口路径前自动加 /wechat
router = APIRouter(prefix="/wechat", tags=["微信"])


@router.post("/callback")
async def wechat_callback(request: Request):
    """
    Gewechat 消息回调接口
    Gewechat 服务端会把收到的微信消息推送到这个地址

    请求来源：Gewechat Docker 容器
    请求格式：JSON，包含消息类型、发送人、内容等信息
    """
    # 获取 Gewechat 推送的原始消息数据
    data = await request.json()

    # 打印原始数据，方便调试和查看消息结构
    print("\n========== 收到微信消息 ==========")
    print(f"原始数据: {data}")
    print("==================================\n")

    # 解析消息内容
    _parse_message(data)

    # 返回成功响应，告诉 Gewechat 已收到
    return {"status": "ok"}


@router.get("/test")
async def wechat_test():
    """
    测试接口：验证 /wechat 路由是否正常工作
    访问地址：http://127.0.0.1:9000/wechat/test
    """
    return {"message": "微信回调路由正常"}


def _parse_message(data: dict):
    """
    解析 Gewechat 推送的消息

    目前只处理群聊文本消息，其他类型先跳过
    """
    # 获取消息类型
    msg_type = data.get("type", "")

    # 只处理 'AddMsg' 类型（新消息）
    if msg_type != "AddMsg":
        print(f"[跳过] 非文本消息类型: {msg_type}")
        return

    # 获取消息详情
    msg_data = data.get("data", {})

    # 发送人微信ID
    from_user = msg_data.get("fromUserName", "")
    # 接收人微信ID（群聊时是群ID）
    to_user = msg_data.get("toUserName", "")
    # 消息内容
    content = msg_data.get("content", "")
    # 消息类型编号（1=文本，3=图片，34=语音，47=表情等）
    msg_type_id = msg_data.get("msgType", 0)

    # 只处理文本消息（msgType=1）
    if msg_type_id != 1:
        print(f"[跳过] 非文本消息，类型编号: {msg_type_id}")
        return

    # 判断是否是群聊消息
    # 群聊ID以 @chatroom 结尾
    is_group = from_user.endswith("@chatroom")

    if is_group:
        # ========== 群聊消息 ==========
        # 群聊消息的内容格式通常是："发送人wxid:\n消息内容"
        # 需要拆分出发送人和真实内容
        if ":\n" in content:
            parts = content.split(":\n", 1)
            sender_wxid = parts[0]      # 发送人在群里的wxid
            real_content = parts[1]     # 真实消息内容
        else:
            sender_wxid = "未知"
            real_content = content

        print("【群聊消息】")
        print(f"  群ID:     {from_user}")
        print(f"  发送人:   {sender_wxid}")
        print(f"  内容:     {real_content}")

    else:
        # ========== 私聊消息 ==========
        print("【私聊消息】")
        print(f"  发送人:   {from_user}")
        print(f"  内容:     {content}")
