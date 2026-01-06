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
print("Raw API Response Test")
print("=" * 70)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Test 1: 简单聊天请求
print("\n[Test 1] Testing chat completion with claude-3-5-haiku...")
chat_url = f"{base_url}/v1/chat/completions"
payload = {
    "model": "claude-3-5-haiku-20241022",
    "messages": [
        {"role": "user", "content": "Say hello"}
    ],
    "max_tokens": 50
}

try:
    response = requests.post(chat_url, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"\nRaw Response (first 500 chars):")
    print(response.text[:500])
    print("\n" + "-" * 70)

    if response.status_code == 200:
        try:
            data = response.json()
            print("\nParsed JSON successfully!")
            print(f"Keys in response: {list(data.keys())}")
            if 'choices' in data:
                print(f"Message: {data['choices'][0]['message']['content']}")
            elif 'error' in data:
                print(f"Error: {data['error']}")
        except:
            print("\nCannot parse as JSON")

except Exception as e:
    print(f"Request failed: {str(e)}")

# Test 2: 测试一个免费/可用的模型
print("\n\n[Test 2] Testing with gpt-3.5-turbo (usually more widely available)...")
payload['model'] = 'gpt-3.5-turbo'

try:
    response = requests.post(chat_url, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"\nRaw Response (first 500 chars):")
    print(response.text[:500])
    print("\n" + "-" * 70)

    if response.status_code == 200:
        try:
            data = response.json()
            print("\nParsed JSON successfully!")
            print(f"Keys in response: {list(data.keys())}")
            if 'choices' in data:
                print(f"[SUCCESS] Message: {data['choices'][0]['message']['content']}")
        except:
            print("\nCannot parse as JSON")
    elif response.status_code == 503:
        try:
            error_data = response.json()
            print(f"\n[ERROR] {error_data.get('error', {}).get('message', 'Unknown error')}")
        except:
            pass

except Exception as e:
    print(f"Request failed: {str(e)}")

# Test 3: 列出所有可用模型并尝试找到一个真正可用的
print("\n\n[Test 3] Checking which models might actually work...")
try:
    models_response = requests.get(f"{base_url}/v1/models", headers=headers, timeout=30)
    if models_response.status_code == 200:
        models_data = models_response.json()
        all_models = [m['id'] for m in models_data.get('data', [])]

        # 尝试一些常见的模型
        common_models = ['gpt-3.5-turbo', 'gpt-4', 'claude-3-haiku-20240307', 'text-davinci-003']
        available_common = [m for m in common_models if m in all_models]

        print(f"\nTotal models listed: {len(all_models)}")
        print(f"Common models available: {available_common}")

        if available_common:
            print(f"\nTrying first available common model: {available_common[0]}")
            payload['model'] = available_common[0]
            response = requests.post(chat_url, json=payload, headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if 'choices' in data:
                    print(f"[SUCCESS] {available_common[0]} works!")
                    print(f"Response: {data['choices'][0]['message']['content']}")
            else:
                print(f"Failed: {response.text[:200]}")

except Exception as e:
    print(f"Error: {str(e)}")

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
