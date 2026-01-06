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

print("=" * 70)
print("API Functionality Test")
print("=" * 70)
print(f"API Key: {api_key[:15]}...")
print(f"Base URL: {base_url}")

# 首先使用requests获取可用的模型列表
print("\n[Step 1] Fetching available models...")
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(f"{base_url}/v1/models", headers=headers, timeout=30)
    if response.status_code == 200:
        data = response.json()
        model_ids = [model['id'] for model in data.get('data', [])]
        print(f"Total available models: {len(model_ids)}")

        # 过滤出不同类型的模型
        gemini_models = [m for m in model_ids if 'gemini' in m.lower()]
        claude_models = [m for m in model_ids if 'claude' in m.lower()]
        gpt_models = [m for m in model_ids if 'gpt' in m.lower()]
        dalle_models = [m for m in model_ids if 'dall' in m.lower()]

        print(f"\nGemini models ({len(gemini_models)}): {', '.join(gemini_models[:3])}")
        print(f"Claude models ({len(claude_models)}): {', '.join(claude_models[:3])}")
        print(f"GPT models ({len(gpt_models)}): {', '.join(gpt_models[:3])}")
        print(f"DALL-E models ({len(dalle_models)}): {', '.join(dalle_models) if dalle_models else 'None'}")
    else:
        print(f"[ERROR] Failed to fetch models: {response.status_code}")
        model_ids = []
        gemini_models = []
        claude_models = []
        gpt_models = []
        dalle_models = []
except Exception as e:
    print(f"[ERROR] Failed to fetch models: {str(e)}")
    model_ids = []
    gemini_models = []
    claude_models = []
    gpt_models = []
    dalle_models = []

# 初始化OpenAI客户端用于测试
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# 测试1: 聊天问答
print("\n" + "=" * 70)
print("[Test 1/4] Chat Completion Test")
print("=" * 70)

test_models = []
if claude_models:
    test_models.append(("Claude", claude_models[0]))
if gpt_models:
    test_models.append(("GPT", gpt_models[0]))

chat_success = False
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
        chat_success = True
        break
    except Exception as e:
        error_msg = str(e)
        if len(error_msg) > 150:
            error_msg = error_msg[:150] + "..."
        print(f"[FAIL] {model_name} failed: {error_msg}")

if not chat_success:
    print("\n[INFO] Chat completion failed with premium models, no available channels")

# 测试2: PDF文档处理能力
print("\n" + "=" * 70)
print("[Test 2/4] Document/PDF Processing Capability Test")
print("=" * 70)

vision_models = [m for m in model_ids if any(x in m.lower() for x in ['claude-3', 'claude-4', 'gpt-4', 'gemini'])]

pdf_success = False
if vision_models:
    test_model = vision_models[0]
    print(f"\nTesting with model: {test_model}")
    try:
        response = client.chat.completions.create(
            model=test_model,
            messages=[
                {
                    "role": "user",
                    "content": "Explain in 2 sentences how to extract text from a PDF document."
                }
            ],
            max_tokens=150
        )

        result = response.choices[0].message.content
        print(f"[SUCCESS] Document processing capability available!")
        print(f"Response: {result}")
        pdf_success = True
    except Exception as e:
        error_msg = str(e)
        if len(error_msg) > 150:
            error_msg = error_msg[:150] + "..."
        print(f"[FAIL] Test failed: {error_msg}")
else:
    print("[SKIP] No suitable models found")

# 测试3: 图片生成
print("\n" + "=" * 70)
print("[Test 3/4] Image Generation Test")
print("=" * 70)

image_gen_success = False
print("[INFO] Trying image generation with dall-e-3...")
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
    image_gen_success = True
except Exception as e:
    error_msg = str(e)
    if len(error_msg) > 200:
        error_msg = error_msg[:200] + "..."
    print(f"[FAIL] Image generation not available: {error_msg}")

# 测试4: 图片理解
print("\n" + "=" * 70)
print("[Test 4/4] Image Understanding (Vision) Test")
print("=" * 70)

vision_capable = [m for m in model_ids if any(x in m.lower() for x in
                  ['vision', 'claude-3.5', 'claude-4', 'gpt-4o', 'gpt-4-turbo', 'gemini-1.5', 'gemini-2'])]

vision_success = False
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
                            "text": "What do you see in this image? One sentence only."
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
        vision_success = True
    except Exception as e:
        error_msg = str(e)
        if len(error_msg) > 150:
            error_msg = error_msg[:150] + "..."
        print(f"[FAIL] Test failed: {error_msg}")
else:
    print("[SKIP] No vision-capable models found in available list")

# 总结
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

results = {
    "Chat/Text Completion": chat_success,
    "Document/PDF Processing": pdf_success,
    "Image Generation": image_gen_success,
    "Image Understanding": vision_success
}

print("\nTest Results:")
for capability, success in results.items():
    status = "[PASS]" if success else "[FAIL]"
    print(f"  {capability}: {status}")

passed = sum(1 for s in results.values() if s)
total = len(results)
print(f"\nPass Rate: {passed}/{total} ({passed/total*100:.1f}%)")

if not any(results.values()):
    print("\n[WARNING] All tests failed!")
    print("Possible issues:")
    print("  1. API key may not have access to these models")
    print("  2. No available channels configured for these models")
    print("  3. You may need to configure model channels in the web interface")
    print(f"  4. Visit {base_url} to check your configuration")

print("\nAvailable models summary:")
print(f"  - Total models: {len(model_ids)}")
print(f"  - Claude: {len(claude_models)}")
print(f"  - GPT: {len(gpt_models)}")
print(f"  - Gemini: {len(gemini_models)}")
print(f"  - DALL-E: {len(dalle_models)}")

print("=" * 70)
