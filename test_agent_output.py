import re
from main import agent, current_time

def check_output_format(output):
    """检查输出是否严格符合提示词要求"""
    # 检查五个部分
    pattern = (
        r"思考: .+?\n"
        r"行动: .+?\n"
        r"行动输入: \{.+?\}\n"
        r"观察: .+?\n"
        r"最终答案: 内在价值=[\d\.]+，内在股价=[\d\.]+$"
    )
    return re.search(pattern, output, re.DOTALL) is not None


def test_agent(stock_code, report_table="income", period_type="annual", period=3):
    """测试代理输出格式"""
    user_query = f"请分析{stock_code}最近三年的{report_table}，并给出内在价值和内在股价。"
    try:
        output = agent.run(
            input=user_query,
            current_time=current_time
        )
        print(f"\n测试股票: {stock_code}")
        print("输出:\n", output)
        if check_output_format(output):
            print("✓ 输出格式正确\n")
        else:
            print("✗ 输出格式不正确\n")
    except Exception as e:
        print(f"✗ 运行出错: {e}\n")

if __name__ == "__main__":
    # 可根据需要添加更多股票代码
    test_cases = ["0700", "AAPL", "600000"]
    for code in test_cases:
        test_agent(code) 