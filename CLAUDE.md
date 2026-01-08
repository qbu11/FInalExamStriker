# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

本项目在Windows11 开发，常用终端为CMD，故一切启动命令必须符合系统要求

## ⚠️ 重要：上下文管理规则

**在每次对话中，Claude 必须遵循以下规则：**

1. **监控上下文使用量** - 当感知到对话较长、已完成多个任务、或上下文窗口使用量可能超过 80% 时，主动执行以下操作：

2. **更新 Memory 文件** - 将当前会话的重要内容追加到 `memory/` 目录下的文件中：
   - 如果当天的文件已存在（如 `memory/session_YYYY-MM-DD.md`），则追加内容
   - 如果不存在，则创建新文件
   - 记录内容包括：完成的任务、修改的文件、遇到的问题和解决方案、待完成的工作

3. **提示用户重开对话** - 更新完 memory 后，告知用户：
   ```
   ⚠️ 上下文窗口使用量较高，建议重开新对话。

   已将本次对话内容保存到 memory/session_YYYY-MM-DD.md

   新对话开始时，请说："继续开发，请先阅读 memory 文件夹了解上下文"
   ```

4. **新对话开始时** - 如果用户提到"继续开发"或"阅读 memory"，应该：
   - 首先读取 `memory/` 目录下的最新文件
   - 了解项目当前状态和待完成的工作
   - 然后继续之前的工作

## Memory 文件格式

```markdown
# Final Exam Reviewer - 开发记录

## 会话日期: YYYY-MM-DD

### 完成的任务
- [ ] 任务1
- [ ] 任务2

### 修改的文件
- `path/to/file.py` - 修改说明

### 遇到的问题和解决方案
1. **问题**: 描述
   **解决**: 方案

### 待完成的工作
- [ ] 待办1
- [ ] 待办2

### 重要代码片段
（如有需要保留的关键代码）
```

---

## Project Overview

Final Exam Reviewer is an AI-powered PDF study assistant that helps students review and understand study materials. The application uses Gemini AI (via OpenAI-compatible proxy) to provide intelligent document analysis, chat functionality, and text operations.

**Architecture**: FastAPI backend + vanilla JavaScript frontend with SQLite database

## Common Commands

### Starting the Application

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Manual start (from project root):**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Development

**Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

**Run backend server:**
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

**Initialize database manually:**
```bash
cd backend
python -c "from app.database.models import init_db; init_db()"
```

**Access API documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing

```bash
# Test Gemini models functionality
python test/test_gemini_models.py

# Run API tests
python test/complete_api_test.py
```

## Architecture Overview

### Backend Structure (FastAPI)

**Core Services:**
- `GeminiService` (app/services/gemini_service.py): Handles all AI operations using Gemini API through OpenAI-compatible proxy. PDFs are sent as base64-encoded multimodal content.
- `PDFService` (app/services/pdf_service.py): Manages PDF upload, storage, and metadata extraction using PyPDF2.

**API Routes:**
- `pdf_routes.py`: PDF upload, list, delete, and summary generation
- `chat_routes.py`: AI chat, explain, translate, and summarize endpoints
- `annotation_routes.py`: Annotation management (WIP)

**Database (SQLAlchemy + SQLite):**
- `PDF`: Stores PDF metadata and file references
- `Conversation`: Groups messages by PDF
- `Message`: Individual chat messages with optional selected_text
- `Annotation`: Highlights and notes (not fully implemented)
- `PDFSummary`: Cached full document summaries

All models use cascade delete - removing a PDF deletes all associated conversations, messages, and summaries.

**Key Design Patterns:**
- Each Gemini API call sends the entire PDF as base64 in the request (multimodal content)
- Conversation history is limited to last 5 messages to manage token usage
- Database session management uses dependency injection via `get_db()`

### Frontend Structure (Vanilla JS)

- `index.html`: Single-page application with three-panel layout (PDF list, viewer, chat)
- `app.js`: Handles PDF.js rendering, API calls, and UI interactions
- `styles.css`: Responsive CSS styling
- Uses PDF.js CDN for client-side PDF rendering
- Context menu for text operations (explain, translate, summarize)

### Configuration

**Environment Variables (.env):**
```
api_key = <OpenAI-compatible API key>
base_url = <API base URL>
```

**Config Location:** `backend/app/config.py`
- Model: `google/gemini-3-flash-preview` (via OpenAI-compatible endpoint)
- Upload limit: 50MB
- Database: SQLite at `database/exam_reviewer.db`

### API Integration Flow

1. PDF Upload → PDFService saves file + extracts metadata → Database stores record
2. User asks question → chat_routes gets PDF path + conversation history → GeminiService encodes PDF to base64 + calls API → Response saved to database
3. Text selection → Frontend sends selected_text + page_number → GeminiService includes context in prompt → Specialized response (explain/translate/summarize)

### Important Implementation Details

**Gemini API Usage:**
- API endpoint: `{base_url}/v1/chat/completions`
- PDF sent in messages array as: `{"type": "image_url", "image_url": {"url": "data:application/pdf;base64,{pdf_base64}"}}`
- Every request re-encodes and sends the entire PDF (no caching at API level)
- Max tokens: 2000 (default), 3000 for full summaries

**Database Paths:**
- Upload directory: `backend/app/uploads/` (created via settings.UPLOAD_DIR)
- Database file: `backend/database/exam_reviewer.db`
- Both directories auto-created via `os.makedirs(exist_ok=True)`

**CORS Configuration:**
- Allows `localhost:3000` and `localhost:3001`
- Frontend typically opened via file:// protocol, so CORS may need adjustment for production

## File Structure Reference

```
backend/
├── main.py                      # FastAPI app entry point
├── app/
│   ├── config.py                # Settings and environment config
│   ├── database/
│   │   ├── models.py            # SQLAlchemy models and init_db()
│   │   └── __init__.py
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── routes/
│   │   ├── pdf_routes.py        # PDF CRUD + summary generation
│   │   ├── chat_routes.py       # Chat + text operations
│   │   └── annotation_routes.py # Annotations (partial)
│   └── services/
│       ├── gemini_service.py    # AI service (multimodal PDF+text)
│       └── pdf_service.py       # PDF file operations
├── uploads/                     # PDF storage (git-ignored)
└── database/                    # SQLite database (git-ignored)

frontend/
├── index.html                   # Main UI
├── app.js                       # Client-side logic
└── styles.css                   # Styling

test/                            # Various test scripts
```

## Development Notes

- The application stores PDFs locally and processes them via Gemini's multimodal API
- No OCR preprocessing - Gemini handles both text and scanned PDFs
- Conversation context limited to prevent token overflow
- Summary generation is cached per PDF to avoid redundant API calls
- Frontend has no build step - open index.html directly in browser
- Start script automatically installs dependencies and initializes database
