import pandas as pd
import numpy as np
from typing import List, Optional, Tuple, Union
from scipy.interpolate import UnivariateSpline

class DataProcessor:
    """Handles data processing and transformation."""
    @staticmethod
    def remove_rework_curves(df: pd.DataFrame, threshold_hours: float = 3) -> pd.DataFrame:
        """Remove rework curves based on time difference threshold."""
        df = df.sort_values('datetime')
        df['time_diff'] = df['datetime'].diff().dt.total_seconds() / 3600 
        df['new_period'] = df['time_diff'] > threshold_hours
        df['period_id'] = df['new_period'].cumsum()
        first_period_df = df[df['period_id'] == 0]
        return first_period_df.drop(['new_period', 'period_id', 'time_diff'], axis=1)
    
    @staticmethod
    def extend_defect(data: pd.DataFrame, defect_keys: List[str] = [], 
                     defect_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Extend data with defect information."""
        if defect_data is None:
            return data
            
        # Filter defect data for relevant cells
        dfc = defect_data[defect_data['SERIALNO'].isin(data['cell_id'])]
        
        # Use provided defect keys or default process keys
        if not defect_keys:
            defect_keys = ('CAP', 'ADS', 'SCV', 'FCV', 'TCV', 'FOR', 'DCR', 'FIN')
        
        # Filter defect codes by keys
        dfc_need = [i for i in dfc['DEFECTREASONCODE'].unique() 
                   if any(defect_key in i for defect_key in defect_keys)]
        
        # Label data with defect information
        data['bad_label'] = 0
        data.loc[data['cell_id'].isin(
            dfc[dfc['DEFECTREASONCODE'].isin(dfc_need)]['SERIALNO'].unique()), 'bad_label'] = 1
        
        # Aggregate defect codes by cell
        defect_codes = dfc.groupby('SERIALNO')['DEFECTREASONCODE'].apply(', '.join).reset_index()
        
        # Merge defect codes into the data
        result = pd.merge(data, 
                         defect_codes, 
                         left_on='cell_id', 
                         right_on='SERIALNO', 
                         how='left')
        
        # Rename and drop columns
        result = result.rename(columns={'DEFECTREASONCODE': 'defect_code'})
        if 'SERIALNO' in result.columns:
            result = result.drop('SERIALNO', axis=1)
            
        return result
    
