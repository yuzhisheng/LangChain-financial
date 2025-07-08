from langchain_openai import OpenAI, ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.prompts import PromptTemplate
import os
from financial_tools import get_stock_financial_report  # 导入新工具

# 配置模型参数 (替换原有LLM初始化部分)
llm = OpenAI(
    model_name="gemini-2.5-pro",
    api_key="AIzaSyAUMSNybYYzpZl7BkteZIh_uGPakK5BZ2U",
    base_url="https://ai-financial.deno.dev/v1/models",
    temperature=0.7,
)

# 创建工具列表
tools = [
    Tool(
        name="StockFinancialReport",
        func=lambda x: get_stock_financial_report(*x.split(',')),
        description="用于获取指定股票的财报信息。输入格式应为：股票代码,财报类型(annual/quarterly),报表表格(income/balance/cash),期数。例如：AAPL,annual,income,3"
    )
]

# 初始化Agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 交互式查询
if __name__ == "__main__":
    while True:
        user_query = input("请输入您的查询（例如：获取AAPL的最近3年的年报），输入'q'退出：")
        if user_query.lower() == 'q':
            break
        try:
            result = agent.run(user_query)
            print(f"\n结果: {result}\n")
        except Exception as e:
            print(f"处理查询时出错: {str(e)}")