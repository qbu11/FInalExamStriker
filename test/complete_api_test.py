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
print("完整API功能测试")
print("=" * 70)
print(f"API Key: {api_key[:15]}...")
print(f"Base URL: {base_url}")
print("=" * 70)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 测试结果
test_results = {}

# 测试1: 聊天问答功能
print("\n[测试 1/4] 聊天问答功能")
print("-" * 70)
try:
    chat_url = f"{base_url}/v1/chat/completions"
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "你好，请用一句话介绍你自己"}
        ],
        "max_tokens": 100
    }

    response = requests.post(chat_url, json=payload, headers=headers, timeout=30)

    if response.status_code == 200:
        data = response.json()
        if 'choices' in data:
            message = data['choices'][0]['message']['content']
            print(f"✓ 测试成功 (模型: {payload['model']})")
            print(f"  回答: {message}")
            test_results['聊天问答'] = True
        else:
            print(f"✗ 响应格式错误")
            test_results['聊天问答'] = False
    else:
        error = response.json().get('error', {}).get('message', '未知错误')
        print(f"✗ 测试失败: {error}")
        test_results['聊天问答'] = False
except Exception as e:
    print(f"✗ 测试失败: {str(e)}")
    test_results['聊天问答'] = False

# 测试2: PDF解析能力测试（使用视觉模型测试文档处理）
print("\n[测试 2/4] PDF文档处理能力")
print("-" * 70)

# 先尝试获取支持视觉的模型
vision_models = ['gpt-4o', 'gpt-4-turbo', 'claude-3-5-sonnet-20241022', 'gemini-2.5-flash']
pdf_test_model = None

# 检查哪个模型可用
try:
    models_response = requests.get(f"{base_url}/v1/models", headers=headers, timeout=30)
    if models_response.status_code == 200:
        available_models = [m['id'] for m in models_response.json().get('data', [])]
        for model in vision_models:
            if model in available_models:
                pdf_test_model = model
                break

    if not pdf_test_model:
        pdf_test_model = 'gpt-4'  # fallback

    print(f"使用模型: {pdf_test_model}")

    payload = {
        "model": pdf_test_model,
        "messages": [
            {
                "role": "user",
                "content": "请用2-3句话解释如何使用Python从PDF文件中提取文本内容"
            }
        ],
        "max_tokens": 200
    }

    response = requests.post(chat_url, json=payload, headers=headers, timeout=30)

    if response.status_code == 200:
        data = response.json()
        if 'choices' in data:
            message = data['choices'][0]['message']['content']
            print(f"✓ 测试成功 - 模型具备文档处理指导能力")
            print(f"  回答: {message[:150]}...")
            test_results['PDF处理能力'] = True
        else:
            print(f"✗ 响应格式错误")
            test_results['PDF处理能力'] = False
    else:
        error = response.json().get('error', {}).get('message', '未知错误')
        print(f"✗ 测试失败: {error[:100]}")
        test_results['PDF处理能力'] = False

except Exception as e:
    print(f"✗ 测试失败: {str(e)}")
    test_results['PDF处理能力'] = False

# 测试3: 图片生成功能
print("\n[测试 3/4] 图片生成功能")
print("-" * 70)
try:
    images_url = f"{base_url}/v1/images/generations"
    payload = {
        "model": "dall-e-3",
        "prompt": "一只可爱的卡通猫咪在看书",
        "n": 1,
        "size": "1024x1024"
    }

    response = requests.post(images_url, json=payload, headers=headers, timeout=60)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            image_url = data['data'][0].get('url')
            print(f"✓ 测试成功")
            print(f"  图片URL: {image_url}")
            test_results['图片生成'] = True
        else:
            print(f"✗ 响应格式错误")
            test_results['图片生成'] = False
    else:
        error = response.json().get('error', {}).get('message', '未知错误')
        print(f"✗ 测试失败: {error[:100]}")
        print(f"  说明: 该API端点可能未配置DALL-E渠道")
        test_results['图片生成'] = False

except Exception as e:
    print(f"✗ 测试失败: {str(e)[:100]}")
    test_results['图片生成'] = False

# 测试4: 图片理解（Vision）功能
print("\n[测试 4/4] 图片理解功能")
print("-" * 70)

# 使用支持vision的模型
vision_test_models = ['gpt-4o', 'gpt-4-turbo', 'gpt-4-vision-preview', 'claude-3-5-sonnet-20241022']
vision_model = None

try:
    # 检查哪个vision模型可用
    for model in vision_test_models:
        if model in available_models:
            vision_model = model
            break

    if not vision_model:
        vision_model = 'gpt-4'  # fallback

    print(f"使用模型: {vision_model}")

    # 测试图片URL
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/1200px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

    payload = {
        "model": vision_model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请用一句话描述这张图片的内容"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": test_image_url
                        }
                    }
                ]
            }
        ],
        "max_tokens": 150
    }

    response = requests.post(chat_url, json=payload, headers=headers, timeout=60)

    if response.status_code == 200:
        data = response.json()
        if 'choices' in data:
            message = data['choices'][0]['message']['content']
            print(f"✓ 测试成功")
            print(f"  描述: {message}")
            test_results['图片理解'] = True
        else:
            print(f"✗ 响应格式错误")
            test_results['图片理解'] = False
    else:
        error = response.json().get('error', {}).get('message', '未知错误')
        print(f"✗ 测试失败: {error[:100]}")
        test_results['图片理解'] = False

except Exception as e:
    print(f"✗ 测试失败: {str(e)[:100]}")
    test_results['图片理解'] = False

# 总结报告
print("\n" + "=" * 70)
print("测试总结报告")
print("=" * 70)

for test_name, result in test_results.items():
    status = "✓ 通过" if result else "✗ 失败"
    print(f"{test_name}: {status}")

passed = sum(1 for r in test_results.values() if r)
total = len(test_results)
print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")

if passed < total:
    print("\n说明:")
    if not test_results.get('图片生成', False):
        print("  - 图片生成功能需要在API管理界面配置DALL-E渠道")
    if not test_results.get('图片理解', False):
        print("  - 图片理解功能需要使用支持vision的模型（如GPT-4V, Claude 3等）")

print("\n可用的模型列表:")
try:
    models_response = requests.get(f"{base_url}/v1/models", headers=headers, timeout=30)
    if models_response.status_code == 200:
        all_models = [m['id'] for m in models_response.json().get('data', [])]
        print(f"  总计: {len(all_models)} 个模型")
        print(f"  GPT系列: {len([m for m in all_models if 'gpt' in m.lower()])} 个")
        print(f"  Claude系列: {len([m for m in all_models if 'claude' in m.lower()])} 个")
        print(f"  Gemini系列: {len([m for m in all_models if 'gemini' in m.lower()])} 个")
except:
    pass

print("=" * 70)
