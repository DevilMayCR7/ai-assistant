"""
Gewechat 客户端服务
封装与 Gewechat Docker 服务端的交互，包括登录、设置回调等
"""

import requests
from app.config.settings import settings


class WechatService:
    """
    微信服务类
    负责与 Gewechat Docker 容器通信，管理微信登录和消息回调
    """

    def __init__(self):
        """
        初始化微信服务
        默认连接本机的 Gewechat Docker 容器
        """
        # Gewechat 服务端地址（Docker 映射的端口）
        self.base_url = "http://127.0.0.1:2531/v2/api"

    def get_login_qr(self) -> dict:
        """
        获取微信登录二维码

        返回:
            包含二维码信息的字典
        """
        url = f"{self.base_url}/login/getQrCode"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取二维码失败: {e}")
            return {}

    def check_login(self) -> dict:
        """
        检查微信登录状态

        返回:
            登录状态信息，isLogin=true 表示已登录
        """
        url = f"{self.base_url}/login/checkLogin"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"检查登录状态失败: {e}")
            return {}

    def set_callback(self, callback_url: str) -> dict:
        """
        设置消息回调地址
        Gewechat 收到微信消息后会推送到这个地址

        参数:
            callback_url: FastAPI 的回调接口地址
                         例如：http://192.168.1.100:9000/wechat/callback

        返回:
            设置结果
        """
        url = f"{self.base_url}/tools/setCallback"
        payload = {
            "token": "",
            "callbackUrl": callback_url
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            print(f"设置回调结果: {result}")
            return result
        except requests.RequestException as e:
            print(f"设置回调失败: {e}")
            return {}

    def get_contacts(self) -> list:
        """
        获取微信联系人列表

        返回:
            联系人列表
        """
        url = f"{self.base_url}/contacts/getContacts"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.RequestException as e:
            print(f"获取联系人失败: {e}")
            return []

    def get_room_list(self) -> list:
        """
        获取微信群列表

        返回:
            群列表
        """
        url = f"{self.base_url}/group/getRoomList"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except requests.RequestException as e:
            print(f"获取群列表失败: {e}")
            return []


# 创建单例实例
wechat_service = WechatService()
