/**
 * 聊天页面前端逻辑
 * 负责：获取用户输入、调用后端 API、显示聊天记录
 */

// ==================== 获取页面元素 ====================

// 聊天记录容器：所有消息都会添加到这里面
const chatContainer = document.getElementById('chat-container');

// 消息输入框：用户打字的地方
const messageInput = document.getElementById('message-input');

// 发送按钮：点击或按回车时触发发送
const sendBtn = document.getElementById('send-btn');

// 标记当前是否正在等待 AI 回复，防止重复发送
let isWaiting = false;


// ==================== 核心功能：发送消息 ====================

/**
 * 发送消息的主函数
 * 流程：获取输入 → 显示用户消息 → 调用 API → 显示 AI 回复
 */
async function sendMessage() {
    // 获取输入框中的文字，并去掉首尾空格
    const text = messageInput.value.trim();

    // 如果输入为空，或者正在等待 AI 回复，直接返回不做任何操作
    if (!text || isWaiting) {
        return;
    }

    // 清空输入框
    messageInput.value = '';
    // 把输入框高度重置为默认的一行
    messageInput.style.height = 'auto';

    // 第 1 步：在页面上显示用户发送的消息
    addUserMessage(text);

    // 第 2 步：显示"AI 正在输入..."的加载动画
    const loadingId = addLoadingMessage();

    // 设置状态为等待中，禁用发送按钮
    isWaiting = true;
    sendBtn.disabled = true;

    try {
        // 第 3 步：调用后端 API
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'  // 告诉服务器发送的是 JSON 格式
            },
            body: JSON.stringify({ message: text })  // 把消息对象转成 JSON 字符串
        });

        // 第 4 步：解析服务器返回的数据
        const data = await response.json();

        // 第 5 步：移除加载动画
        removeLoadingMessage(loadingId);

        // 检查请求是否成功
        if (response.ok) {
            // 成功：显示 AI 的回复
            addAssistantMessage(data.answer);
        } else {
            // 失败：显示错误信息
            addAssistantMessage('抱歉，出错了：' + (data.detail || '未知错误'));
        }

    } catch (error) {
        // 网络错误（如服务器没启动、断网）
        removeLoadingMessage(loadingId);
        addAssistantMessage('网络异常，请检查服务是否正常运行。');
        console.error('请求失败:', error);
    } finally {
        // 无论成功还是失败，都要恢复发送按钮状态
        isWaiting = false;
        sendBtn.disabled = false;
    }
}


// ==================== 显示消息的函数 ====================

/**
 * 在页面上添加一条用户消息
 * @param {string} text - 用户输入的文字内容
 */
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="avatar">我</div>
        <div class="bubble">${escapeHtml(text)}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();  // 自动滚动到最底部
}

/**
 * 在页面上添加一条 AI 回复消息
 * @param {string} text - AI 回复的文字内容
 */
function addAssistantMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant-message';
    messageDiv.innerHTML = `
        <div class="avatar">AI</div>
        <div class="bubble">${escapeHtml(text)}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * 显示"AI 正在输入"的加载动画
 * @returns {string} 返回该加载元素的 ID，方便后面移除
 */
function addLoadingMessage() {
    const id = 'loading-' + Date.now();  // 用时间戳生成唯一 ID
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant-message';
    messageDiv.id = id;
    messageDiv.innerHTML = `
        <div class="avatar">AI</div>
        <div class="bubble loading">
            <span></span><span></span><span></span>
        </div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
    return id;
}

/**
 * 移除加载动画
 * @param {string} id - 要移除的加载元素 ID
 */
function removeLoadingMessage(id) {
    const el = document.getElementById(id);
    if (el) {
        el.remove();
    }
}


// ==================== 辅助函数 ====================

/**
 * 将聊天区域滚动到最底部
 * 这样用户总能看到最新的消息
 */
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * 转义 HTML 特殊字符，防止 XSS 攻击
 * 例如：用户输入 <script> 会被转成 &lt;script&gt;
 * @param {string} text - 原始文本
 * @returns {string} 转义后的安全文本
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 自动调整输入框高度
 * 根据输入内容的行数动态增高，最多到 max-height（CSS 中设置的 120px）
 */
function autoResize() {
    messageInput.style.height = 'auto';           // 先重置高度
    messageInput.style.height = messageInput.scrollHeight + 'px';  // 再设为内容的实际高度
}


// ==================== 事件绑定 ====================

// 点击发送按钮时发送消息
sendBtn.addEventListener('click', sendMessage);

// 输入框内容变化时自动调整高度
messageInput.addEventListener('input', autoResize);

// 在输入框中按下键盘时的处理
messageInput.addEventListener('keydown', function(event) {
    // 判断是否按下了回车键（Enter）
    if (event.key === 'Enter') {
        // 如果同时按下了 Shift 键，允许换行（不发送）
        if (event.shiftKey) {
            return;  // 不做任何处理，让默认行为生效（插入换行）
        }
        // 否则阻止默认行为（不插入换行），直接发送消息
        event.preventDefault();
        sendMessage();
    }
});
