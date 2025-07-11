from financial_tools import normalize_stock_symbol, get_stock_financial_statement_akshare

def test_stock_symbol_normalization():
    """测试股票代码标准化功能"""
    test_cases = [
        ("0700", "0700.HK"),
        ("00700", "00700.HK"),
        ("0700.HK", "0700.HK"),
        ("01378", "01378.HK"),
        ("01378.HK", "01378.HK"),
        ("600000", "600000.SH"),
        ("000001", "000001.SZ"),
        ("AAPL", "AAPL"),
        ("", ""),
        ("  0700  ", "0700.HK"),
    ]
    
    print("测试股票代码标准化功能:")
    for input_symbol, expected in test_cases:
        result = normalize_stock_symbol(input_symbol)
        status = "✓" if result == expected else "✗"
        print(f"{status} 输入: '{input_symbol}' -> 输出: '{result}' (期望: '{expected}')")

def test_akshare_function():
    """测试akshare函数是否能正确处理0700"""
    print("\n测试akshare函数:")
    try:
        # 测试0700是否能自动转换为0700.HK
        result = get_stock_financial_statement_akshare("0700", "income", "annual", 1)
        print("✓ 0700转换测试成功")
        print(f"结果: {result[:200]}...")  # 只显示前200个字符
    except Exception as e:
        print(f"✗ 0700转换测试失败: {e}")

if __name__ == "__main__":
    test_stock_symbol_normalization()
    test_akshare_function() 