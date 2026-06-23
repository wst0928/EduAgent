import os
from openai import OpenAI

# 1. 配置你的阿里云 API Key（直接填你测试成功的那个）
API_KEY = "sk-ws-H.RPPDLHR.yz63.MEYCIQCLGRfIdN5hYplyNDFEEt29BXsqftH-onZNLCb7ZdM4aQIhAIH6Em_aKBgLJZ9GfOpIkOTEAkWe_t9WGrztAetJ_lao"

# 2. 初始化客户端（直连阿里云，不走任何代理）
client = OpenAI(
    api_key=API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 3. 调用大模型（这就是你 A3 项目的核心功能）
def call_qwen(prompt):
    try:
        response = client.chat.completions.create(
            model="qwen-plus",  # 你测试通过的模型
            messages=[
                {"role": "system", "content": "你是一个智能助手，帮助用户解决问题。"},
                {"role": "user", "content": prompt}
            ],
            stream=False  # 关掉流式，避免 Codex 那种断连问题
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用失败: {e}"

# 4. 测试一下
if __name__ == "__main__":
    result = call_qwen("你好，请介绍一下你自己。")
    print(result)