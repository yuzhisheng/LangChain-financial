import yfinance as yf
from datetime import datetime

def get_stock_financial_report(symbol, report_type='annual', report_table='income', period=1):
    """
    使用yfinance获取股票财报信息
    :param symbol: 股票代码，如"AAPL"
    :param report_type: 财报类型，'annual'（年报）或'quarterly'（季报）
    :param report_table: 报表类型，'income'（利润表）、'balance'（资产负债表）或'cash'（现金流量表）
    :param period: 获取的期数，默认为1
    :return: 格式化的财报信息字符串
    """
    try:
        # 创建Ticker对象
        ticker = yf.Ticker(symbol)
        
        # 根据报表类型和时间周期获取数据
        table_map = {
            ('income', 'annual'): ticker.financials,
            ('income', 'quarterly'): ticker.quarterly_financials,
            ('balance', 'annual'): ticker.balance_sheet,
            ('balance', 'quarterly'): ticker.quarterly_balance_sheet,
            ('cash', 'annual'): ticker.cashflow,
            ('cash', 'quarterly'): ticker.quarterly_cashflow
        }
        
        # 获取对应报表数据
        key = (report_table, report_type)
        if key not in table_map:
            return f"不支持的报表类型组合: {report_table}/{report_type}"
        
        financials = table_map[key]
        report_name_map = {
            'income': '利润表',
            'balance': '资产负债表',
            'cash': '现金流量表'
        }
        report_name = f"{report_name_map.get(report_table, report_table)}{'年度' if report_type == 'annual' else '季度'}"
        
        # 检查数据是否存在
        if financials.empty:
            return f"未找到{symbol}的{report_name}数据"
        
        # 取最近period期的数据
        recent_reports = financials.iloc[:, :period]
        
        # 格式化输出
        result = f"{symbol} {report_name}信息（最近{period}期）:\n"
        result += f"数据日期: {[col.strftime('%Y-%m-%d') for col in recent_reports.columns]}\n\n"
        
        # 为不同报表类型定义关键指标
        key_metrics = {
            'income': [
                'Total Revenue', 'Gross Profit', 'Operating Income',
                'Net Income', 'EPS Basic', 'EPS Diluted'
            ],
            'balance': [
                'Total Assets', 'Total Liabilities', 'Total Stockholder Equity',
                'Cash And Cash Equivalents', 'Current Assets', 'Current Liabilities'
            ],
            'cash': [
                'Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow',
                'End Cash Position', 'Capital Expenditures'
            ]
        }.get(report_table, [])
        
        for metric in key_metrics:
            if metric in recent_reports.index:
                values = recent_reports.loc[metric].apply(lambda x: f"${x:,.2f}" if x else "N/A")
                result += f"{metric}: {values.to_list()}\n"
        
        return result
    except Exception as e:
        return f"获取财报数据失败: {str(e)}"