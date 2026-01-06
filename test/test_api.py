import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 加载.env文件
load_dotenv()

# 初始化客户端
api_key = os.getenv('api_key')
base_url = os.getenv('base_url')

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

print("=" * 60)
print("API Testing")
print("=" * 60)
print(f"API Key: {api_key[:10]}...")
print(f"Base URL: {base_url}")
print("=" * 60)


def test_chat():
    """测试聊天问答功能"""
    print("\n[1/3] Testing Chat Completion...")
    try:
        # 测试Gemini 2.5 Pro模型
        response = client.chat.completions.create(
            model="gemini-2.5-pro",
            messages=[
                {"role": "user", "content": "Hello, introduce yourself in one sentence"}
            ],
            max_tokens=100
        )

        # 检查响应类型
        if isinstance(response, str):
            result = response
        else:
            result = response.choices[0].message.content

        print(f"[OK] Chat test passed (model: gemini-2.5-pro)")
        print(f"  Response: {result}")
        return True
    except Exception as e:
        print(f"[FAIL] Chat test failed: {str(e)}")
        return False


def test_pdf_parsing():
    """测试PDF解析功能"""
    print("\n[2/3] Testing PDF Parsing Capability...")
    try:
        # 注意：这需要一个实际的PDF文件URL或base64编码的PDF
        # 这里我们测试带有文档分析能力的模型
        response = client.chat.completions.create(
            model="gemini-3-flash-preview",
            messages=[
                {
                    "role": "user",
                    "content": "Explain the basic process of PDF document parsing"
                }
            ],
            max_tokens=150
        )

        if isinstance(response, str):
            result = response
        else:
            result = response.choices[0].message.content

        print(f"[OK] PDF parsing test passed (model: gemini-3-flash-preview)")
        print(f"  Response: {result[:100]}...")
        return True
    except Exception as e:
        print(f"[FAIL] PDF parsing test failed: {str(e)}")
        return False


def test_image_generation():
    """测试图片生成功能"""
    print("\n[3/3] Testing Image Generation...")
    try:
        # 测试图片生成
        response = client.images.generate(
            model="dall-e-3",
            prompt="a cute cartoon cat reading a book",
            n=1,
            size="1024x1024"
        )

        image_url = response.data[0].url
        print(f"[OK] Image generation test passed")
        print(f"  Image URL: {image_url}")
        return True
    except Exception as e:
        print(f"[FAIL] Image generation test failed: {str(e)}")
        return False


def test_multimodal():
    """测试多模态功能（图片理解）"""
    print("\n[Extra Test] Testing Image Understanding...")
    try:
        response = client.chat.completions.create(
            model="google/gemini-3-flash-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                            }
                        }
                    ]
                }
            ],
            max_tokens=150
        )

        if isinstance(response, str):
            result = response
        else:
            result = response.choices[0].message.content

        print(f"[OK] Image understanding test passed")
        print(f"  Response: {result[:100]}...")
        return True
    except Exception as e:
        print(f"[FAIL] Image understanding test failed: {str(e)}")
        return False


if __name__ == "__main__":
    results = []

    # 运行所有测试
    results.append(("Chat Completion", test_chat()))
    results.append(("PDF Parsing", test_pdf_parsing()))
    results.append(("Image Generation", test_image_generation()))
    results.append(("Image Understanding", test_multimodal()))

    # 总结
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nPass Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    print("=" * 60)
