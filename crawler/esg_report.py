# Fineta/crawler/esg_report.py

import requests
import pandas as pd
import json
from typing import Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from .exceptions import InvalidDateError, DataFetchError
from Fineta.stock import Portfolio
import urllib3

# 抑制 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ESGReportScraper:
    """
    ESG報告爬蟲類別，用於從台灣證券交易所獲取公司ESG相關數據
    """

    def __init__(self, portfolio: Portfolio):
        """
        初始化 ESG 報告爬蟲。

        Args:
            portfolio (Portfolio): 包含多個股票的投資組合對象
        """
        self.portfolio = portfolio
        self.base_url = "https://esggenplus.twse.com.tw/api/api/mopsEsg/singleCompanyData"

    def _validate_year(self, year: int) -> None:
        """
        驗證年份是否有效。

        Args:
            year (int): 要驗證的年份

        Raises:
            InvalidDateError: 如果年份無效
        """
        current_year = datetime.now().year
        if not (2015 <= year <= current_year):
            raise InvalidDateError(f"年份必須在 2015 和 {current_year} 之間")

    def fetch_esg_data(self, stock_id: str, year: int) -> Optional[Dict]:
        """
        獲取公司的ESG數據。

        Args:
            stock_id (str): 股票代號
            year (int): 年份

        Returns:
            Optional[Dict]: ESG數據，如果請求失敗則返回None
        """
        self._validate_year(year)
        
        payload = {
            "companyCode": stock_id,
            "yearList": [year],
            "companyName": "",
            "year": year
        }

        try:
            response = requests.post(self.base_url, json=payload, timeout=30, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"獲取 {stock_id} {year}年 ESG資料時發生錯誤: {e}")
            return None

    def get_portfolio_esg_data(self, year: int, max_workers: int = 5) -> Dict[str, pd.DataFrame]:
        """
        獲取投資組合中所有公司的ESG數據。

        Args:
            year (int): 要獲取的年份
            max_workers (int): 最大執行緒數

        Returns:
            Dict[str, pd.DataFrame]: 股票代號對應的ESG數據DataFrame
        """
        self._validate_year(year)
        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 建立future字典
            future_to_stock = {
                executor.submit(self.fetch_esg_data, stock_id, year): stock_id
                for stock in self.portfolio.stocks
                for stock_id in stock.get_all_stock_ids()
            }

            # 處理結果
            for future in as_completed(future_to_stock):
                stock_id = future_to_stock[future]
                try:
                    data = future.result()
                    if data:
                        # 處理數據並轉換為DataFrame
                        df = self._process_esg_data(data)
                        if not df.empty:
                            results[stock_id] = df
                            print(f"成功處理 {stock_id} 的ESG數據，共 {len(df)} 筆記錄")
                        else:
                            print(f"{stock_id} 無ESG數據")
                    else:
                        print(f"無法獲取 {stock_id} 的ESG數據")
                except Exception as e:
                    print(f"處理 {stock_id} 的ESG數據時發生錯誤: {e}")

        return results


    def _process_esg_data(self, response_data: Dict) -> pd.DataFrame:
        """
        處理 ESG 數據，將其轉換為 DataFrame 格式。
        
        Args:
            response_data (Dict): API 返回的原始數據
            
        Returns:
            pd.DataFrame: 處理後的 ESG 數據表格
        """
        try:
            processed_data = []
            
            # 檢查數據是否存在
            if not response_data or 'data' not in response_data or not response_data['data']:
                return pd.DataFrame()

            for tree_model in response_data['data'][0]['treeModels']:
                category = tree_model['categoryString']  # 環境/社會/治理
                
                for item in tree_model['items']:
                    declare_item = item['declareItemName']  # 第二層分類
                    
                    for section in item['sections']:
                        for control in section['controls']:
                            # 整理每一筆數據
                            data_row = {
                                '類別': category,
                                '項目': declare_item,
                                '區段': section['name'],
                                '指標名稱': control['title'],
                                '數值': control['value'],
                                '資料類型': control['ctrType']
                            }
                            processed_data.append(data_row)
            
            df = pd.DataFrame(processed_data)
            df['數值'] = df['數值'].apply(lambda x: str(x).replace(',', '') if isinstance(x, str) else x)
            df.loc[df['資料類型'] == 'number', '數值'] = pd.to_numeric(
                df.loc[df['資料類型'] == 'number', '數值'],
                errors='coerce'
            )
            
            return df
        
        except Exception as e:
            print(f"處理 ESG 數據時發生錯誤: {e}")
            return pd.DataFrame()

    def export_to_excel(self, data: Dict[str, pd.DataFrame], file_path: str) -> None:
        """
        將ESG數據導出到Excel文件。

        Args:
            data (Dict[str, pd.DataFrame]): 股票代號對應的ESG數據
            file_path (str): Excel文件路徑
        """
        if not data:
            print("沒有數據可供導出")
            return

        try:
            print("準備導出數據...")
            
            # 合併所有股票的數據
            all_data = []
            for stock_id, df in data.items():
                df = df.copy()
                df['股票代號'] = stock_id
                all_data.append(df)
            
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # 使用 ExcelWriter 導出數據
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 導出完整數據
                combined_df.to_excel(
                    writer,
                    sheet_name='ESG_DATA',
                    index=False
                )
                
                # 建立並導出摘要數據
                summary_df = combined_df.groupby(['股票代號', '類別', '項目']).size().reset_index(name='指標數量')
                summary_df.to_excel(
                    writer,
                    sheet_name='摘要',
                    index=False
                )
                
                # 依照類別分別導出
                for category in combined_df['類別'].unique():
                    category_df = combined_df[combined_df['類別'] == category]
                    safe_sheet_name = f'{category}'[:31]  # Excel工作表名稱限制31字元
                    category_df.to_excel(
                        writer,
                        sheet_name=safe_sheet_name,
                        index=False
                    )

            print(f"數據已成功導出至 {file_path}")
            print(f"共處理 {len(data)} 支股票的 ESG 數據")
            print(f"總記錄數: {len(combined_df)}")
            print("\n各類別資料分布:")
            print(combined_df.groupby(['類別'])['項目'].count())

        except Exception as e:
            print(f"導出數據時發生錯誤: {e}")
            print("錯誤詳細資訊:", str(e))
