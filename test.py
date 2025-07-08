from langchain_google_vertexai import ChatVertexAI  # 替换为VertexAI
from langchain_openai import OpenAI, ChatOpenAI
import os

llm = OpenAI(
    model_name="gemini-2.5-pro",
    api_key="AIzaSyAUMSNybYYzpZl7BkteZIh_uGPakK5BZ2U",
    base_url="https://ai-financial.deno.dev/v1",
    temperature=0.7,
)

def test_model_connection():
    try:
        # 初始化VertexAI模型（支持地区代理）

        print("正在测试模型连接...")
        response = llm.invoke("请简单介绍一下你自己")
        
        print("模型连接成功！")
        print("响应内容:", response.content)
        return True
    except Exception as e:
        print(f"模型连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_model_connection()