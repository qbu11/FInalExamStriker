from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PDFUploadResponse(BaseModel):
    id: int
    filename: str
    page_count: int
    file_size: int
    is_scanned: bool
    upload_date: datetime

class PDFInfo(BaseModel):
    id: int
    filename: str
    original_filename: str
    page_count: int
    file_size: int
    is_scanned: bool
    upload_date: datetime
    last_accessed: datetime

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    selected_text: Optional[str] = None
    page_number: Optional[int] = None
    action_type: Optional[str] = None

class ChatRequest(BaseModel):
    pdf_id: int
    message: str
    selected_text: Optional[str] = None
    page_number: Optional[int] = None
    coordinates: Optional[dict] = None

class ChatResponse(BaseModel):
    message_id: int
    response: str
    conversation_id: int

class ExplainRequest(BaseModel):
    pdf_id: int
    selected_text: str
    page_number: int
    custom_prompt: Optional[str] = None

class SummaryRequest(BaseModel):
    pdf_id: int

class SummaryResponse(BaseModel):
    pdf_id: int
    summary: str
    generated_at: datetime

class Annotation(BaseModel):
    id: Optional[int] = None
    pdf_id: int
    page_number: int
    type: str  # 'highlight' or 'note'
    text_content: Optional[str] = None
    coordinates: dict
    color: Optional[str] = "#FFFF00"
    note_text: Optional[str] = None
    created_at: Optional[datetime] = None

class ConversationHistory(BaseModel):
    conversation_id: int
    pdf_id: int
    title: Optional[str] = None
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
