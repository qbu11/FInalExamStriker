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
print("Gemini模型功能测试")
print("=" * 70)
print(f"API Key: {api_key[:15]}...")
print(f"Base URL: {base_url}")
print("=" * 70)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 要测试的Gemini模型列表
gemini_models = [
    "gemini-3-flash-preview",
    "gemini-3-pro-preview",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "google/gemini-3-flash-preview",
    "google/gemini-3-pro-preview"
]

chat_url = f"{base_url}/v1/chat/completions"

# 存储测试结果
results = {}

print("\n" + "=" * 70)
print("测试1: 聊天问答功能")
print("=" * 70)

for model in gemini_models:
    print(f"\n测试模型: {model}")
    print("-" * 70)

    results[model] = {
        '聊天问答': False,
        'PDF处理': False,
        '图片理解': False
    }

    try:
        payload = {
            "model": model,
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
                print(f"✓ 聊天测试通过")
                print(f"  回答: {message[:100]}")
                results[model]['聊天问答'] = True
            else:
                print(f"✗ 响应格式错误")
        else:
            error = response.json().get('error', {}).get('message', '未知错误')
            print(f"✗ 聊天测试失败: {error[:100]}")

    except Exception as e:
        print(f"✗ 聊天测试异常: {str(e)[:100]}")

print("\n\n" + "=" * 70)
print("测试2: PDF文档处理能力")
print("=" * 70)

for model in gemini_models:
    print(f"\n测试模型: {model}")
    print("-" * 70)

    try:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "请详细说明如何使用Python的PyPDF2库从PDF文件中提取文本，给出完整代码示例"
                }
            ],
            "max_tokens": 300
        }

        response = requests.post(chat_url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            if 'choices' in data:
                message = data['choices'][0]['message']['content']
                print(f"✓ PDF处理能力测试通过")
                print(f"  回答: {message[:150]}...")
                results[model]['PDF处理'] = True
            else:
                print(f"✗ 响应格式错误")
        else:
            error = response.json().get('error', {}).get('message', '未知错误')
            print(f"✗ PDF处理测试失败: {error[:100]}")

    except Exception as e:
        print(f"✗ PDF处理测试异常: {str(e)[:100]}")

print("\n\n" + "=" * 70)
print("测试3: 图片理解功能（Vision）")
print("=" * 70)

# 使用一个简单的base64编码的小图片（1x1红色像素的PNG）
simple_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

for model in gemini_models:
    print(f"\n测试模型: {model}")
    print("-" * 70)

    # 尝试方法1: 使用base64编码
    try:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "这张图片是什么颜色？请简短回答"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{simple_image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 100
        }

        response = requests.post(chat_url, json=payload, headers=headers, timeout=60)

        if response.status_code == 200:
            data = response.json()
            if 'choices' in data:
                message = data['choices'][0]['message']['content']
                print(f"✓ 图片理解测试通过（base64方式）")
                print(f"  回答: {message}")
                results[model]['图片理解'] = True
            else:
                print(f"✗ 响应格式错误")
        else:
            error = response.json().get('error', {}).get('message', '未知错误')
            print(f"✗ 图片理解测试失败: {error[:150]}")

    except Exception as e:
        print(f"✗ 图片理解测试异常: {str(e)[:150]}")

# 生成测试报告
print("\n\n" + "=" * 70)
print("测试结果汇总")
print("=" * 70)

print("\n{:<35} {:<12} {:<12} {:<12}".format("模型", "聊天问答", "PDF处理", "图片理解"))
print("-" * 70)

for model, tests in results.items():
    chat_status = "✓ 通过" if tests['聊天问答'] else "✗ 失败"
    pdf_status = "✓ 通过" if tests['PDF处理'] else "✗ 失败"
    vision_status = "✓ 通过" if tests['图片理解'] else "✗ 失败"

    print("{:<35} {:<12} {:<12} {:<12}".format(
        model[:33], chat_status, pdf_status, vision_status
    ))

# 统计
print("\n" + "=" * 70)
print("功能可用性统计")
print("=" * 70)

chat_working = sum(1 for r in results.values() if r['聊天问答'])
pdf_working = sum(1 for r in results.values() if r['PDF处理'])
vision_working = sum(1 for r in results.values() if r['图片理解'])
total_models = len(results)

print(f"\n聊天问答: {chat_working}/{total_models} 个模型可用")
print(f"PDF处理: {pdf_working}/{total_models} 个模型可用")
print(f"图片理解: {vision_working}/{total_models} 个模型可用")

# 找出完全可用的模型
fully_working = [model for model, tests in results.items()
                 if all(tests.values())]

if fully_working:
    print(f"\n完全可用的模型（所有功能都通过）:")
    for model in fully_working:
        print(f"  ✓ {model}")
else:
    print(f"\n没有完全可用的模型（至少有一项功能失败）")

    # 显示部分可用的模型
    partially_working = [model for model, tests in results.items()
                        if any(tests.values()) and not all(tests.values())]

    if partially_working:
        print(f"\n部分可用的模型:")
        for model in partially_working:
            working_features = [k for k, v in results[model].items() if v]
            print(f"  • {model}: {', '.join(working_features)}")

print("\n" + "=" * 70)
print("推荐使用:")
print("=" * 70)

if fully_working:
    print(f"推荐使用: {fully_working[0]}")
    print("该模型支持聊天问答、PDF处理和图片理解三项功能")
elif chat_working > 0:
    working_model = [m for m, r in results.items() if r['聊天问答']][0]
    print(f"推荐使用: {working_model}")
    features = [k for k, v in results[working_model].items() if v]
    print(f"支持功能: {', '.join(features)}")
else:
    print("警告: 所有测试的Gemini模型都不可用")
    print("请检查:")
    print("  1. API密钥是否有效")
    print("  2. 是否配置了Gemini模型的渠道")
    print("  3. 账户是否有足够的配额")

print("=" * 70)
