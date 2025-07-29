# main.py
from .config import FetcherConfig
from .data_fetcher import DataFetcher
from .data_processor import DataProcessor
from .visualizer import Visualizer
from typing import List, Optional, Dict, Union, Tuple
from .tools import Tool


class BatteryDataManager:
    """电池数据管理类，提供统一接口"""
    def __init__(self, base: str, wip_line: str = None, table_prefix: str = "POUCH"):
        """初始化电池数据管理器"""
        self.config = FetcherConfig(base=base, wip_line=wip_line, table_prefix=table_prefix)
        self.fetcher = DataFetcher(self.config)
        self.processor = DataProcessor()
        self.visualizer = Visualizer(self.fetcher)
        self.tool = Tool()
        print(f"BatteryDataManager已初始化: {base}.{wip_line} with {table_prefix}")
    
    def set_config(self, base: str, wip_line: str = None, table_prefix: str = "POUCH"):
        """更新配置"""
        self.config = FetcherConfig(base=base, wip_line=wip_line, table_prefix=table_prefix)
        self.fetcher = DataFetcher(self.config)
        self.visualizer = Visualizer(self.fetcher)
        print(f"配置已更新: {base}.{wip_line} with {table_prefix}")
    
    # ========== 数据获取方法 ==========
    def get_data_by_cell_ids(self, cell_ids: list, cp_names: list):
        """获取指定电池ID的CP数据"""
        return self.fetcher.get_multi_cp_by_celllist(cell_ids, cp_names)
    
    def get_data_by_date_range(self, start_date: str, end_date: str, cp_names: list, local_cache: bool = False):
        """获取日期范围内的CP数据"""
        return self.fetcher.get_multi_cp_by_day_period(start_date, end_date, cp_names, local_cache)
    
    def get_data_by_day(self, day: str, cp_names: list):
        """获取指定日期的CP数据"""
        return self.fetcher.get_multi_cp_by_day(day, cp_names)
    
    def get_data_by_day_latest(self, day: str, cp_names: list):
        """获取指定日期的最新CP数据（不含返工）"""
        return self.fetcher.get_multi_cp_by_day_latest(day, cp_names)
    
    def get_curves_by_cell_ids(self, cell_ids: List[str], proc: str = 'CAP', step_sequence_no: Optional[List[int]] = None, extend=False,chunk_size: int=500):
        """获取电池曲线数据"""
        return self.fetcher.get_ftp_curves_by_celllist_optimized(cell_ids, proc, step_sequence_no, extend,chunk_size=chunk_size)
    
    def get_container_data(self, cell_id: str, proc: list):
        """获取同容器内的电池数据"""
        return self.fetcher.get_container_extend_by_celllist([cell_id], proc)
    
    def get_defects(self, cell_ids: list):
        """获取电池缺陷数据"""
        return self.fetcher.get_defect_by_celllist(cell_ids)
    
    def get_dynamic_k(self, cell_id: str):
        """获取电池的动态K值"""
        return self.fetcher.get_dynamic_k_by_id(cell_id)
    
    # ========== 数据处理方法 ==========
    def remove_rework_curves(self, data, threshold_hours=3):
        """移除返工曲线数据"""
        return self.processor.remove_rework_curves(data, threshold_hours)
    
    def extend_defect(self, data, defect_keys=[]):
        """扩展数据中的缺陷信息"""
        defect_data = self.get_defects(data.cell_id.values)
        return self.processor.extend_defect(data, defect_keys, defect_data)
    
    def calculate_dqdv(self, df, spec='FOR', step=None, fine_output=False):
        """计算dQ/dV"""
        return self.processor.calculate_dqdv(df, spec, step, fine_output)
    
    # ========== 可视化方法 ==========
    def analyze_cell_cp(self, bad_id, processes=None, save=False, save_path=None, raw=False, show=True):
        """分析电池特征参数"""
        return self.visualizer.analyze_cell_cp(bad_id, processes, save, save_path, raw, show)
    
    def analyze_cell(self, bad_id, processes=None):
        """分析电池曲线"""
        return self.visualizer.analyze_cell(bad_id, processes)
    
    # ========== 数据操作方法 ==========
    def upload_data(self, df, table_name):
        """上传数据到数据库"""
        return self.fetcher.upload_to_doris(df, table_name)
    
    def mark_defect(self, cell_ids, defect_code, wipline_jy=None):
        """标记电池缺陷"""
        return self.fetcher.give_mark_by_cellids(cell_ids, defect_code, wipline_jy)