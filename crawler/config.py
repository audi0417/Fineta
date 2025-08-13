# Fineta/crawler/config.py

"""
爬蟲模組的配置檔案
包含 URL、請求參數、重試設定等常數
"""

# 台灣證券交易所相關 URL
TWSE_URLS = {
    'financial_statement': 'https://mopsov.twse.com.tw/server-java/t164sb01',
    'balance_sheet': 'https://mopsov.twse.com.tw/server-java/t164sb01',
    'income_statement': 'https://mopsov.twse.com.tw/server-java/t164sb01',
    'cash_flow': 'https://mopsov.twse.com.tw/server-java/t164sb01',
    'esg_report': 'https://esggenplus.twse.com.tw/api/api/mopsEsg/singleCompanyData',
    'stock_price': 'https://www.twse.com.tw/exchangeReport/BWIBBU',
    'fundamental_data': 'https://www.twse.com.tw/exchangeReport/BWIBBU',
}

# 台灣櫃買中心相關 URL
TPEX_URLS = {
    'financial_statement': 'https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php',
    'balance_sheet': 'https://www.tpex.org.tw/web/stock/financial_info/balancesheet.php',
    'income_statement': 'https://www.tpex.org.tw/web/stock/financial_info/income.php',
    'cash_flow': 'https://www.tpex.org.tw/web/stock/financial_info/cashflow.php',
    'stock_price': 'https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote.php',
}

# 請求標頭設定
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Content-Type': 'application/x-www-form-urlencoded',
}

# 請求逾時設定
REQUEST_TIMEOUT = 30

# 請求設定
REQUEST_CONFIG = {
    'timeout': 30,
    'verify': False,  # 台灣證交所 SSL 憑證問題
    'retries': 3,
    'delay': 5,
}

# 資料類型對應
FINANCIAL_STATEMENT_TYPES = {
    '資產負債表': 0,
    '綜合損益表': 1,
    '現金流量表': 2,
}

# 季度設定
VALID_SEASONS = [1, 2, 3, 4]

# 年份範圍設定
MIN_YEAR = 2010
MAX_YEAR = 2030

# ESG 相關設定
ESG_CONFIG = {
    'min_year': 2015,
    'max_year': 2030,
    'categories': {
        '環境': 0,
        '社會': 1,
        '治理': 2,
    }
}

# 錯誤訊息模板
ERROR_MESSAGES = {
    'invalid_year': '年份必須在 {min_year} 和 {max_year} 之間',
    'invalid_season': '季度必須在 1 到 4 之間',
    'invalid_stock_id': '股票代號格式不正確',
    'no_data': '找不到指定的資料',
    'connection_error': '連線失敗，請檢查網路連線',
    'ssl_error': 'SSL 憑證驗證失敗',
    'timeout_error': '請求逾時',
}

# 日期格式
DATE_FORMATS = {
    'input': '%Y-%m-%d',
    'api': '%Y%m%d',
    'display': '%Y年%m月%d日',
}
