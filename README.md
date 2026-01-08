# 🎓 Final Exam Reviewer - AI复习助手

一个基于AI的智能PDF学习助手，帮助学生更高效地复习和理解学习资料。
本项目在windows11开发，主要命令终端cmd，所生成的一切命令必须服务于这条规则
## ✨ 主要功能

### 📄 PDF文档管理
- 上传和管理多个PDF文档
- 自动识别文档页数和大小
- 检测是否为扫描版PDF

### 💬 智能对话
- 与AI助手对话，提问关于文档的任何问题
- 保存完整的对话历史
- 支持上下文理解，记忆之前的对话

### 🔍 文本分析
- **解释功能**: 选中文字即可获得详细解释
- **翻译功能**: 支持多语言翻译
- **总结功能**: 快速总结长段文字的要点

### 📝 文档摘要
- 一键生成整篇PDF的完整摘要
- 提取文档核心内容和关键要点
- 保存摘要供后续查看

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 现代浏览器（Chrome、Firefox、Edge等）

### 常用命令

#### 启动后端服务

打开 CMD，执行：

```
cd E:\11Projects\FInalExamReviewer\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 关闭后端服务

方法1：在运行服务的 CMD 窗口按 Ctrl+C

方法2：新开 CMD 窗口执行：

```
taskkill /F /IM python.exe
```

#### 访问地址

- 前端页面：直接用浏览器打开 frontend/index.html
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd FInalExamReviewer
```

2. **配置API密钥**

项目根目录已有 `.env` 文件，包含API配置：
```
api_key = sk-VaTwaN5KdWDPMAIcNW6U3byvwS81CtmFnNh8rtim3xsaOaVs
base_url = https://openai-proxy.miracleplus.com
```

3. **启动应用**

**Windows用户：**
```bash
start.bat
```

**Linux/Mac用户：**
```bash
chmod +x start.sh
./start.sh
```

4. **打开前端界面**

在浏览器中打开 `frontend/index.html` 文件

## 📁 项目结构

```
FInalExamReviewer/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── config.py          # 配置文件
│   │   ├── database/          # 数据库模型
│   │   ├── models/            # Pydantic模型
│   │   ├── routes/            # API路由
│   │   │   ├── pdf_routes.py
│   │   │   ├── chat_routes.py
│   │   │   └── annotation_routes.py
│   │   ├── services/          # 业务逻辑
│   │   │   ├── gemini_service.py
│   │   │   └── pdf_service.py
│   │   └── utils/
│   ├── main.py                # FastAPI主程序
│   └── requirements.txt       # Python依赖
├── frontend/                   # 前端代码
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── database/                   # SQLite数据库
├── uploads/                    # 上传的PDF文件
├── test/                       # 测试文件和报告
├── .env                        # 环境变量
└── README.md
```

## 🔧 技术栈

### 后端
- **FastAPI**: 高性能Web框架
- **SQLAlchemy**: ORM数据库操作
- **SQLite**: 轻量级数据库
- **PyPDF2**: PDF文件处理
- **Gemini AI**: Google的多模态AI模型

### 前端
- **原生JavaScript**: 无框架依赖
- **PDF.js**: PDF渲染引擎
- **纯CSS**: 响应式设计

## 📖 API文档

启动服务器后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API端点

#### PDF管理
- `POST /api/pdfs/upload` - 上传PDF
- `GET /api/pdfs/` - 获取PDF列表
- `GET /api/pdfs/{pdf_id}` - 获取PDF详情
- `DELETE /api/pdfs/{pdf_id}` - 删除PDF
- `POST /api/pdfs/{pdf_id}/summary` - 生成摘要

#### AI对话
- `POST /api/chat/send` - 发送消息
- `POST /api/chat/explain` - 解释文本
- `POST /api/chat/translate` - 翻译文本
- `POST /api/chat/summarize` - 总结文本
- `GET /api/chat/{pdf_id}/conversations` - 获取对话历史

#### 注释管理
- `POST /api/annotations/` - 创建注释
- `GET /api/annotations/{pdf_id}` - 获取注释列表
- `PUT /api/annotations/{annotation_id}` - 更新注释
- `DELETE /api/annotations/{annotation_id}` - 删除注释

## 🎯 使用指南

### 1. 上传PDF文档
- 点击左侧"上传PDF"按钮
- 选择PDF文件（最大50MB）
- 等待上传完成

### 2. 查看和阅读
- 点击左侧文档列表中的文档
- 使用"上一页"/"下一页"按钮浏览
- 支持鼠标滚轮缩放

### 3. 与AI对话
- 在右侧聊天框输入问题
- 按回车或点击"发送"
- AI会基于PDF内容回答

### 4. 文本操作
- 选中文档中的任意文字
- 右键菜单选择操作：
  - 💡 解释这段文字
  - 🌐 翻译
  - 📋 总结要点

### 5. 生成摘要
- 点击顶部"生成摘要"按钮
- 切换到"摘要"标签页查看
- 摘要会自动保存

## 🧪 测试

项目包含完整的API测试：

```bash
# Gemini模型功能测试
python test/test_gemini_models.py

# API功能测试
python test/complete_api_test.py
```

测试报告：
- `test/GEMINI_TEST_REPORT.md` - Gemini模型测试（✅ 100%通过）
- `test/API_TEST_REPORT.md` - API功能测试

## 📊 功能状态

| 功能 | 状态 | 说明 |
|------|------|------|
| PDF上传 | ✅ | 支持50MB以内PDF |
| PDF查看 | ✅ | 基于PDF.js |
| AI对话 | ✅ | Gemini 3 Flash Preview |
| 文本解释 | ✅ | 理解选中内容 |
| 文本翻译 | ✅ | 多语言支持 |
| 文本总结 | ✅ | 提取关键要点 |
| 文档摘要 | ✅ | 完整文档分析 |
| 对话历史 | ✅ | 自动保存 |
| 笔记注释 | 🚧 | 开发中 |

## 🔐 隐私和安全

- 所有文档存储在本地
- 数据不会上传到第三方服务器
- API密钥应妥善保管
- 建议不要上传敏感文档

## 🐛 常见问题

### 1. 上传失败
- 检查文件大小是否超过50MB
- 确保文件是有效的PDF格式
- 检查磁盘空间是否充足

### 2. AI回复缓慢
- Gemini处理大型PDF需要时间
- 网络连接可能影响速度
- 可以尝试较小的文档

### 3. PDF无法显示
- 确保浏览器支持PDF.js
- 检查PDF文件是否损坏
- 尝试刷新页面

### 4. 跨域错误
- 确保后端服务正在运行
- 检查CORS配置
- 使用支持file://协议的浏览器

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [PDF.js](https://mozilla.github.io/pdf.js/) - PDF渲染
- [Google Gemini](https://ai.google.dev/) - AI模型
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM框架

## 📞 联系方式

如有问题或建议，请提交Issue。

---

**Happy Studying! 📚✨**
