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


    return pd.DataFrame(fundamental_data)
