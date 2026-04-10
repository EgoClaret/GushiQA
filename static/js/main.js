/**
 * 古诗词问答系统前端JavaScript
 * 包含问答交互、表单验证、UI增强等功能
 */

// 全局变量
let currentUser = null;
let chatHistory = [];
let isWaitingForResponse = false;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * 初始化应用
 */
function initializeApp() {
    console.log('古诗词问答系统初始化...');
    
    // 检查用户登录状态
    checkUserStatus();
    
    // 初始化聊天功能
    if (document.getElementById('chatMessages')) {
        initializeChat();
    }
    
    // 初始化表单验证
    initializeFormValidation();
    
    // 初始化其他功能
    initializeFeatures();
}

/**
 * 检查用户登录状态
 */
function checkUserStatus() {
    // 这里可以通过AJAX请求检查用户登录状态
    // 为了简化，我们使用本地存储来模拟
    const user = localStorage.getItem('currentUser');
    if (user) {
        currentUser = JSON.parse(user);
        updateUIForLoggedInUser();
    }
}

/**
 * 更新已登录用户的UI
 */
function updateUIForLoggedInUser() {
    const userInfo = document.getElementById('userInfo');
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    
    if (userInfo && currentUser) {
        userInfo.innerHTML = `
            <div class="dropdown dropdown-end">
                <label tabindex="0" class="btn btn-ghost btn-circle avatar">
                    <div class="w-10 rounded-full">
                        <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=${currentUser.username}" />
                    </div>
                </label>
                <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
                    <li>
                        <a class="justify-between">
                            个人资料
                            <span class="badge">New</span>
                        </a>
                    </li>
                    <li><a>问答历史</a></li>
                    <li><a>设置</a></li>
                    <li><a onclick="logout()">退出登录</a></li>
                </ul>
            </div>
        `;
        userInfo.style.display = 'block';
    }
    
    if (loginBtn) loginBtn.style.display = 'none';
    if (registerBtn) registerBtn.style.display = 'none';
}

/**
 * 初始化聊天功能
 */
function initializeChat() {
    console.log('初始化聊天功能...');
    
    // 加载聊天记录
    loadChatHistory();
    
    // 绑定事件监听器
    const questionInput = document.getElementById('questionInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearBtn = document.getElementById('clearBtn');
    
    if (questionInput) {
        questionInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendQuestion();
            }
        });
    }
    
    if (sendBtn) {
        sendBtn.addEventListener('click', sendQuestion);
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', clearChat);
    }
    
    // 显示欢迎消息
    showWelcomeMessage();
}

/**
 * 显示欢迎消息
 */
function showWelcomeMessage() {
    const welcomeMessages = [
        "您好！我是小诗，一个专门回答古诗词问题的AI助手。您可以问我关于诗人、诗词、朝代等各种问题。",
        "欢迎来到古诗词问答系统！我可以帮您查找诗人信息、诗词内容、历史背景等。请随时提问！",
        "您好！我是您的古诗词助手小诗。无论是唐诗宋词还是元曲明清小说，我都能为您解答相关问题。"
    ];
    
    const randomMessage = welcomeMessages[Math.floor(Math.random() * welcomeMessages.length)];
    addMessageToChat('bot', randomMessage);
}

/**
 * 发送问题
 */
async function sendQuestion() {
    if (isWaitingForResponse) return;
    
    const questionInput = document.getElementById('questionInput');
    const question = questionInput.value.trim();
    
    if (!question) {
        showNotification('请输入您的问题', 'warning');
        return;
    }
    
    if (question.length < 2) {
        showNotification('问题长度至少为2个字符', 'warning');
        return;
    }
    
    // 添加用户消息到聊天界面
    addMessageToChat('user', question);
    questionInput.value = '';
    
    // 显示输入提示
    showTypingIndicator();
    
    // 禁用发送按钮
    setSendButtonState(false);
    isWaitingForResponse = true;
    
    try {
        // 发送请求到后端
        const response = await fetch('/KGQA_Poetry_Answer', {
            method: 'POST',
            headers: {
                'Content-Type': application/json',
            },
            body: JSON.stringify({
                prompts: chatHistory
            })
        });
        
        if (!response.ok) {
            throw new Error('网络请求失败');
        }
        
        const answer = await response.text();
        
        // 移除输入提示
        removeTypingIndicator();
        
        // 添加回答到聊天界面
        addMessageToChat('bot', answer);
        
        // 保存到聊天记录
        saveChatHistory();
        
    } catch (error) {
        console.error('获取回答失败:', error);
        removeTypingIndicator();
        addMessageToChat('bot', '抱歉，暂时无法回答您的问题。请稍后再试，或者联系技术支持。');
    } finally {
        setSendButtonState(true);
        isWaitingForResponse = false;
    }
}

/**
 * 添加消息到聊天界面
 */
function addMessageToChat(sender, message) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = sender === 'user' ? '👤' : '🤖';
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.textContent = avatar;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.innerHTML = message; // 使用innerHTML支持Markdown格式
    
    if (sender === 'user') {
        messageDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(avatarDiv);
    } else {
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(bubbleDiv);
    }
    
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // 更新聊天记录
    chatHistory.push({
        sender: sender,
        content: message,
        timestamp: new Date().toISOString()
    });
}

/**
 * 显示输入提示
 */
function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'message bot';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-bubble">
            <span class="typing">小诗正在思考中</span>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * 移除输入提示
 */
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

/**
 * 设置发送按钮状态
 */
function setSendButtonState(enabled) {
    const sendBtn = document.getElementById('sendBtn');
    const questionInput = document.getElementById('questionInput');
    
    if (sendBtn) {
        sendBtn.disabled = !enabled;
        sendBtn.innerHTML = enabled ? '发送' : '<span class="loading"></span>';
    }
    
    if (questionInput) {
        questionInput.disabled = !enabled;
    }
}

/**
 * 清空聊天记录
 */
function clearChat() {
    if (confirm('确定要清空聊天记录吗？')) {
        chatHistory = [];
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
        }
        localStorage.removeItem('chatHistory');
        showWelcomeMessage();
        showNotification('聊天记录已清空', 'success');
    }
}

/**
 * 加载聊天记录
 */
function loadChatHistory() {
    const saved = localStorage.getItem('chatHistory');
    if (saved) {
        try {
            chatHistory = JSON.parse(saved);
            // 显示历史记录
            chatHistory.forEach(msg => {
                if (msg.sender !== 'system') {
                    addMessageToChat(msg.sender, msg.content);
                }
            });
        } catch (e) {
            console.error('加载聊天记录失败:', e);
        }
    }
}

/**
 * 保存聊天记录
 */
function saveChatHistory() {
    try {
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    } catch (e) {
        console.error('保存聊天记录失败:', e);
    }
}

/**
 * 初始化表单验证
 */
function initializeFormValidation() {
    // 注册表单验证
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', validateRegisterForm);
    }
    
    // 登录表单验证
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', validateLoginForm);
    }
    
    // 邮箱验证码功能
    const sendCaptchaBtn = document.getElementById('sendCaptchaBtn');
    if (sendCaptchaBtn) {
        sendCaptchaBtn.addEventListener('click', sendEmailCaptcha);
    }
}

/**
 * 验证注册表单
 */
function validateRegisterForm(e) {
    e.preventDefault();
    
    const form = e.target;
    const email = form.email.value.trim();
    const username = form.username.value.trim();
    const password = form.password.value;
    const passwordConfirm = form.password_confirm.value;
    const captcha = form.captcha.value.trim();
    
    // 验证邮箱格式
    if (!validateEmail(email)) {
        showNotification('请输入有效的邮箱地址', 'error');
        return false;
    }
    
    // 验证用户名
    if (username.length < 3 || username.length > 20) {
        showNotification('用户名长度应在3-20个字符之间', 'error');
        return false;
    }
    
    // 验证密码
    if (password.length < 6) {
        showNotification('密码长度至少为6位', 'error');
        return false;
    }
    
    if (password !== passwordConfirm) {
        showNotification('两次输入的密码不一致', 'error');
        return false;
    }
    
    // 验证验证码
    if (captcha.length !== 6) {
        showNotification('验证码应为6位字符', 'error');
        return false;
    }
    
    // 表单验证通过，提交表单
    form.submit();
}

/**
 * 验证登录表单
 */
function validateLoginForm(e) {
    const form = e.target;
    const email = form.email.value.trim();
    const password = form.password.value;
    
    // 验证邮箱格式
    if (!validateEmail(email)) {
        showNotification('请输入有效的邮箱地址', 'error');
        e.preventDefault();
        return false;
    }
    
    // 验证密码
    if (password.length < 6) {
        showNotification('密码长度至少为6位', 'error');
        e.preventDefault();
        return false;
    }
}

/**
 * 发送邮箱验证码
 */
async function sendEmailCaptcha() {
    const email = document.getElementById('email').value.trim();
    const btn = document.getElementById('sendCaptchaBtn');
    
    if (!validateEmail(email)) {
        showNotification('请输入有效的邮箱地址', 'error');
        return;
    }
    
    // 禁用按钮
    btn.disabled = true;
    btn.innerHTML = '发送中...';
    
    try {
        const response = await fetch('/send_captcha', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });
        
        if (response.ok) {
            showNotification('验证码已发送到您的邮箱', 'success');
            startCountdown(btn, 60);
        } else {
            const error = await response.json();
            showNotification(error.message || '发送失败，请重试', 'error');
            btn.disabled = false;
            btn.innerHTML = '发送验证码';
        }
    } catch (error) {
        console.error('发送验证码失败:', error);
        showNotification('网络错误，请检查连接', 'error');
        btn.disabled = false;
        btn.innerHTML = '发送验证码';
    }
}

/**
 * 开始倒计时
 */
function startCountdown(button, seconds) {
    let remaining = seconds;
    const timer = setInterval(() => {
        button.innerHTML = `${remaining}秒后重试`;
        remaining--;
        
        if (remaining < 0) {
            clearInterval(timer);
            button.disabled = false;
            button.innerHTML = '发送验证码';
        }
    }, 1000);
}

/**
 * 验证邮箱格式
 */
function validateEmail(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}

/**
 * 显示通知消息
 */
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fixed top-4 right-4 z-50`;
    notification.innerHTML = `
        <div class="flex items-center">
            <span>${message}</span>
            <button class="ml-2 btn btn-sm btn-ghost" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // 自动移除
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

/**
 * 初始化其他功能
 */
function initializeFeatures() {
    // 添加平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // 添加页面加载动画
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease-in-out';
        document.body.style.opacity = '1';
    }, 100);
}

/**
 * 用户登出
 */
function logout() {
    if (confirm('确定要退出登录吗？')) {
        localStorage.removeItem('currentUser');
        currentUser = null;
        location.reload();
    }
}

// 工具函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// 导出函数供其他脚本使用
window.PoetryQA = {
    sendQuestion,
    clearChat,
    showNotification,
    validateEmail
};