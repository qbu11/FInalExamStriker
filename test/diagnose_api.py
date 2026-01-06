import os
import sys
import requests
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
print("API Diagnostics")
print("=" * 70)
print(f"API Key: {api_key[:15]}...")
print(f"Base URL: {base_url}")
print("=" * 70)

# 测试1: 检查基础URL是否可访问
print("\n[Test 1] Testing base URL accessibility...")
try:
    response = requests.get(base_url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Type: {response.headers.get('content-type', 'unknown')}")

    if 'html' in response.headers.get('content-type', '').lower():
        print("[INFO] Base URL returns HTML - this is a web interface")
        print("[INFO] You may need to use the correct API endpoint")

except Exception as e:
    print(f"[ERROR] Cannot access base URL: {str(e)}")

# 测试2: 尝试chat completions端点
print("\n[Test 2] Testing chat completions endpoint...")
chat_url = f"{base_url}/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "gemini-2.5-pro",
    "messages": [
        {"role": "user", "content": "Hello"}
    ],
    "max_tokens": 50
}

try:
    response = requests.post(chat_url, json=payload, headers=headers, timeout=30)
    print(f"Endpoint: {chat_url}")
    print(f"Status Code: {response.status_code}")
    print(f"Response Type: {response.headers.get('content-type', 'unknown')}")

    if response.status_code == 200:
        try:
            data = response.json()
            print("[SUCCESS] Chat completions endpoint is working!")
            if 'choices' in data:
                print(f"Response: {data['choices'][0]['message']['content'][:100]}")
        except:
            print(f"[WARNING] Response is not JSON")
            print(f"First 200 chars: {response.text[:200]}")
    else:
        print(f"[ERROR] Request failed")
        print(f"Response: {response.text[:500]}")

except Exception as e:
    print(f"[ERROR] Request failed: {str(e)}")

# 测试3: 列出可用模型
print("\n[Test 3] Testing models endpoint...")
models_url = f"{base_url}/v1/models"

try:
    response = requests.get(models_url, headers=headers, timeout=30)
    print(f"Endpoint: {models_url}")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        try:
            data = response.json()
            print("[SUCCESS] Models endpoint is working!")
            if 'data' in data:
                print(f"Available models count: {len(data['data'])}")
                print("Sample models:")
                for model in data['data'][:5]:
                    print(f"  - {model.get('id', 'unknown')}")
        except:
            print(f"[WARNING] Response is not JSON")
            print(f"First 200 chars: {response.text[:200]}")
    else:
        print(f"[ERROR] Request failed")
        print(f"Response: {response.text[:500]}")

except Exception as e:
    print(f"[ERROR] Request failed: {str(e)}")

# 测试4: 图片生成端点
print("\n[Test 4] Testing image generation endpoint...")
images_url = f"{base_url}/v1/images/generations"
image_payload = {
    "model": "dall-e-3",
    "prompt": "a cat",
    "n": 1,
    "size": "1024x1024"
}

try:
    response = requests.post(images_url, json=image_payload, headers=headers, timeout=60)
    print(f"Endpoint: {images_url}")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        try:
            data = response.json()
            print("[SUCCESS] Image generation endpoint is working!")
            if 'data' in data and len(data['data']) > 0:
                print(f"Image URL: {data['data'][0].get('url', 'N/A')}")
        except:
            print(f"[WARNING] Response is not JSON")
            print(f"First 200 chars: {response.text[:200]}")
    else:
        print(f"[INFO] Image generation may not be supported")
        print(f"Response: {response.text[:300]}")

except Exception as e:
    print(f"[ERROR] Request failed: {str(e)}")

print("\n" + "=" * 70)
print("Diagnosis Complete")
print("=" * 70)
print("\nRecommendations:")
print("1. If base URL returns HTML, make sure to append '/v1' to base_url")
print("2. Check if your API key is valid and has the correct permissions")
print("3. Verify the models you're using are available on this endpoint")
print("4. Image generation may require a different endpoint or may not be supported")
print("=" * 70)
