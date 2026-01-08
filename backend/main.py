from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database.models import init_db
from app.routes import pdf_routes, chat_routes, annotation_routes, formula_routes

# 初始化数据库
init_db()

# 创建FastAPI应用
app = FastAPI(
    title="Final Exam Reviewer API",
    description="AI-powered PDF review and study assistant",
    version="1.0.0"
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(pdf_routes.router, prefix="/api/pdfs", tags=["PDFs"])
app.include_router(chat_routes.router, prefix="/api/chat", tags=["Chat"])
app.include_router(formula_routes.router, prefix="/api/formula", tags=["Formula"])
app.include_router(annotation_routes.router, prefix="/api/annotations", tags=["Annotations"])

# 静态文件服务（用于上传的PDF）
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

@app.get("/")
async def root():
    return {
        "message": "Final Exam Reviewer API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
