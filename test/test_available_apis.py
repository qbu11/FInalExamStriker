import os
import sys
import requests
from openai import OpenAI
from dotenv import load_dotenv

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 加载.env文件
load_dotenv()

# 获取配置
api_key = os.getenv('api_key')
base_url = os.getenv('base_url')

# 初始化客户端
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

print("=" * 70)
print("API Functionality Test (Using Available Models)")
print("=" * 70)

# 首先获取可用的模型列表
print("\n[Step 1] Fetching available models...")
try:
    models = client.models.list()
    model_ids = [model.id for model in models.data]
    print(f"Total available models: {len(model_ids)}")

    # 过滤出Gemini模型
    gemini_models = [m for m in model_ids if 'gemini' in m.lower()]
    claude_models = [m for m in model_ids if 'claude' in m.lower()]
    gpt_models = [m for m in model_ids if 'gpt' in m.lower()]
    dalle_models = [m for m in model_ids if 'dall' in m.lower()]

    print(f"\nGemini models ({len(gemini_models)}): {gemini_models[:5]}")
    print(f"Claude models ({len(claude_models)}): {claude_models[:5]}")
    print(f"GPT models ({len(gpt_models)}): {gpt_models[:5]}")
    print(f"DALL-E models ({len(dalle_models)}): {dalle_models}")

except Exception as e:
    print(f"[ERROR] Failed to fetch models: {str(e)}")
    gemini_models = []
    claude_models = []
    gpt_models = []
    dalle_models = []

# 测试1: 聊天问答（使用Claude模型）
print("\n" + "=" * 70)
print("[Test 1/4] Chat Completion Test")
print("=" * 70)

test_models = []
if claude_models:
    test_models.append(("Claude", claude_models[0]))
if gpt_models:
    test_models.append(("GPT", gpt_models[0]))
if gemini_models:
    # 尝试找一个不是preview的稳定版本
    stable_gemini = [m for m in gemini_models if 'preview' not in m.lower()]
    if stable_gemini:
        test_models.append(("Gemini", stable_gemini[0]))

for model_name, model_id in test_models:
    print(f"\nTesting {model_name} ({model_id})...")
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "user", "content": "Say 'Hello! I am working.' in one sentence."}
            ],
            max_tokens=50
        )

        result = response.choices[0].message.content
        print(f"[SUCCESS] {model_name} chat is working!")
        print(f"Response: {result}")
        break  # 成功后就不继续测试其他模型了
    except Exception as e:
        print(f"[FAIL] {model_name} failed: {str(e)[:100]}")

# 测试2: PDF文档处理能力（使用Vision模型）
print("\n" + "=" * 70)
print("[Test 2/4] Document/PDF Processing Capability Test")
print("=" * 70)

vision_models = [m for m in model_ids if any(x in m.lower() for x in ['vision', 'claude-3', 'gpt-4', 'gemini'])]

if vision_models:
    test_model = vision_models[0]
    print(f"\nTesting with model: {test_model}")
    try:
        response = client.chat.completions.create(
            model=test_model,
            messages=[
                {
                    "role": "user",
                    "content": "Explain in 2 sentences how to extract text from a PDF document programmatically."
                }
            ],
            max_tokens=150
        )

        result = response.choices[0].message.content
        print(f"[SUCCESS] Document processing capability is available!")
        print(f"Response: {result}")
    except Exception as e:
        print(f"[FAIL] Test failed: {str(e)[:200]}")
else:
    print("[SKIP] No suitable models found for document processing")

# 测试3: 图片生成
print("\n" + "=" * 70)
print("[Test 3/4] Image Generation Test")
print("=" * 70)

if dalle_models:
    test_model = dalle_models[0]
    print(f"\nTesting with model: {test_model}")
    try:
        response = client.images.generate(
            model=test_model,
            prompt="a simple red circle",
            n=1,
            size="1024x1024"
        )

        image_url = response.data[0].url
        print(f"[SUCCESS] Image generation is working!")
        print(f"Image URL: {image_url}")
    except Exception as e:
        print(f"[FAIL] Test failed: {str(e)[:200]}")
else:
    print("[INFO] No DALL-E models available in the model list")
    print("Trying direct request with dall-e-3...")
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt="a simple red circle",
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        print(f"[SUCCESS] Image generation is working!")
        print(f"Image URL: {image_url}")
    except Exception as e:
        print(f"[FAIL] Image generation not available: {str(e)[:200]}")

# 测试4: 图片理解（Vision）
print("\n" + "=" * 70)
print("[Test 4/4] Image Understanding (Vision) Test")
print("=" * 70)

vision_capable = [m for m in model_ids if any(x in m.lower() for x in ['vision', 'claude-3', 'gpt-4-turbo', 'gpt-4o', 'gemini-1.5', 'gemini-2'])]

if vision_capable:
    test_model = vision_capable[0]
    print(f"\nTesting with model: {test_model}")
    try:
        response = client.chat.completions.create(
            model=test_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What do you see in this image? Answer in one sentence."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/1200px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                            }
                        }
                    ]
                }
            ],
            max_tokens=100
        )

        result = response.choices[0].message.content
        print(f"[SUCCESS] Image understanding is working!")
        print(f"Response: {result}")
    except Exception as e:
        print(f"[FAIL] Test failed: {str(e)[:200]}")
else:
    print("[SKIP] No vision-capable models found")

# 总结
print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print("\nAvailable capabilities on this API endpoint:")
print(f"  - Chat/Text Completion: {'✓' if claude_models or gpt_models else '✗'}")
print(f"  - Document Processing: {'✓' if vision_models else '✗'}")
print(f"  - Image Generation: {'?' if dalle_models else 'Possibly not available'}")
print(f"  - Image Understanding: {'✓' if vision_capable else '✗'}")

print("\nRecommended models for your use:")
if claude_models:
    print(f"  - Chat: {claude_models[0]}")
if vision_capable:
    print(f"  - Vision/PDF: {vision_capable[0]}")
if dalle_models:
    print(f"  - Image Gen: {dalle_models[0]}")

print("=" * 70)
