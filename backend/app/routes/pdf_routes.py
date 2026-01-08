from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.database.models import PDF, get_db
from app.services.pdf_service import PDFService
from app.services.gemini_service import GeminiService
from app.models.schemas import PDFUploadResponse, PDFInfo, SummaryResponse
from datetime import datetime
import os

router = APIRouter()
pdf_service = PDFService()
gemini_service = GeminiService()

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传PDF文件"""
    try:
        # 保存文件
        file_info = await pdf_service.save_pdf(file)

        # 保存到数据库
        pdf_record = PDF(
            filename=file_info['filename'],
            original_filename=file_info['original_filename'],
            file_path=file_info['file_path'],
            file_size=file_info['file_size'],
            page_count=file_info['page_count'],
            is_scanned=file_info['is_scanned']
        )

        db.add(pdf_record)
        db.commit()
        db.refresh(pdf_record)

        return PDFUploadResponse(
            id=pdf_record.id,
            filename=pdf_record.filename,
            page_count=pdf_record.page_count,
            file_size=pdf_record.file_size,
            is_scanned=pdf_record.is_scanned,
            upload_date=pdf_record.upload_date
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[PDFInfo])
async def list_pdfs(db: Session = Depends(get_db)):
    """获取所有PDF列表"""
    pdfs = db.query(PDF).order_by(PDF.upload_date.desc()).all()
    return [
        PDFInfo(
            id=pdf.id,
            filename=pdf.filename,
            original_filename=pdf.original_filename,
            page_count=pdf.page_count,
            file_size=pdf.file_size,
            is_scanned=pdf.is_scanned,
            upload_date=pdf.upload_date,
            last_accessed=pdf.last_accessed
        )
        for pdf in pdfs
    ]

@router.get("/{pdf_id}", response_model=PDFInfo)
async def get_pdf(pdf_id: int, db: Session = Depends(get_db)):
    """获取单个PDF信息"""
    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    # 更新最后访问时间
    pdf.last_accessed = datetime.utcnow()
    db.commit()

    return PDFInfo(
        id=pdf.id,
        filename=pdf.filename,
        original_filename=pdf.original_filename,
        page_count=pdf.page_count,
        file_size=pdf.file_size,
        is_scanned=pdf.is_scanned,
        upload_date=pdf.upload_date,
        last_accessed=pdf.last_accessed
    )

@router.get("/{pdf_id}/file")
async def get_pdf_file(pdf_id: int, db: Session = Depends(get_db)):
    """获取PDF文件"""
    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    if not os.path.exists(pdf.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    # 更新最后访问时间
    pdf.last_accessed = datetime.utcnow()
    db.commit()

    return FileResponse(
        path=pdf.file_path,
        media_type="application/pdf",
        filename=pdf.original_filename,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.delete("/{pdf_id}")
async def delete_pdf(pdf_id: int, db: Session = Depends(get_db)):
    """删除PDF文件"""
    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    # 删除物理文件
    pdf_service.delete_pdf(pdf.file_path)

    # 删除数据库记录（级联删除相关数据）
    db.delete(pdf)
    db.commit()

    return {"message": "PDF deleted successfully"}

@router.post("/{pdf_id}/summary", response_model=SummaryResponse)
async def generate_summary(pdf_id: int, db: Session = Depends(get_db)):
    """生成PDF完整摘要"""
    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    try:
        # 检查是否已有摘要
        if pdf.summary:
            return SummaryResponse(
                pdf_id=pdf_id,
                summary=pdf.summary.summary_text,
                generated_at=pdf.summary.generated_at
            )

        # 生成摘要
        from app.database.models import PDFSummary
        summary_text = gemini_service.generate_full_summary(pdf.file_path)

        # 保存摘要
        summary = PDFSummary(
            pdf_id=pdf_id,
            summary_text=summary_text
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)

        return SummaryResponse(
            pdf_id=pdf_id,
            summary=summary_text,
            generated_at=summary.generated_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@router.get("/{pdf_id}/summary", response_model=SummaryResponse)
async def get_summary(pdf_id: int, db: Session = Depends(get_db)):
    """获取PDF摘要"""
    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    if not pdf.summary:
        raise HTTPException(status_code=404, detail="Summary not generated yet")

    return SummaryResponse(
        pdf_id=pdf_id,
        summary=pdf.summary.summary_text,
        generated_at=pdf.summary.generated_at
    )

@router.get("/{pdf_id}/file")
async def get_pdf_file(pdf_id: int, db: Session = Depends(get_db)):
    """获取PDF文件"""
    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    if not os.path.exists(pdf.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        pdf.file_path,
        media_type='application/pdf',
        filename=pdf.original_filename
    )
