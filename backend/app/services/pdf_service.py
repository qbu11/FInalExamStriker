import os
import PyPDF2
from typing import Optional
from fastapi import UploadFile, HTTPException
from app.config import settings
import uuid

class PDFService:
    """PDF处理服务"""

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_pdf(self, file: UploadFile) -> dict:
        """
        保存上传的PDF文件

        Args:
            file: 上传的文件

        Returns:
            文件信息字典
        """
        # 验证文件类型
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持PDF文件")

        # 验证文件大小
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="文件过大（最大50MB）")

        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.pdf"
        file_path = os.path.join(self.upload_dir, filename)

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(content)

        # 提取PDF元数据
        metadata = self._extract_pdf_metadata(file_path)

        return {
            "id": file_id,
            "filename": filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "file_size": len(content),
            **metadata
        }

    def _extract_pdf_metadata(self, file_path: str) -> dict:
        """
        提取PDF元数据

        Args:
            file_path: PDF文件路径

        Returns:
            元数据字典
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)

                # 尝试提取文本以判断是否为扫描版PDF
                total_text = ""
                for page in pdf_reader.pages[:3]:  # 只检查前3页
                    text = page.extract_text()
                    total_text += text

                # 如果前3页的文本总长度很少，可能是扫描版PDF
                is_scanned = len(total_text.strip()) < 100

                return {
                    "page_count": page_count,
                    "is_scanned": is_scanned
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF解析失败: {str(e)}")

    def delete_pdf(self, file_path: str) -> bool:
        """
        删除PDF文件

        Args:
            file_path: 文件路径

        Returns:
            是否删除成功
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
            return False

    def get_pdf_path(self, filename: str) -> str:
        """
        获取PDF文件的完整路径

        Args:
            filename: 文件名

        Returns:
            完整路径
        """
        return os.path.join(self.upload_dir, filename)
