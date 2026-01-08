// API配置
const API_BASE_URL = 'http://localhost:8000/api';

// PDF.js配置
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

// Markdown 配置
marked.setOptions({
    breaks: true,
    gfm: true,
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(code, { language: lang }).value;
            } catch (e) {}
        }
        return hljs.highlightAuto(code).value;
    }
});

// 全局状态
let currentPDF = null;
let currentPDFDoc = null;
let currentPage = 1;
let totalPages = 0;
let selectedText = '';
let currentConversationId = null;
let viewMode = 'scroll'; // 'page' 或 'scroll'，默认滚动模式

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadPDFList();
    setupEventListeners();
    setupResizers();
});

// 设置事件监听器
function setupEventListeners() {
    // 文本选择
    document.addEventListener('mouseup', handleTextSelection);

    // 隐藏上下文菜单
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.context-menu')) {
            hideContextMenu();
        }
    });
}

// ========== 可调整大小的面板 ==========

function setupResizers() {
    const resizerLeft = document.getElementById('resizer-left');
    const resizerRight = document.getElementById('resizer-right');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const chatSidebar = document.getElementById('chat-sidebar');

    let isResizing = false;
    let currentResizer = null;

    function startResize(e, resizer) {
        isResizing = true;
        currentResizer = resizer;
        document.body.classList.add('resizing');
        resizer.classList.add('resizing');
    }

    function stopResize() {
        isResizing = false;
        document.body.classList.remove('resizing');
        if (currentResizer) {
            currentResizer.classList.remove('resizing');
        }
        currentResizer = null;
    }

    function resize(e) {
        if (!isResizing) return;

        const containerRect = document.querySelector('.container').getBoundingClientRect();

        if (currentResizer === resizerLeft) {
            // 调整左侧边栏宽度
            const newWidth = e.clientX - containerRect.left;
            if (newWidth >= 200 && newWidth <= 400) {
                sidebar.style.width = `${newWidth}px`;
            }
        } else if (currentResizer === resizerRight) {
            // 调整右侧聊天面板宽度
            const newWidth = containerRect.right - e.clientX;
            if (newWidth >= 280 && newWidth <= 600) {
                chatSidebar.style.width = `${newWidth}px`;
            }
        }
    }

    // 鼠标事件
    resizerLeft.addEventListener('mousedown', (e) => startResize(e, resizerLeft));
    resizerRight.addEventListener('mousedown', (e) => startResize(e, resizerRight));

    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);

    // 触摸事件（移动设备支持）
    resizerLeft.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startResize(e.touches[0], resizerLeft);
    });
    resizerRight.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startResize(e.touches[0], resizerRight);
    });

    document.addEventListener('touchmove', (e) => {
        if (isResizing) {
            resize(e.touches[0]);
        }
    });
    document.addEventListener('touchend', stopResize);
}

// ========== PDF管理 ==========

async function loadPDFList() {
    try {
        const response = await fetch(`${API_BASE_URL}/pdfs/`);
        const pdfs = await response.json();

        const listContainer = document.getElementById('pdf-list');
        if (pdfs.length === 0) {
            listContainer.innerHTML = '<p class="empty-message">暂无文档</p>';
            return;
        }

        listContainer.innerHTML = pdfs.map(pdf => `
            <div class="pdf-item" data-pdf-id="${pdf.id}" onclick="loadPDF(${pdf.id}, event)">
                <div class="pdf-item-title">${pdf.original_filename}</div>
                <div class="pdf-item-info">
                    ${pdf.page_count} 页 · ${formatFileSize(pdf.file_size)}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load PDF list:', error);
        showError('加载文档列表失败');
    }
}

async function uploadPDF(event) {
    const file = event.target.files[0];
    if (!file) return;

    showLoading('上传中...');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/pdfs/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');

        const result = await response.json();
        hideLoading();

        // 刷新列表并加载新上传的PDF
        await loadPDFList();
        await loadPDF(result.id);

        showSuccess('上传成功！');
    } catch (error) {
        hideLoading();
        console.error('Upload failed:', error);
        showError('上传失败，请重试');
    }

    // 清空input
    event.target.value = '';
}

async function loadPDF(pdfId, event) {
    showLoading('加载文档...');

    try {
        // 获取PDF信息
        const response = await fetch(`${API_BASE_URL}/pdfs/${pdfId}`);
        const pdfInfo = await response.json();
        currentPDF = pdfInfo;

        // 更新UI
        document.getElementById('welcome-screen').style.display = 'none';
        document.getElementById('pdf-viewer-container').style.display = 'flex';
        document.getElementById('pdf-title').textContent = pdfInfo.original_filename;

        // 更新列表选中状态
        document.querySelectorAll('.pdf-item').forEach(item => {
            item.classList.remove('active');
        });
        if (event && event.target) {
            event.target.closest('.pdf-item')?.classList.add('active');
        } else {
            // 如果没有event，通过pdfId查找
            const pdfItem = document.querySelector(`[data-pdf-id="${pdfId}"]`);
            if (pdfItem) pdfItem.classList.add('active');
        }

        // 加载PDF文档
        const pdfUrl = `${API_BASE_URL}/pdfs/${pdfId}/file`;
        console.log('Loading PDF from:', pdfUrl);

        const loadingTask = pdfjsLib.getDocument({
            url: pdfUrl,
            httpHeaders: {
                'Accept': 'application/pdf'
            },
            withCredentials: false
        });

        currentPDFDoc = await loadingTask.promise;
        totalPages = currentPDFDoc.numPages;
        currentPage = 1;

        // 根据当前视图模式渲染
        if (viewMode === 'scroll') {
            // 确保滚动模式容器显示
            document.getElementById('page-mode-container').style.display = 'none';
            document.getElementById('scroll-mode-container').style.display = 'flex';
            document.getElementById('page-controls').style.display = 'none';
            document.getElementById('btn-page-mode').classList.remove('active');
            document.getElementById('btn-scroll-mode').classList.add('active');
            await renderAllPages();
        } else {
            // 翻页模式
            document.getElementById('page-mode-container').style.display = 'block';
            document.getElementById('scroll-mode-container').style.display = 'none';
            document.getElementById('page-controls').style.display = 'flex';
            document.getElementById('btn-page-mode').classList.add('active');
            document.getElementById('btn-scroll-mode').classList.remove('active');
            await renderPage(currentPage);
        }

        // 更新页码显示
        document.getElementById('page-info').textContent = `${currentPage} / ${totalPages}`;

        // 加载对话历史
        await loadConversationHistory(pdfId);

        hideLoading();
    } catch (error) {
        hideLoading();
        console.error('Failed to load PDF:', error);
        console.error('Error details:', error.message, error.name);
        showError(`加载文档失败: ${error.message || '未知错误'}`);
    }
}

async function renderPage(pageNum) {
    try {
        const page = await currentPDFDoc.getPage(pageNum);
        const canvas = document.getElementById('pdf-canvas');
        const context = canvas.getContext('2d');
        const textLayerDiv = document.getElementById('text-layer');

        const scale = 1.5;
        const viewport = page.getViewport({ scale: scale });
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
            canvasContext: context,
            viewport: viewport
        };

        await page.render(renderContext).promise;

        // 渲染文本层以支持文本选择
        textLayerDiv.innerHTML = '';
        textLayerDiv.style.width = `${viewport.width}px`;
        textLayerDiv.style.height = `${viewport.height}px`;

        const textContent = await page.getTextContent();

        // 使用 PDF.js 的 renderTextLayer API
        pdfjsLib.renderTextLayer({
            textContentSource: textContent,
            container: textLayerDiv,
            viewport: viewport,
            textDivs: []
        });

        // 更新页码显示
        document.getElementById('page-info').textContent = `${pageNum} / ${totalPages}`;
    } catch (error) {
        console.error('Failed to render page:', error);
    }
}

function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        renderPage(currentPage);
    }
}

function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        renderPage(currentPage);
    }
}

// ========== 视图模式切换 ==========

function setViewMode(mode) {
    if (viewMode === mode) return;
    viewMode = mode;

    // 更新按钮状态
    document.getElementById('btn-page-mode').classList.toggle('active', mode === 'page');
    document.getElementById('btn-scroll-mode').classList.toggle('active', mode === 'scroll');

    // 切换显示容器
    const pageModeContainer = document.getElementById('page-mode-container');
    const scrollModeContainer = document.getElementById('scroll-mode-container');
    const pageControls = document.getElementById('page-controls');

    if (mode === 'page') {
        pageModeContainer.style.display = 'block';
        scrollModeContainer.style.display = 'none';
        pageControls.style.display = 'flex';
        // 渲染当前页
        if (currentPDFDoc) {
            renderPage(currentPage);
        }
    } else {
        pageModeContainer.style.display = 'none';
        scrollModeContainer.style.display = 'flex';
        pageControls.style.display = 'none';
        // 渲染所有页面
        if (currentPDFDoc) {
            renderAllPages();
        }
    }
}

async function renderAllPages() {
    const container = document.getElementById('scroll-mode-container');
    container.innerHTML = '<div class="loading-pages">正在加载所有页面...</div>';

    const pages = [];

    for (let i = 1; i <= totalPages; i++) {
        const pageWrapper = document.createElement('div');
        pageWrapper.className = 'pdf-page-wrapper';
        pageWrapper.dataset.pageNum = i;

        // 创建 canvas 和文本层的容器
        const canvasContainer = document.createElement('div');
        canvasContainer.className = 'pdf-canvas-container';
        canvasContainer.style.position = 'relative';
        canvasContainer.style.display = 'inline-block';

        const canvas = document.createElement('canvas');
        canvas.className = 'pdf-page-canvas';
        canvas.id = `pdf-canvas-${i}`;

        const textLayer = document.createElement('div');
        textLayer.className = 'textLayer';
        textLayer.id = `text-layer-${i}`;

        canvasContainer.appendChild(canvas);
        canvasContainer.appendChild(textLayer);

        const pageLabel = document.createElement('div');
        pageLabel.className = 'pdf-page-label';
        pageLabel.textContent = `第 ${i} 页 / 共 ${totalPages} 页`;

        pageWrapper.appendChild(canvasContainer);
        pageWrapper.appendChild(pageLabel);
        pages.push(pageWrapper);
    }

    container.innerHTML = '';
    pages.forEach(page => container.appendChild(page));

    // 渲染所有页面（包括文本层）
    for (let i = 1; i <= totalPages; i++) {
        await renderPageToCanvas(i, `pdf-canvas-${i}`, `text-layer-${i}`);
    }

    // 设置滚动监听，更新当前页码
    setupScrollObserver();
}

async function renderPageToCanvas(pageNum, canvasId, textLayerId) {
    try {
        const page = await currentPDFDoc.getPage(pageNum);
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const context = canvas.getContext('2d');
        const scale = 1.5;
        const viewport = page.getViewport({ scale: scale });

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
            canvasContext: context,
            viewport: viewport
        };

        await page.render(renderContext).promise;

        // 渲染文本层（如果提供了 textLayerId）
        if (textLayerId) {
            const textLayerDiv = document.getElementById(textLayerId);
            if (textLayerDiv) {
                textLayerDiv.innerHTML = '';
                textLayerDiv.style.width = `${viewport.width}px`;
                textLayerDiv.style.height = `${viewport.height}px`;

                const textContent = await page.getTextContent();

                pdfjsLib.renderTextLayer({
                    textContentSource: textContent,
                    container: textLayerDiv,
                    viewport: viewport,
                    textDivs: []
                });
            }
        }
    } catch (error) {
        console.error(`Failed to render page ${pageNum}:`, error);
    }
}

function setupScrollObserver() {
    const container = document.getElementById('scroll-mode-container');
    const pageWrappers = container.querySelectorAll('.pdf-page-wrapper');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
                const pageNum = parseInt(entry.target.dataset.pageNum);
                if (pageNum !== currentPage) {
                    currentPage = pageNum;
                    document.getElementById('page-info').textContent = `${currentPage} / ${totalPages}`;
                }
            }
        });
    }, {
        root: container,
        threshold: 0.5
    });

    pageWrappers.forEach(wrapper => observer.observe(wrapper));
}

// ========== 聊天功能 ==========

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message || !currentPDF) return;

    // 添加用户消息到界面
    addMessage('user', message);
    input.value = '';

    // 显示加载状态
    const loadingMsg = addMessage('assistant', '正在思考...', false);

    try {
        const response = await fetch(`${API_BASE_URL}/chat/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pdf_id: currentPDF.id,
                message: message,
                selected_text: selectedText || null,
                page_number: selectedText ? currentPage : null
            })
        });

        const result = await response.json();

        // 替换加载消息为实际回复（使用Markdown渲染）
        updateMessage(loadingMsg, result.response, true);
        currentConversationId = result.conversation_id;

        // 清空选中文本
        selectedText = '';
    } catch (error) {
        console.error('Chat failed:', error);
        updateMessage(loadingMsg, '❌ 发送失败，请重试', false);
    }
}

function addMessage(role, content, useMarkdown = true) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    if (role === 'assistant' && useMarkdown) {
        // AI 回复使用 Markdown 渲染
        const contentDiv = document.createElement('div');
        contentDiv.className = 'markdown-content';
        contentDiv.innerHTML = renderMarkdown(content);
        messageDiv.appendChild(contentDiv);
    } else {
        // 用户消息保持纯文本
        messageDiv.textContent = content;
    }

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return messageDiv;
}

// Markdown 渲染函数
function renderMarkdown(text) {
    try {
        return marked.parse(text);
    } catch (e) {
        console.error('Markdown parsing error:', e);
        return text;
    }
}

// 更新消息内容（用于替换加载状态）
function updateMessage(messageDiv, content, useMarkdown = true) {
    if (messageDiv.classList.contains('assistant') && useMarkdown) {
        let contentDiv = messageDiv.querySelector('.markdown-content');
        if (!contentDiv) {
            contentDiv = document.createElement('div');
            contentDiv.className = 'markdown-content';
            messageDiv.textContent = '';
            messageDiv.appendChild(contentDiv);
        }
        contentDiv.innerHTML = renderMarkdown(content);
    } else {
        messageDiv.textContent = content;
    }
}

async function loadConversationHistory(pdfId) {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/${pdfId}/conversations`);
        const conversations = await response.json();

        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.innerHTML = `
            <div class="system-message">
                👋 你好！我是AI助手，可以帮你理解文档内容。
                <br><br>
                <strong>功能：</strong><br>
                • 选中文字后右键可以解释、翻译或总结<br>
                • 直接提问关于文档的任何问题<br>
                • 生成整篇文档的摘要
            </div>
        `;

        if (conversations.length > 0) {
            const latestConv = conversations[0];
            currentConversationId = latestConv.conversation_id;

            latestConv.messages.forEach(msg => {
                addMessage(msg.role, msg.content);
            });
        }
    } catch (error) {
        console.error('Failed to load conversation history:', error);
    }
}

function handleEnter(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// ========== 文本选择功能 ==========

function handleTextSelection(event) {
    const selection = window.getSelection();
    const text = selection.toString().trim();

    if (text.length > 0 && currentPDF) {
        selectedText = text;
        showContextMenu(event.pageX, event.pageY, text);
    } else {
        hideContextMenu();
    }
}

function showContextMenu(x, y, text) {
    const menu = document.getElementById('context-menu');
    const preview = document.getElementById('selected-text-preview');

    // 显示选中文本预览（截断过长的文本）
    const maxPreviewLength = 100;
    if (text.length > maxPreviewLength) {
        preview.textContent = text.substring(0, maxPreviewLength) + '...';
    } else {
        preview.textContent = text;
    }

    // 计算菜单位置，确保不超出屏幕
    const menuWidth = 250;
    const menuHeight = 400;

    let posX = x;
    let posY = y;

    if (x + menuWidth > window.innerWidth) {
        posX = window.innerWidth - menuWidth - 10;
    }
    if (y + menuHeight > window.innerHeight) {
        posY = window.innerHeight - menuHeight - 10;
    }

    menu.style.display = 'block';
    menu.style.left = `${posX}px`;
    menu.style.top = `${posY}px`;
}

function hideContextMenu() {
    document.getElementById('context-menu').style.display = 'none';
}

async function explainText() {
    if (!selectedText || !currentPDF) return;
    hideContextMenu();

    addMessage('user', `请解释: "${selectedText}"`);
    const loadingMsg = addMessage('assistant', '正在分析...', false);

    try {
        const response = await fetch(`${API_BASE_URL}/chat/explain`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pdf_id: currentPDF.id,
                selected_text: selectedText,
                page_number: currentPage
            })
        });

        const result = await response.json();
        updateMessage(loadingMsg, result.explanation, true);
    } catch (error) {
        console.error('Explain failed:', error);
        updateMessage(loadingMsg, '❌ 解释失败，请重试', false);
    }
}

async function translateText() {
    if (!selectedText || !currentPDF) return;
    hideContextMenu();

    addMessage('user', `请翻译: "${selectedText}"`);
    const loadingMsg = addMessage('assistant', '正在翻译...', false);

    try {
        const response = await fetch(`${API_BASE_URL}/chat/translate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pdf_id: currentPDF.id,
                selected_text: selectedText,
                target_language: '中文'
            })
        });

        const result = await response.json();
        updateMessage(loadingMsg, result.translation, true);
    } catch (error) {
        console.error('Translation failed:', error);
        updateMessage(loadingMsg, '❌ 翻译失败，请重试', false);
    }
}

async function summarizeSelection() {
    if (!selectedText || !currentPDF) return;
    hideContextMenu();

    addMessage('user', `请总结: "${selectedText}"`);
    const loadingMsg = addMessage('assistant', '正在总结...', false);

    try {
        const response = await fetch(`${API_BASE_URL}/chat/summarize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pdf_id: currentPDF.id,
                selected_text: selectedText
            })
        });

        const result = await response.json();
        updateMessage(loadingMsg, result.summary, true);
    } catch (error) {
        console.error('Summarization failed:', error);
        updateMessage(loadingMsg, '❌ 总结失败，请重试', false);
    }
}

// 定义术语
async function defineTerms() {
    if (!selectedText || !currentPDF) return;
    hideContextMenu();

    addMessage('user', `请定义术语: "${selectedText}"`);
    const loadingMsg = addMessage('assistant', '正在查找定义...', false);

    try {
        const response = await fetch(`${API_BASE_URL}/chat/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pdf_id: currentPDF.id,
                message: `请详细定义以下术语或概念，包括：
1. 准确的定义
2. 在本文档上下文中的含义
3. 相关的概念或术语

术语: "${selectedText}"`,
                selected_text: selectedText,
                page_number: currentPage
            })
        });

        const result = await response.json();
        updateMessage(loadingMsg, result.response, true);
    } catch (error) {
        console.error('Define terms failed:', error);
        updateMessage(loadingMsg, '❌ 定义失败，请重试', false);
    }
}

// 举例说明
async function giveExamples() {
    if (!selectedText || !currentPDF) return;
    hideContextMenu();

    addMessage('user', `请举例说明: "${selectedText}"`);
    const loadingMsg = addMessage('assistant', '正在生成示例...', false);

    try {
        const response = await fetch(`${API_BASE_URL}/chat/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pdf_id: currentPDF.id,
                message: `请用具体的例子来说明以下内容，帮助我更好地理解：

"${selectedText}"

请提供：
1. 2-3个具体的例子
2. 每个例子的简要解释
3. 例子与原文的关联`,
                selected_text: selectedText,
                page_number: currentPage
            })
        });

        const result = await response.json();
        updateMessage(loadingMsg, result.response, true);
    } catch (error) {
        console.error('Give examples failed:', error);
        updateMessage(loadingMsg, '❌ 生成示例失败，请重试', false);
    }
}

// 生成问题
async function askQuestion() {
    if (!selectedText || !currentPDF) return;
    hideContextMenu();

    addMessage('user', `基于以下内容生成复习问题: "${selectedText}"`);
    const loadingMsg = addMessage('assistant', '正在生成问题...', false);

    try {
        const response = await fetch(`${API_BASE_URL}/chat/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pdf_id: currentPDF.id,
                message: `基于以下内容，生成3-5个复习问题，帮助我检验对这部分内容的理解：

"${selectedText}"

请生成：
1. 基础理解题（检验是否理解基本概念）
2. 应用题（检验是否能应用知识）
3. 分析题（检验是否能深入分析）

每个问题后面请提供简要的参考答案。`,
                selected_text: selectedText,
                page_number: currentPage
            })
        });

        const result = await response.json();
        updateMessage(loadingMsg, result.response, true);
    } catch (error) {
        console.error('Generate questions failed:', error);
        updateMessage(loadingMsg, '❌ 生成问题失败，请重试', false);
    }
}

// 添加到输入框
function addToInput() {
    if (!selectedText) return;
    hideContextMenu();

    const input = document.getElementById('chat-input');
    const currentValue = input.value.trim();

    if (currentValue) {
        input.value = currentValue + '\n\n' + `"${selectedText}"`;
    } else {
        input.value = `关于这段内容: "${selectedText}"\n\n我的问题是: `;
    }

    input.focus();
    // 将光标移到末尾
    input.setSelectionRange(input.value.length, input.value.length);
}

// 复制文本
function copyText() {
    if (!selectedText) return;
    hideContextMenu();

    navigator.clipboard.writeText(selectedText).then(() => {
        showToast('已复制到剪贴板');
    }).catch(err => {
        console.error('Copy failed:', err);
        showToast('复制失败');
    });
}

// Toast 提示
function showToast(message, duration = 2000) {
    // 移除已存在的 toast
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    // 显示动画
    setTimeout(() => toast.classList.add('show'), 10);

    // 自动隐藏
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ========== 摘要功能 ==========

async function generateSummary() {
    if (!currentPDF) return;

    showLoading('生成摘要中，这可能需要一些时间...');

    try {
        const response = await fetch(`${API_BASE_URL}/pdfs/${currentPDF.id}/summary`, {
            method: 'POST'
        });

        const result = await response.json();
        hideLoading();

        // 切换到摘要标签页
        switchTab('summary');

        // 显示摘要（使用Markdown渲染）
        const summaryContent = document.getElementById('summary-content');
        summaryContent.innerHTML = `<div class="markdown-content">${renderMarkdown(result.summary)}</div>`;

        showSuccess('摘要生成成功！');
    } catch (error) {
        hideLoading();
        console.error('Summary generation failed:', error);
        showError('生成摘要失败，请重试');
    }
}

// ========== 标签页切换 ==========

function switchTab(tabName) {
    // 移除所有active类
    document.querySelectorAll('.chat-tabs .tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // 添加active类
    event.target.classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// ========== 工具函数 ==========

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function showLoading(text = '处理中...') {
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function showSuccess(message) {
    // 可以实现一个toast通知
    console.log('Success:', message);
}

function showError(message) {
    // 可以实现一个toast通知
    console.error('Error:', message);
    alert(message);
}
