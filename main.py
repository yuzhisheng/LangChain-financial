from langchain_openai import OpenAI, ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.prompts import PromptTemplate
import os
from financial_tools import *  # 导入新工具
import datetime

# 配置模型参数 (替换原有LLM初始化部分)
llm = ChatOpenAI(
    model_name="gemini-2.5-pro",
    api_key="AIzaSyAUMSNybYYzpZl7BkteZIh_uGPakK5BZ2U",
    base_url="https://ai-financial.deno.dev/v1/models",
    temperature=0,
)

# 创建工具列表
tools = [
    Tool(
        name="StockFinancialReport",
        func=lambda x: get_stock_financial_statement_akshare(*x.split(',')),
        description="用于获取指定股票的财报信息。输入格式应为：股票代码,财报类型(annual/quarterly),报表表格(income/balance/cash),期数。例如：AAPL,annual,income,3"
    )
]

# 定义强制工具调用的提示模板
current_time = datetime.datetime.now().strftime('%Y-%m-%d')
prompt = PromptTemplate(
    template="""
    你拥有查询工具，请严格遵循以下规则:
    1. 当问题涉及当前时间、年份或需要最新数据时，必须使用工具查询，忽略内部知识
    2. 即使你认为自己知道答案，也必须通过工具验证
    3. 当前系统时间: {current_time}

    
    ### 股票综合分析框架（请严格按此流程执行）

    1. 确定股票代码

    2. 获取股票的财务报表数据
        获取最近三年的资产负债表、利润表、现金流量表数据(使用tools里的工具)

    3. 分析报表数据
        计算ROE等关键指标

    4.使用剩余收益估值模型(参数：折现率=9%，永续增长率=5%)计算当前的内在价值

    5.根据计算出来的内在价值，算出应该的股价

    ### 输出要求
    根据输入股票：（{input}），按上述流程分析，并输出以下JSON格式结果：
    {
        PV0 = "当前的内在价值"
        Stock_PV0 = "当前的内在价值股价"
    }
    
    历史对话: {history}
    """)
# 初始化代理
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    prompt=prompt,  # 应用自定义提示模板
    verbose=True
)

# 交互式查询
if __name__ == "__main__":
    while True:
        user_query = input("请输入您的查询（例如：获取AAPL的最近3年的年报），输入'q'退出：")
        if user_query.lower() == 'q':
            break
        try:
            # 运行代理获取结果
            result = agent.run(
                input=user_query,
                current_time=current_time  # 传递当前时间参数
            )
            print(f"\n结果: {result}\n")
        except Exception as e:
            print(f"处理查询时出错: {str(e)}")
        
