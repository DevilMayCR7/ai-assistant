# Gewechat 微信接入安装指南（Windows）

## 一、准备工作

### 1. 注册一个微信小号

> **重要警告**：Gewechat 使用微信个人号协议，存在被封号风险。**务必使用小号，不要用主号。**

### 2. 安装 Docker Desktop（Windows）

1. 打开 https://www.docker.com/products/docker-desktop/
2. 下载 Windows 版本并安装
3. 安装过程中如果提示启用 WSL2，点击确定（需要重启电脑）
4. 重启后打开 Docker Desktop，等待左下角显示 **Docker Engine running**

验证 Docker 是否可用：

```bash
docker --version
```

---

## 二、启动 Gewechat 服务端

### 1. 打开 PowerShell，拉取镜像

```powershell
docker pull registry.cn-hangzhou.aliyuncs.com/gewe/gewe:latest
```

> 如果上面的镜像拉取失败，可以尝试备用镜像：
> ```powershell
> docker pull hanxi/gewe:latest
> ```

### 2. 运行容器

```powershell
docker run -itd --name=gewe -p 2531:2531 -p 2532:2532 registry.cn-hangzhou.aliyuncs.com/gewe/gewe:latest
```

参数说明：
- `-itd`：后台运行
- `--name=gewe`：容器名叫 gewe
- `-p 2531:2531`：映射端口 2531（API 端口）
- `-p 2532:2532`：映射端口 2532（回调端口）

### 3. 验证服务端是否启动

```powershell
# 查看容器状态
docker ps

# 应该能看到 gewe 容器在运行
```

浏览器访问 http://127.0.0.1:2531/v2/api 测试是否通。

---

## 三、登录微信

### 1. 获取登录二维码

浏览器打开：

```
http://127.0.0.1:2531/v2/api/login/getQrCode
```

或者直接用 Python 获取：

```python
import requests

res = requests.get("http://127.0.0.1:2531/v2/api/login/getQrCode")
print(res.json())
```

返回的 JSON 中会有 `qrCodeUrl` 或 `qrCodeBase64`，用手机微信扫码登录。

### 2. 检查登录状态

扫码后调用：

```
http://127.0.0.1:2531/v2/api/login/checkLogin
```

返回 `isLogin: true` 表示登录成功。

---

## 四、配置消息回调

### 1. 确保 FastAPI 服务已启动

```bash
venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 9000
```

### 2. 设置回调地址

Gewechat 需要知道把消息推送到哪里，调用以下接口设置回调：

```python
import requests

callback_url = "http://你的电脑IP:9000/wechat/callback"

res = requests.post(
    "http://127.0.0.1:2531/v2/api/tools/setCallback",
    json={"token": "", "callbackUrl": callback_url}
)
print(res.json())
```

> `你的电脑IP` 用 `ipconfig` 查到的局域网 IP（如 `192.168.43.237`）
>
> 如果 Gewechat 和 FastAPI 在同一台机器，也可以用 `http://host.docker.internal:9000/wechat/callback`

---

## 五、验证消息接收

1. 用另一个微信给登录的微信号发消息
2. 查看 FastAPI 控制台输出，应该能看到打印的消息内容
3. 或者在群里发消息，也能看到群名、发送人、消息内容

---

## 六、常见问题

| 问题 | 解决 |
|------|------|
| Docker 启动失败 | 确保 BIOS 中开启了虚拟化（Intel VT-x / AMD-V） |
| 端口被占用 | 改端口：`docker run ... -p 2533:2531` |
| 扫码后显示异地登录 | 正常现象，点击确认登录 |
| 收不到消息 | 检查回调地址是否正确、防火墙是否放行端口 |
| 容器掉了 | `docker start gewe` 重新启动 |

---

## 七、项目文件说明

接入后新增的文件：

| 文件 | 作用 |
|------|------|
| `app/api/wechat.py` | 微信消息回调路由 |
| `app/service/wechat_service.py` | Gewechat 客户端封装 |
| `gewechat_setup.md` | 本文档 |
