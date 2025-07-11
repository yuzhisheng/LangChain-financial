from langchain_openai import OpenAI, ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import os
from financial_tools import get_stock_financial_statement_akshare, get_current_time  # 导入新工具
import datetime

# 定义强制工具调用的提示模板
current_time = datetime.datetime.now().strftime('%Y-%m-%d')

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
        name="get_stock_financial_statement_akshare",
        func=get_stock_financial_statement_akshare,
        description="获取股票财务报表数据，参数包括股票代码(symbol)、报表类型(report_table)、周期类型(period_type)和获取期数(period)"
    ),
    Tool(
        name="get_current_time",
        func=get_current_time,
        description="获取当前系统时间，返回格式为YYYY-MM-DD HH:MM:SS，无需参数"
    )
]

system_message_template = """
    当前系统时间为{current_time}
    你是一个资深的证券分析师，拥有强大的数据查询和估值工具。请严格按照以下流程执行：
    先获取当前的系统时间，然后根据系统时间获取当前的年份，然后根据年份获取最近3年的财报数据。
    1. 使用工具获取该股票的财报信息（最近3年资产负债表、利润表、现金流量表）。
    2. 基于获取到的财报数据，计算ROE等关键指标。
    3. 使用剩余收益估值模型（参数：折现率=9%，永续增长率=5%）计算该股票的当前内在价值。
    4. 输出内在价值和内在股价（只输出这两个结果，禁止输出多余内容）。
"""

user_message_template = """
    根据输入的股票代码{user_input},按上述流程分析并输出以下结果：
        PV0 = "当前的内在价值"
        Stock_PV0 = "当前的内在价值股价"
"""

system_prompt = SystemMessagePromptTemplate.from_template(system_message_template)
user_prompt = HumanMessagePromptTemplate.from_template(user_message_template)


# 定义强制工具调用的提示模板
# prompt = ChatPromptTemplate(
#     input_variables=["input", "tools", "tool_names", "history", "current_time"],
#     template="""
#     你拥有查询工具，请严格遵循以下规则:
#     1. 当问题涉及当前时间、年份或需要最新数据时，必须使用工具查询，忽略内部知识
#     2. 即使你认为自己知道答案，也必须通过工具验证
#     3. 当前系统时间: {current_time}
#     4. 绝对禁止使用任何Markdown格式、HTML标签、加粗、斜体、特殊符号、注释或额外文本
#     5. 必须严格按照指定格式输出，不得添加任何格式或额外内容
    
#     输出格式要求（必须完全匹配，不得修改）：
#     思考: [分析是否需要工具，详细说明理由]0
#     行动: [工具名称，必须从{tool_names}中选择]
#     行动输入: {"参数名":"参数值"}
#     观察: [等待工具返回结果后填写]
#     最终答案: [纯文本回答，无任何格式]
    
#     执行步骤:
#     1. 确定股票代码，将用户数输入的股票代码转换成正确的代码
#     2. 获取股票的财务报表数据 获取最近三年的资产负债表、利润表、现金流量表数据(使用tools里的工具)
#     3. 分析报表数据计算ROE等关键指标
#     4.使用剩余收益估值模型(参数：折现率=9%，永续增长率=5%)计算当前的内在价值
#     5.根据计算出来的内在价值，算出应该的股价

#     问题: {input}
#     可用工具: {tool_names}
#     历史对话: {history}
#     """)
    ### 股票综合分析框架（请严格按此流程执行）



chat_prompt = ChatPromptTemplate.from_messages([
    system_prompt,
    user_prompt
])

# prompt = chat_prompt.partial(current_time=current_time)
# 初始化代理


# 交互式查询
if __name__ == "__main__":
    while True:
        user_query = input("请输入股票代码:")
        if user_query.lower() == 'q':
            break
        system_param = {"current_time": current_time}
        human_param = {"user_input": user_query}

        # messages = chat_prompt.format_messages(**system_param, **human_param)

        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            prompt=chat_prompt,  # 应用自定义提示模板
            handle_parsing_errors=True,  #允许代理重试解析错误
            verbose=True
        )

        # 运行代理获取结果
        result = agent.invoke({"input": user_query, "user_input": user_query, "current_time": current_time})
        
        print(f"\n结果: {result}\n")
        
