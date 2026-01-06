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
print("Gemini模型测试")
print("=" * 70)

# 图中的Gemini模型列表
test_models = [
    "gemini-3-flash-preview",
    "gemini-3-pro-preview",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "google/gemini-3-flash-preview",
    "google/gemini-3-pro-preview"
]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

chat_url = f"{base_url}/v1/chat/completions"

# 测试每个模型
results = {}

for model in test_models:
    print(f"\n测试模型: {model}")
    print("-" * 70)

    try:
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "你好，请说'测试成功'"}
            ],
            "max_tokens": 50
        }

        response = requests.post(chat_url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            if 'choices' in data:
                message = data['choices'][0]['message']['content']
                print(f"✓ 状态: 可用")
                print(f"  响应: {message}")
                results[model] = "可用"
            else:
                print(f"✗ 状态: 响应格式错误")
                results[model] = "格式错误"
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', '未知错误')
            print(f"✗ 状态: 不可用")
            print(f"  错误: {error_msg[:100]}")

            # 判断错误类型
            if "No available channels" in error_msg or "无可用渠道" in error_msg:
                results[model] = "未配置渠道"
            elif "model_not_found" in error_msg:
                results[model] = "模型不存在"
            else:
                results[model] = "其他错误"

    except Exception as e:
        print(f"✗ 状态: 请求失败")
        print(f"  错误: {str(e)[:100]}")
        results[model] = "请求异常"

# 总结
print("\n" + "=" * 70)
print("测试结果汇总")
print("=" * 70)

available_count = 0
for model, status in results.items():
    status_icon = "✓" if status == "可用" else "✗"
    print(f"{status_icon} {model}: {status}")
    if status == "可用":
        available_count += 1

print(f"\n可用模型数: {available_count}/{len(test_models)}")
print("=" * 70)
