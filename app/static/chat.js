/**
 * 聊天页面前端逻辑
 * 负责：获取用户输入、调用后端 API、显示聊天记录、管理会话状态
 */

// ==================== 全局状态 ====================

// 当前用户ID，固定为1（后续可扩展为登录系统）
const currentUserId = 1;

// 当前会话ID，null 表示还没有会话
// 第一次发送消息时不带 session_id，后端会自动创建新会话并返回
// 后续发送消息时自动携带这个 session_id，实现上下文续接
let currentSessionId = null;

// 标记当前是否正在等待 AI 回复，防止重复发送
let isWaiting = false;


// ==================== 获取页面元素 ====================

const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');


// ==================== 核心功能：发送消息 ====================

/**
 * 发送消息的主函数
 *
 * 流程：
 *   1. 获取输入内容
 *   2. 构造请求体（第一次不带 session_id，后续带）
 *   3. 显示用户消息
 *   4. 调用后端 API
 *   5. 保存后端返回的 session_id
 *   6. 显示 AI 回复
 */
async function sendMessage() {
    // 获取输入框中的文字，并去掉首尾空格
    const text = messageInput.value.trim();

    // 如果输入为空，或者正在等待 AI 回复，直接返回
    if (!text || isWaiting) {
        return;
    }

    // 清空输入框
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // 在页面上显示用户发送的消息
    addUserMessage(text);

    // 显示"AI 正在输入..."的加载动画
    const loadingId = addLoadingMessage();

    // 禁用发送按钮
    isWaiting = true;
    sendBtn.disabled = true;

    try {
        // 构造请求体
        // 如果 currentSessionId 有值，说明已经有会话了，带上它
        // 如果 currentSessionId 为 null，说明是第一次聊天，不带 session_id
        const requestBody = {
            user_id: currentUserId,
            message: text
        };

        if (currentSessionId !== null) {
            requestBody.session_id = currentSessionId;
        }

        // 调用后端 API
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        // 解析服务器返回的数据
        const data = await response.json();

        // 移除加载动画
        removeLoadingMessage(loadingId);

        // 检查请求是否成功
        if (response.ok) {
            // 保存后端返回的 session_id
            // 第一次聊天时后端会创建新会话并返回 session_id
            // 后续聊天时后端会返回同一个 session_id
            if (data.session_id !== undefined) {
                currentSessionId = data.session_id;
                console.log('当前会话ID:', currentSessionId);
            }

            // 显示 AI 的回复
            addAssistantMessage(data.answer);
        } else {
            // 失败：显示错误信息
            addAssistantMessage('抱歉，出错了：' + (data.detail || '未知错误'));
        }

    } catch (error) {
        // 网络错误
        removeLoadingMessage(loadingId);
        addAssistantMessage('网络异常，请检查服务是否正常运行。');
        console.error('请求失败:', error);
    } finally {
        // 恢复发送按钮状态
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
    scrollToBottom();
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
    const id = 'loading-' + Date.now();
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
 */
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * 转义 HTML 特殊字符，防止 XSS 攻击
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
 */
function autoResize() {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
}


// ==================== 事件绑定 ====================

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('input', autoResize);

messageInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        if (event.shiftKey) {
            return;
        }
        event.preventDefault();
        sendMessage();
    }
});
