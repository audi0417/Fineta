def fetch_esg_report(self, stock_id, year):
    """
    使用爬蟲技術蟲獲取 ESG 報告的內容

    Args:
        stock_id (str): 股票代號
        year (int): 年分

    Returns:
        str: 包含 ESG 報告的內容
    """
    url = f'https://esggenplus.twse.com.tw/api/api/mopsEsg/singleCompanyData'
    payload = {"companyCode": "1101", "yearList": [2023], "companyName": "", year: 2023}
    response = requests.post(url, data=payload)
    response.encoding = 'utf-8'
    return response.text

