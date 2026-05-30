# Gewechat Windows Docker Desktop 部署修复指南

## 一、报错原因

你遇到的错误：

```
Failed to mount tmpfs at /run: Operation not permitted
Failed to mount cgroup at /sys/fs/cgroup/systemd: Operation not permitted
Failed to mount API filesystems, freezing.
```

**根本原因**：Gewechat 镜像内部使用 **systemd** 作为 1 号进程管理微信服务，而 systemd 需要挂载 tmpfs、cgroup 等系统文件。Windows Docker Desktop 的 WSL2 后端对这类特权操作有限制，即使加了 `--privileged` 也不一定能直接通过。

---

## 二、解决方案（按推荐顺序）

### 方案一：配置 WSL2 原生支持 systemd（推荐）

这是**最稳妥**的方案，让 WSL2 本身支持 systemd，从而容器内的 systemd 也能正常工作。

**步骤 1：进入 WSL2 Ubuntu 终端**

在 PowerShell 中执行：

```powershell
wsl -d Ubuntu
```

（如果你的发行版不叫 Ubuntu，用 `wsl -l` 查看名称）

**步骤 2：创建/编辑 wsl.conf**

```bash
sudo tee /etc/wsl.conf << 'EOF'
[boot]
systemd=true
EOF
```

**步骤 3：重启 WSL2**

在 PowerShell（不是 WSL 内）中执行：

```powershell
wsl --shutdown
```

等待几秒，重新打开 Docker Desktop。

**步骤 4：删除之前失败的容器**

```powershell
docker rm -f gewe
```

**步骤 5：用正确命令启动 Gewechat**

```powershell
# 先创建数据目录（在 WSL2 中）
wsl -d Ubuntu mkdir -p /root/temp

# 启动容器（在 PowerShell 中执行）
docker run -itd `
  --name=gewe `
  --privileged=true `
  --cgroupns=private `
  --tmpfs /run `
  --tmpfs /tmp `
  -v /root/temp:/root/temp `
  -p 2531:2531 `
  -p 2532:2532 `
  registry.cn-hangzhou.aliyuncs.com/gewe/gewe:latest `
  /usr/sbin/init
```

> **注意**：最后一行 `/usr/sbin/init` 是启动命令，必须加上！

**步骤 6：验证**

```powershell
docker logs gewe -f
```

等待 10~30 秒，不再出现 `freezing` 错误，说明启动成功。

---

### 方案二：直接在 WSL2 中安装 Docker Engine（绕过 Docker Desktop）

如果你方案一试了还是不行，或者想一劳永逸解决 Windows 上 systemd 容器的问题，可以**在 WSL2 Ubuntu 内部直接安装 Docker**，不走 Docker Desktop。

**优点**：WSL2 原生 Docker 对 systemd 容器兼容性更好。  
**缺点**：没有 Docker Desktop 的图形界面。

**步骤 1：进入 WSL2 Ubuntu**

```powershell
wsl -d Ubuntu
```

**步骤 2：安装 Docker Engine**

```bash
# 更新软件源
sudo apt update

# 安装依赖
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 软件源
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 把当前用户加入 docker 组（免 sudo）
sudo usermod -aG docker $USER
```

**步骤 3：退出并重新进入 WSL2**

```bash
exit
```

然后重新 `wsl -d Ubuntu` 进入，让用户组生效。

**步骤 4：启动 Gewechat**

```bash
# 在 WSL2 Ubuntu 中执行
sudo mkdir -p /root/temp

sudo docker run -itd \
  --name=gewe \
  --privileged=true \
  -v /root/temp:/root/temp \
  -p 2531:2531 \
  -p 2532:2532 \
  registry.cn-hangzhou.aliyuncs.com/gewe/gewe:latest \
  /usr/sbin/init
```

---

## 三、命令参数说明

| 参数 | 是否必须 | 说明 |
|------|---------|------|
| `--privileged=true` | **必须** | 授予容器特权，systemd 需要挂载 cgroup、tmpfs |
| `/usr/sbin/init` | **必须** | 容器的启动命令，用 systemd 作为 1 号进程 |
| `--cgroupns=private` | 建议加 | 为容器创建独立的 cgroup 命名空间 |
| `--tmpfs /run` | 建议加 | 显式挂载 /run 为 tmpfs，避免容器自己挂载失败 |
| `--tmpfs /tmp` | 建议加 | 显式挂载 /tmp 为 tmpfs |
| `-v /root/temp:/root/temp` | 建议加 | 数据持久化，容器重启后数据不丢失 |
| `-p 2531:2531` | 必须 | API 服务端口 |
| `-p 2532:2532` | 必须 | 文件下载端口 |

---

## 四、常见问题

### Q1：方案一配置了 systemd=true 还是报错？

确保 `wsl --shutdown` 后**等待 5 秒以上**再重新打开 Docker Desktop。WSL2 关机需要时间。

### Q2：怎么确认容器真的启动了？

```powershell
docker ps
```

看 STATUS 是不是 `Up xxx seconds`，不是 `Restarting` 或 `Exited`。

### Q3：WSL2 Ubuntu 怎么进？

```powershell
wsl -l -v          # 查看所有发行版
wsl -d Ubuntu      # 进入 Ubuntu
```

如果你的发行版叫 `Ubuntu-22.04`，就用 `wsl -d Ubuntu-22.04`。

### Q4：Docker Desktop 和 WSL2 内部 Docker 会冲突吗？

不会。WSL2 内部的 Docker Engine 和 Docker Desktop 是两个独立的 Docker Daemon，端口不冲突。但建议**二选一**，不要同时运行。

---

## 五、下一步

容器成功启动后，继续按 `gewechat_setup.md` 的步骤：

1. 浏览器访问 `http://127.0.0.1:2531/v2/api/login/getQrCode` 获取二维码
2. 微信扫码登录
3. 设置回调地址到 FastAPI
4. 发消息测试
