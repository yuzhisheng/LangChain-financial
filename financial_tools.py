import yfinance as yf
from datetime import datetime
import json
import re
import akshare as ak

def get_stock_financial_statement(symbol, report_table='income', period_type='annual', period=1):
    """获取股票的财务报表数据

    参数:
        symbol (str): 股票代码，需符合yfinance格式要求
        report_table (str): 报表类型，可选值: 'income' (利润表), 'balance' (资产负债表), 'cash' (现金流量表)
        period_type (str): 财报周期，可选值: 'annual' (年度), 'quarterly' (季度)
        period (int): 获取最近几期的数据，默认为1

    返回:
        pandas.DataFrame: 包含财务数据的DataFrame
        str: 错误信息（如果发生错误）
    """
    # 验证股票代码格式
    if not symbol or not symbol.strip():
        return "无效的股票代码，请输入有效的字母或数字组合（如'AAPL'）。"
    

    # 创建Ticker对象
    ticker = yf.Ticker(symbol)
    
    info = ticker.info
    print(f"公司名称: {info.get('longName', '未找到')}")
    print(f"当前价格: {info.get('currentPrice', '未找到')}")

    # 根据报表类型和时间周期获取数据
    table_map = {
        ('income', 'annual'): ticker.income_stmt,
        ('income', 'quarterly'): ticker.quarterly_income_stmt,
        ('balance', 'annual'): ticker.balance_sheet,
        ('balance', 'quarterly'): ticker.quarterly_balance_sheet,
        ('cash', 'annual'): ticker.cashflow,
        ('cash', 'quarterly'): ticker.quarterly_cashflow
    }
    
    # 获取对应报表数据
    key = (report_table, period_type)
    if key not in table_map:
        return f"不支持的报表类型组合: {report_table}/{period_type}"
    
    financials = table_map[key]
    df = financials.T.reset_index()
    df.columns = ["period"] + list(df.columns[1:])
    df = df.head(period)

    # 确保日期列按降序排列（最新的在前）
    financials = financials.reindex(financials.columns.sort_values(ascending=False), axis=1)
    # 检查数据是否存在
    if financials.empty:
        return f"未找到{symbol}的{report_table}数据"
    
    # 验证并调整period参数
    if period < 1:
        return "期数必须为正整数"
    available_periods = len(financials.columns)
    period = min(period, available_periods)

    
    result = {
    "stock_code": symbol,
    "report_table": report_table,
    "period_type": period_type,
    "periods": df["period"].dt.strftime('%Y-%m-%d').tolist(),  # 将Timestamp转换为ISO日期字符串
    "data": df.drop("period", axis=1).to_dict(orient="records")
    }

    return json.dumps({
        "status": "success", 
        "data": result
    }, ensure_ascii=False) 


def get_stock_financial_statement_akshare(symbol, report_table='income', period_type='annual', period=1):
    """使用akshare获取股票财务报表数据，支持A股和港股

    参数:
        symbol (str): 股票代码，A股格式如'000001.SZ'或'600000.SH'，港股格式如'00700.HK'
        report_table (str): 报表类型，可选值: 'income' (利润表), 'balance' (资产负债表), 'cash' (现金流量表)
        period_type (str): 财报周期，可选值: 'annual' (年度), 'quarterly' (季度)
        period (int): 获取最近几期的数据，默认为1
    """

    hk_report_type_map = {
        'income': '利润表',
        'balance': '资产负债表',
        'cash': '现金流量表'
    }
    hk_period_map = {
        'annual': '年度',
        'quarterly': '报告期'
    }
    # 验证报表类型和周期参数
    if report_table not in hk_report_type_map:
        return f"无效的报表类型: {report_table}，可选值: income, balance, cash"
    if period_type not in hk_period_map:
        return f"无效的周期类型: {period_type}，可选值: annual, quarterly"

    df = ak.stock_financial_hk_report_em(
        stock=symbol.split('.')[0],  # Reverted parameter name to 'stock' to match API
        symbol=hk_report_type_map[report_table],
        indicator=hk_period_map[period_type]
    )
    
    # Check if data retrieval failed
    if df is None:
        return f"无法获取{symbol}的{hk_report_type_map[report_table]}数据，请检查参数是否正确"
    
    if df.empty:
        return f"未找到{symbol}的{report_table}数据"

    # 取最近period期的数据
    df = df.head(500)
    df.to_csv(symbol + "+" + report_table + "_" + period_type + '.csv')

    result = {
        "stock_code": symbol,
        "report_table": report_table,
        "period_type": period_type,
        "periods": period,
        "data": df.to_dict(orient="records")
    }

    return json.dumps({
        "status": "success", 
        "data": result
    }, ensure_ascii=False)


