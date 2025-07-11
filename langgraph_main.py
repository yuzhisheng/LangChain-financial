from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated, Sequence
import json
from financial_tools import normalize_stock_symbol, get_stock_financial_statement_akshare, get_current_time
import datetime
from IPython.display import Image, display

# 定义状态类型
class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], add_messages]
    stock_code: str
    normalized_stock_code: str
    financial_data: dict
    intrinsic_value: float
    intrinsic_price: float
    current_step: str

# 配置模型
llm = ChatOpenAI(
    model_name="gemini-2.5-pro",
    api_key="AIzaSyAUMSNybYYzpZl7BkteZIh_uGPakK5BZ2U",
    base_url="https://ai-financial.deno.dev/v1/models",
    temperature=0,
)

# 节点1: 股票代码标准化
def normalize_stock_code(state: AgentState) -> AgentState:
    """标准化股票代码"""
    stock_code = state["stock_code"]
    normalized_code = normalize_stock_symbol(stock_code)
    
    print(f"原始股票代码: {stock_code} -> 标准化后: {normalized_code}")
    
    return {
        **state,
        "stock_code": stock_code,
        "normalized_stock_code": normalized_code,
        "current_step": "normalized"
    }

# 节点2: 获取财报数据
def get_financial_data(state: AgentState) -> AgentState:
    """获取股票财报数据"""
    normalized_code = state["normalized_stock_code"]
    
    # 获取利润表数据
    income_args = {
        "symbol": normalized_code,
        "report_table": "income",
        "period_type": "annual",
        "period": 3
    }
    
    try:
        income_data = get_stock_financial_statement_akshare(income_args)
        financial_data = json.loads(income_data)
        
        return {
            **state,
            "financial_data": financial_data,
            "messages": [*state["messages"], SystemMessage(content=json.dumps(financial_data))],
            "current_step": "financial_data_obtained"
        }
    except Exception as e:
        print(f"获取财报数据失败: {e}")
        return {
            **state,
            "financial_data": {"error": str(e)},
            "current_step": "financial_data_error"
        }

# 节点3: 计算估值
def calculate_valuation(state: AgentState) -> AgentState:
    """使用剩余收益估值模型计算内在价值"""
    try:
        # 这里应该基于financial_data进行实际计算
        # 简化实现，实际应该解析财报数据计算ROE等指标
        intrinsic_value = 150.0  # 示例值
        intrinsic_price = 300.0  # 示例值

        return llm.invoke(state["messages"])
        
        # return {
        #     **state,
        #     "intrinsic_value": intrinsic_value,
        #     "intrinsic_price": intrinsic_price,
        #     "current_step": "valuation_completed"
        # }
    except Exception as e:
        print(f"估值计算失败: {e}")
        return {
            **state,
            "intrinsic_value": 0.0,
            "intrinsic_price": 0.0,
            "current_step": "valuation_error"
        }

# 节点4: 生成最终答案
def generate_final_answer(state: AgentState) -> AgentState:
    """生成最终答案"""
    intrinsic_value = state["intrinsic_value"]
    intrinsic_price = state["intrinsic_price"]
    
    final_answer = f"内在价值={intrinsic_value}，内在股价={intrinsic_price}"
    
    # 添加AI消息到状态
    ai_message = AIMessage(content=final_answer)
    
    return {
        **state,
        "messages": [*state["messages"], ai_message],
        "current_step": "completed"
    }

# 创建图
def create_graph():
    """创建LangGraph工作流"""
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("normalize_stock_code", normalize_stock_code)
    workflow.add_node("get_financial_data", get_financial_data)
    workflow.add_node("calculate_valuation", calculate_valuation)
    workflow.add_node("generate_final_answer", generate_final_answer)
    
    # 设置入口点
    workflow.set_entry_point("normalize_stock_code")
    
    # 添加边
    workflow.add_edge("normalize_stock_code", "get_financial_data")
    workflow.add_edge("get_financial_data", "calculate_valuation")
    workflow.add_edge("calculate_valuation", "generate_final_answer")
    workflow.add_edge("generate_final_answer", END)
    
    return workflow.compile()


system_message_prompt ="""
你是一个资深的证券分析师，拥有强大的数据查询和估值工具。请严格按照以下流程执行：
 先获取当前的系统时间，然后根据系统时间获取当前的年份，然后根据年份获取最近三年的财报数据。
1. 使用工具获取该股票的财报信息（最近三年资产负债表、利润表、现金流量表）。
2. 基于获取到的财报数据，计算ROE等关键指标。
3. 使用剩余收益估值模型（参数：折现率=9%，永续增长率=5%）计算该股票的当前内在价值。
4. 输出内在价值和内在股价（只输出这两个结果，禁止输出多余内容）。
"""

user_message_prompt =  """
根据输入{user_input}，按上述流程分析并输出以下JSON格式结果：
    {
        PV0 = "当前的内在价值"
        Stock_PV0 = "当前的内在价值股价"
    }
"""


# 主函数
def main():
    """主函数"""
    graph = create_graph()
    
    while True:
        user_input = input("请输入股票代码（如：0700），输入'q'退出：")
        if user_input.lower() == 'q':
            break
            
        try:
            # 创建初始状态
            initial_state = {
                "messages": [HumanMessage(content=user_message_prompt), SystemMessage(content=system_message_prompt)],
                "stock_code": user_input,
                "normalized_stock_code": "",
                "financial_data": {},
                "intrinsic_value": 0.0,
                "intrinsic_price": 0.0,
                "current_step": "start"
            }

            # 运行图
            result = graph.invoke(initial_state)

            display(Image(graph.get_graph().draw_mermaid_png()))

            for message in result["messages"]:
                message.pretty_print()
            
            # 输出结果
            print(f"\n最终结果: {result['messages'][-1].content}")
            print(f"处理步骤: {result['current_step']}")
            
        except Exception as e:
            print(f"处理出错: {e}")

if __name__ == "__main__":
    main() 