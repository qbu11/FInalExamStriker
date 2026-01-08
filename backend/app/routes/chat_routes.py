from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.models import PDF, Conversation, Message, get_db
from app.services.gemini_service import GeminiService
from app.models.schemas import (
    ChatRequest, ChatResponse, ExplainRequest,
    ChatMessage, ConversationHistory
)
from datetime import datetime

router = APIRouter()
gemini_service = GeminiService()

@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """发送消息并获取AI回复"""
    # 验证PDF存在
    pdf = db.query(PDF).filter(PDF.id == request.pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    try:
        # 查找或创建对话
        conversation = db.query(Conversation).filter(
            Conversation.pdf_id == request.pdf_id
        ).order_by(Conversation.updated_at.desc()).first()

        if not conversation:
            conversation = Conversation(
                pdf_id=request.pdf_id,
                title=f"Conversation with {pdf.original_filename}"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # 获取对话历史
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.asc()).all()

        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages[-5:]  # 只取最近5条
        ]

        # 保存用户消息
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            selected_text=request.selected_text,
            page_number=request.page_number,
            coordinates=request.coordinates
        )
        db.add(user_message)

        # 调用AI获取回复
        ai_response = gemini_service.chat_with_pdf(
            pdf_path=pdf.file_path,
            user_message=request.message,
            conversation_history=conversation_history,
            selected_text=request.selected_text
        )

        # 保存AI回复
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response
        )
        db.add(assistant_message)

        # 更新对话时间
        conversation.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(assistant_message)

        return ChatResponse(
            message_id=assistant_message.id,
            response=ai_response,
            conversation_id=conversation.id
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.post("/explain")
async def explain_text(request: ExplainRequest, db: Session = Depends(get_db)):
    """解释选中的文本"""
    pdf = db.query(PDF).filter(PDF.id == request.pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    try:
        explanation = gemini_service.explain_selected_text(
            pdf_path=pdf.file_path,
            selected_text=request.selected_text,
            page_num=request.page_number,
            custom_prompt=request.custom_prompt
        )

        return {"explanation": explanation}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

@router.post("/translate")
async def translate_text(request: dict, db: Session = Depends(get_db)):
    """翻译选中的文本"""
    pdf_id = request.get("pdf_id")
    selected_text = request.get("selected_text")
    target_language = request.get("target_language", "中文")

    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    try:
        translation = gemini_service.translate_text(
            pdf_path=pdf.file_path,
            selected_text=selected_text,
            target_language=target_language
        )

        return {"translation": translation}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/summarize")
async def summarize_text(request: dict, db: Session = Depends(get_db)):
    """总结选中的文本"""
    pdf_id = request.get("pdf_id")
    selected_text = request.get("selected_text")

    pdf = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    try:
        summary = gemini_service.summarize_text(
            pdf_path=pdf.file_path,
            selected_text=selected_text
        )

        return {"summary": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.post("/explain-formula")
async def explain_formula(request: dict, db: Session = Depends(get_db)):
    """解释公式 - 支持文本或图片输入"""
    pdf_id = request.get("pdf_id")
    selected_text = request.get("selected_text")  # 框选的文本（可能包含公式）
    image_base64 = request.get("image_base64")    # 截图的 base64 数据
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


@router.get("/{pdf_id}/conversations", response_model=List[ConversationHistory])
async def get_conversations(pdf_id: int, db: Session = Depends(get_db)):
    """获取PDF的所有对话历史"""
    conversations = db.query(Conversation).filter(
        Conversation.pdf_id == pdf_id
    ).order_by(Conversation.updated_at.desc()).all()

    result = []
    for conv in conversations:
        messages = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.created_at.asc()).all()

        result.append(ConversationHistory(
            conversation_id=conv.id,
            pdf_id=conv.pdf_id,
            title=conv.title,
            messages=[
                ChatMessage(
                    role=msg.role,
                    content=msg.content,
                    selected_text=msg.selected_text,
                    page_number=msg.page_number,
                    action_type=msg.action_type
                )
                for msg in messages
            ],
            created_at=conv.created_at,
            updated_at=conv.updated_at
        ))

    return result

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """删除对话"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.delete(conversation)
    db.commit()

    return {"message": "Conversation deleted successfully"}
