from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.models import PDF, Annotation as AnnotationModel, get_db
from app.models.schemas import Annotation
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=Annotation)
async def create_annotation(annotation: Annotation, db: Session = Depends(get_db)):
    """创建新注释"""
    # 验证PDF存在
    pdf = db.query(PDF).filter(PDF.id == annotation.pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    try:
        db_annotation = AnnotationModel(
            pdf_id=annotation.pdf_id,
            page_number=annotation.page_number,
            type=annotation.type,
            text_content=annotation.text_content,
            coordinates=annotation.coordinates,
            color=annotation.color,
            note_text=annotation.note_text
        )

        db.add(db_annotation)
        db.commit()
        db.refresh(db_annotation)

        return Annotation(
            id=db_annotation.id,
            pdf_id=db_annotation.pdf_id,
            page_number=db_annotation.page_number,
            type=db_annotation.type,
            text_content=db_annotation.text_content,
            coordinates=db_annotation.coordinates,
            color=db_annotation.color,
            note_text=db_annotation.note_text,
            created_at=db_annotation.created_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create annotation: {str(e)}")

@router.get("/{pdf_id}", response_model=List[Annotation])
async def get_annotations(pdf_id: int, db: Session = Depends(get_db)):
    """获取PDF的所有注释"""
    annotations = db.query(AnnotationModel).filter(
        AnnotationModel.pdf_id == pdf_id
    ).order_by(AnnotationModel.page_number, AnnotationModel.created_at).all()

    return [
        Annotation(
            id=ann.id,
            pdf_id=ann.pdf_id,
            page_number=ann.page_number,
            type=ann.type,
            text_content=ann.text_content,
            coordinates=ann.coordinates,
            color=ann.color,
            note_text=ann.note_text,
            created_at=ann.created_at
        )
        for ann in annotations
    ]

@router.put("/{annotation_id}", response_model=Annotation)
async def update_annotation(
    annotation_id: int,
    annotation: Annotation,
    db: Session = Depends(get_db)
):
    """更新注释"""
    db_annotation = db.query(AnnotationModel).filter(
        AnnotationModel.id == annotation_id
    ).first()

    if not db_annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    try:
        # 更新字段
        if annotation.text_content is not None:
            db_annotation.text_content = annotation.text_content
        if annotation.coordinates is not None:
            db_annotation.coordinates = annotation.coordinates
        if annotation.color is not None:
            db_annotation.color = annotation.color
        if annotation.note_text is not None:
            db_annotation.note_text = annotation.note_text

        db_annotation.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_annotation)

        return Annotation(
            id=db_annotation.id,
            pdf_id=db_annotation.pdf_id,
            page_number=db_annotation.page_number,
            type=db_annotation.type,
            text_content=db_annotation.text_content,
            coordinates=db_annotation.coordinates,
            color=db_annotation.color,
            note_text=db_annotation.note_text,
            created_at=db_annotation.created_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update annotation: {str(e)}")

@router.delete("/{annotation_id}")
async def delete_annotation(annotation_id: int, db: Session = Depends(get_db)):
    """删除注释"""
    annotation = db.query(AnnotationModel).filter(
        AnnotationModel.id == annotation_id
    ).first()

    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    db.delete(annotation)
    db.commit()

    return {"message": "Annotation deleted successfully"}
