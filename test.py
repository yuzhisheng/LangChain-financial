from langchain_openai import OpenAI, ChatOpenAI
import os
from financial_tools import *  # 导入新工具

llm = ChatOpenAI(
    model_name="gemini-2.5-pro",
    openai_api_key="AIzaSyAUMSNybYYzpZl7BkteZIh_uGPakK5BZ2U",
    openai_api_base="https://ai-financial.deno.dev/v1",
    temperature=0.7,
)

def test_model_connection():
    print("正在测试模型连接...")
    response = llm.invoke("请简单介绍一下你自己")
    
    print("模型连接成功！")
    print("响应内容:", response.content)
    return True

if __name__ == "__main__":
    # test_model_connection()
    print(get_stock_financial_statement_akshare(symbol= "01378.HK",report_table = "income",  period_type ="quarterly", period= 100))