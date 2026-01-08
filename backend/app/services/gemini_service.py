import base64
import requests
import os
from typing import List, Optional
from app.config import settings

class GeminiService:
    """Gemini AI服务 - 处理PDF读取和AI对话"""

    def __init__(self):
        self.api_key = settings.API_KEY
        self.base_url = settings.BASE_URL
        self.model = settings.GEMINI_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _pdf_to_base64(self, pdf_path: str) -> str:
        """将PDF文件转换为base64编码"""
        with open(pdf_path, "rb") as pdf_file:
            pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        return pdf_base64

    def _call_gemini_api(self, messages: List[dict], max_tokens: int = 2000) -> str:
        """调用Gemini API"""
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens
                },
                headers=self.headers,
                timeout=60
            )

            response.raise_for_status()
            data = response.json()

            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            else:
                raise ValueError("Invalid response format from API")

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def read_pdf_with_context(self, pdf_path: str, prompt: str, max_tokens: int = 2000) -> str:
        """
        使用Gemini读取PDF并回答问题

        Args:
            pdf_path: PDF文件路径
            prompt: 用户问题或提示
            max_tokens: 最大token数

        Returns:
            AI的回复
        """
        pdf_base64 = self._pdf_to_base64(pdf_path)

        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:application/pdf;base64,{pdf_base64}"
                    }
                }
            ]
        }]

        return self._call_gemini_api(messages, max_tokens)

    def explain_selected_text(
        self,
        pdf_path: str,
        selected_text: str,
        page_num: int,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        解释用户选中的文本

        Args:
            pdf_path: PDF文件路径
            selected_text: 选中的文本
            page_num: 页码
            custom_prompt: 用户自定义提示（可选）

        Returns:
            AI的解释
        """
        if custom_prompt:
            prompt = custom_prompt.replace("{selected_text}", selected_text)
        else:
            prompt = f"""用户从第{page_num}页选择了以下文本:

"{selected_text}"

请详细解释这段文字的内容，包括：
1. 字面意思是什么？
2. 背后的概念或原理是什么？
3. 有哪些关键要点？
4. 需要注意什么？

请用中文回答，简洁明了。"""

        return self.read_pdf_with_context(pdf_path, prompt)

    def translate_text(
        self,
        pdf_path: str,
        selected_text: str,
        target_language: str = "中文"
    ) -> str:
        """
        翻译选中的文本

        Args:
            pdf_path: PDF文件路径
            selected_text: 选中的文本
            target_language: 目标语言

        Returns:
            翻译结果
        """
        prompt = f"""请将以下文本翻译成{target_language}：

"{selected_text}"

只返回翻译结果，不要额外解释。"""

        return self.read_pdf_with_context(pdf_path, prompt)

    def summarize_text(
        self,
        pdf_path: str,
        selected_text: str
    ) -> str:
        """
        总结选中的文本

        Args:
            pdf_path: PDF文件路径
            selected_text: 选中的文本

        Returns:
            总结内容
        """
        prompt = f"""请用中文总结以下文本的核心要点：

"{selected_text}"

请简洁地列出3-5个要点。"""

        return self.read_pdf_with_context(pdf_path, prompt)

    def generate_full_summary(self, pdf_path: str) -> str:
        """
        生成整篇PDF的摘要

        Args:
            pdf_path: PDF文件路径

        Returns:
            完整摘要
        """
        prompt = """请仔细分析这个PDF文档并提供：

1. **文档概述**（2-3段）：这份文档的主要内容是什么？讨论了什么主题？

2. **核心内容**（3-5个要点）：文档中最重要的概念、公式、定义或结论是什么？

3. **关键细节**：有哪些重要的细节、例子或说明？

4. **总结建议**：读者应该重点关注什么？

请用中文回答，结构清晰，内容详实。"""

        return self.read_pdf_with_context(pdf_path, prompt, max_tokens=3000)

    def chat_with_pdf(
        self,
        pdf_path: str,
        user_message: str,
        conversation_history: Optional[List[dict]] = None,
        selected_text: Optional[str] = None
    ) -> str:
        """
        与PDF对话

        Args:
            pdf_path: PDF文件路径
            user_message: 用户消息
            conversation_history: 对话历史（最近几轮）
            selected_text: 选中的文本（可选）

        Returns:
            AI回复
        """
        # 构建上下文
        context_parts = []

        if conversation_history:
            # 只保留最近5条消息作为上下文
            recent_history = conversation_history[-5:]
            history_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in recent_history
            ])
            context_parts.append(f"之前的对话:\n{history_text}")

        if selected_text:
            context_parts.append(f"用户选中的文本:\n\"{selected_text}\"")

        if context_parts:
            full_prompt = f"""{chr(10).join(context_parts)}

用户的问题: {user_message}

请基于PDF文档内容回答用户的问题。"""
        else:
            full_prompt = user_message

        return self.read_pdf_with_context(pdf_path, full_prompt)

    def analyze_pdf_structure(self, pdf_path: str) -> dict:
        """
        分析PDF结构（使用Gemini识别章节、标题等）

        Args:
            pdf_path: PDF文件路径

        Returns:
            PDF结构信息
        """
        prompt = """请分析这个PDF文档的结构，返回：
1. 文档标题
2. 主要章节（包括页码范围，如果可能的话）
3. 章节层级关系
4. 是否有图表、公式等特殊内容

请用JSON格式返回结果。"""

        response = self.read_pdf_with_context(pdf_path, prompt)
        # 这里可以尝试解析JSON，如果失败则返回原始文本
        return {"raw_analysis": response}
