# FINPLUS/indicators/fundamental_indicators.py

import pandas as pd
import numpy as np

def calculate_fundamentals(df: pd.DataFrame) -> pd.DataFrame:
    fundamental_data = {
        'Stock': [],
        'EPS': [],
        'P/E': [],
        'P/B': [],
        'Dividend Yield': []
    }

    for stock in df.index.levels[0]:
        fundamental_data['Stock'].append(stock)
        fundamental_data['EPS'].append(np.random.uniform(1, 10))
        fundamental_data['P/E'].append(np.random.uniform(10, 30))
        fundamental_data['P/B'].append(np.random.uniform(1, 5))
        fundamental_data['Dividend Yield'].append(np.random.uniform(1, 5))

    return pd.DataFrame(fundamental_data)
