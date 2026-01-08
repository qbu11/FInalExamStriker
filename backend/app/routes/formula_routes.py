from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.models import PDF, get_db
from app.services.gemini_service import GeminiService

router = APIRouter()
gemini_service = GeminiService()


@router.post("/explain")
async def explain_formula(request: dict, db: Session = Depends(get_db)):
    """解释公式 - 支持文本或图片输入"""
    pdf_id = request.get("pdf_id")
    selected_text = request.get("selected_text")
    image_base64 = request.get("image_base64")
    page_number = request.get("page_number")

    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    try:
        explanation = gemini_service.explain_formula(
            pdf_path=pdf.file_path,
            selected_text=selected_text,
            image_base64=image_base64,
            page_num=page_number
        )

        return {"explanation": explanation}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Formula explanation failed: {str(e)}")
