# data_fetcher.py
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Union, Tuple
from tqdm import tqdm
import os
import datetime
from functools import wraps
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from .database import DatabaseConnection
from .config import FetcherConfig

def exclude_rework(func):
    """装饰器：排除返工数据，保留首次测试结果"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        cp = func(*args, **kwargs)
        sorted_cp = cp.sort_values([i for i in cp.columns if 'out_time' in i]) \
                       .drop_duplicates(subset='cell_id', keep='first')
        return sorted_cp.reset_index(drop=True)
    return wrapper

class DataFetcher:
    """数据获取类，负责从数据库获取各类电池数据"""
    
    def __init__(self, config: FetcherConfig):
        """初始化数据获取器"""
        self.config = config
        self.db_connection = DatabaseConnection(config.database_config)
        
    def _gen_table_names(self, cp_names: List[str]) -> List[str]:
        """生成表名"""
        return [f'DWD_{self.config.table_prefix}_MES_{i.upper()}_CPS' for i in cp_names]
    def translate_cell_id(self, cell_id_list: List[str]) -> pd.DataFrame:
        '''
        beer专用
        '''
        batch_formatted_list = ', '.join(f"'{item}'" for item in cell_id_list)
        sql = f'''
            SELECT *
            FROM jy_gd_dwd.DWD_CYLINDER_CELL_STEEL_NEXUS AS t1
            WHERE t1.cell_id IN ({batch_formatted_list})
        '''     
        columns = self.db_connection.get_multiple_table_columns(['DWD_CYLINDER_CELL_STEEL_NEXUS'])
        res = self.db_connection.execute_query(sql, columns)
        return res
    def get_single_cp_by_celllist_raw(self, 
                                     items: List[str], 
                                     cp_name: List[str], 
                                     chunk_size: int = 8000) -> pd.DataFrame:
        """获取指定电池ID列表的单个CP原始数据（包含返工数据）"""
        table_names = self._gen_table_names(cp_name)
        
        # 分块处理大量电池ID
        chunks = [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]
        dfs = []
        if self.config.table_prefix.upper() == 'CYLINDER':
            for chunk in chunks:
                trans = self.translate_cell_id(chunk)
                batch_formatted_list = ', '.join(f"'{item}'" for item in trans['steel_jellyroll_no'].values)
                
                sql = f'''
                    SELECT *
                    FROM {table_names[0]} AS t1
                    WHERE t1.jellyroll_no IN ({batch_formatted_list})
                    {f"AND t1.wip_line = '{self.config.wip_line}'" if self.config.wip_line else ''}
                '''
                
                columns = self.db_connection.get_multiple_table_columns(table_names)
                batch_df = self.db_connection.execute_query(sql, columns)
                batch_df = batch_df.sort_values(f'{cp_name[0].lower()}_out_time')
                batch_df[f'{cp_name[0].lower()}_rework_num'] = batch_df.groupby('cell_id').cumcount()
                batch_df.rename(columns={'cell_id': 'cell_id_raw'}, inplace=True)
                batch_df = pd.merge(batch_df, trans, left_on=f'{cp_name[0].lower()}_jellyroll_no',right_on='steel_jellyroll_no', how='left').drop(columns=['steel_jellyroll_no','steel_lake_time'])
                dfs.append(batch_df)
        else:
            for chunk in chunks:
                batch_formatted_list = ', '.join(f"'{item}'" for item in chunk)
                
                sql = f'''
                    SELECT *
                    FROM {table_names[0]} AS t1
                    WHERE t1.cell_id IN ({batch_formatted_list})
                    {f"AND t1.wip_line = '{self.config.wip_line}'" if self.config.wip_line else ''}
                '''
                
                columns = self.db_connection.get_multiple_table_columns(table_names)
                batch_df = self.db_connection.execute_query(sql, columns)
                batch_df = batch_df.sort_values(f'{cp_name[0].lower()}_out_time')
                batch_df[f'{cp_name[0].lower()}_rework_num'] = batch_df.groupby('cell_id').cumcount()
                dfs.append(batch_df)
        
        if dfs:
            return pd.concat(dfs, ignore_index=True).reset_index(drop=True)
        else:
            columns = self.db_connection.get_multiple_table_columns(table_names)
            return pd.DataFrame(columns=columns)
    
    def get_multi_cp_by_celllist(self, 
                               items: List[str], 
                               cp_names: List[str]) -> pd.DataFrame:
        """获取指定电池ID列表的多个CP数据，并合并"""
        merged_data = self.get_single_cp_by_celllist_raw(items, [cp_names[0]])
        for cp in cp_names[1:]:
            cp_data = self.get_single_cp_by_celllist_raw(items, [cp])
            merged_data = pd.merge(merged_data, cp_data, on='cell_id', how='outer')
        return merged_data
    def get_mpd_online_ocv(self, 
                            cell_ids: List[str], ) -> pd.DataFrame:
        formatted_list = ', '.join(f"'{item}'" for item in cell_ids)
        
        sql = f'''
            SELECT *
            FROM sy_gd_dwd.DWD_PW_MES_MODULE_ALL_PROCESS_CPS AS t1
            WHERE t1.cell_id IN ({formatted_list})
            AND test_item = 'SY_M7CPT_AR101'
        '''
        columns = self.db_connection.get_multiple_table_columns(['DWD_PW_MES_MODULE_ALL_PROCESS_CPS'])
        batch_df = self.db_connection.execute_query(sql, columns)
        return batch_df
    def get_multi_cp_by_day(self, day: str, cp_names: List[str]) -> pd.DataFrame:
        """获取特定日期的CP数据"""
        table_names = self._gen_table_names(cp_names)
        
        if len(table_names) > 1:
            join_clauses = " \n".join(
                [f"JOIN {table} AS t{i+2} ON t1.cell_id = t{i+2}.cell_id" 
                 for i, table in enumerate(table_names[1:])]
            )
        else:
            join_clauses = ""
        
        sql = f'''
            SELECT *
            FROM {table_names[0]} AS t1
            {join_clauses}
            WHERE CONVERT_TZ(t1.out_time, '+00:00', '+08:00') < '{day} 23:59:59'
                    AND CONVERT_TZ(t1.out_time, '+00:00', '+08:00') >= '{day} 00:00:00'
            {f"AND t1.wip_line = '{self.config.wip_line}'" if self.config.wip_line else ''}
        '''
        
        columns = self.db_connection.get_multiple_table_columns(table_names)
        return self.db_connection.execute_query(sql, columns)
    
    def get_multi_cp_by_day_period(self, 
                                 start_date: str, 
                                 end_date: str, 
                                 cp_names: List[str], 
                                 local_cache: bool = False) -> pd.DataFrame:
        """获取日期范围内的CP数据"""
        table_names = self._gen_table_names(cp_names)
        
        if len(table_names) > 1:
            join_clauses = " \n".join(
                [f"JOIN {table} AS t{i+2} ON t1.cell_id = t{i+2}.cell_id" 
                 for i, table in enumerate(table_names[1:])]
            )
        else:
            join_clauses = ""
        
        base_sql = f'''
            SELECT *
            FROM {table_names[0]} AS t1
            {join_clauses}
            {f"WHERE t1.wip_line = '{self.config.wip_line}'" if self.config.wip_line else 'WHERE 1=1'}
        '''
        
        # 生成日期范围
        date_list = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()
        multiple_data = []
        columns = self.db_connection.get_multiple_table_columns(table_names)
        
        for day in tqdm(date_list):
            try:
                # 添加日期过滤条件
                sql = base_sql + f'''
                    AND t1.out_time <= DATE_SUB('{day} 23:59:59', INTERVAL 8 HOUR)
                    AND t1.out_time >= DATE_SUB('{day} 00:00:00', INTERVAL 8 HOUR)
                '''
                
                single_day_data = self.db_connection.execute_query(sql, columns)
                
                if local_cache:
                    os.makedirs('data', exist_ok=True)
                    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                    single_day_data.to_csv(f"data/{day}_{self.config.base}_{timestamp}.csv")
                
                multiple_data.append(single_day_data)
            except Exception as e:
                print(f"获取{day}数据出错: {e}")
        
        if multiple_data:
            return pd.concat(multiple_data).reset_index(drop=True)
        else:
            return pd.DataFrame(columns=columns)
    
    # @exclude_rework
    def get_cell_module_by_pack_id(self, pack_ids: str) -> pd.DataFrame:
        '''
            获取指定pack_id的cell_id, module_id, module_location, cell_id, cell_location, out_time, product_no, wip_line, medium
        '''
        pack_ids_str = ', '.join([f'"{pack_id}"' for pack_id in pack_ids])
        sql = f'''SELECT DISTINCT a.cell_id as pack_id, b.module_id, b.module_location, b.cell_id as cell_id, b.cell_location, a.out_time, a.product_no, a.wip_line, c.medium
        FROM sy_gd_dwd.DWD_PW_MES_PACK_ALL_PROCESS_CPS a
        LEFT JOIN sy_gd_dwd.DWD_PW_MES_PACK_MODULE_CELL_NEXUS b
        ON a.cell_id = b.pack_id
        LEFT JOIN (
            SELECT p.productno, t01.medium
            FROM sy_ods.ODS_MES_PRODUCT p
            LEFT JOIN sy_ods.ODS_MES_TEXT_TRANSLATION t01
            ON t01.textid = p.textid AND t01.languageid = 2052
        ) AS c
        ON a.product_no = c.productno
        WHERE pack_id IN ({pack_ids_str})
        ORDER BY pack_id, b.module_location, b.cell_location'''
        res = self.db_connection.execute_query(sql, ['pack_id', 'module_id', 'module_location', 'cell_id', 'cell_location', 'out_time', 'product_no', 'wip_line', 'medium'])
        return res
    def get_multi_cp_by_day_latest(self, day: str, cp_names: List[str]) -> pd.DataFrame:
        pass
    #     """获取特定日期的最新CP数据（排除返工）"""
    #     table_names = self._gen_table_names(cp_names)
    #     date_obj = datetime.datetime.strptime(day, '%Y-%m-%d')
    #     new_date_obj = date_obj - datetime.timedelta(days=1)
    #     new_date_str = new_date_obj.strftime('%Y-%m-%d')
        
    #     if len(table_names) > 1:
    #         join_clauses = " \n".join(
    #             [f"JOIN {table} AS t{i+2} ON t1.cell_id = t{i+2}.cell_id" 
    #              for i, table in enumerate(table_names[1:])]
    #         )
    #     else:
    #         join_clauses = ""
        
    #     sql = f'''
    #         SELECT *
    #         FROM {table_names[0]} AS t1
    #         {join_clauses}
    #         WHERE CONVERT_TZ(t1.out_time, '+00:00', '+08:00') < '{day} 09:00:00'
    #                 AND CONVERT_TZ(t1.out_time, '+00:00', '+08:00') >= '{new_date_str} 09:00:00'
    #         {f"AND t1.wip_line = '{self.config.wip_line}'" if self.config.wip_line else ''}
    #     '''
        
    #     columns = self.db_connection.get_multiple_table_columns(table_names)
    #     return self.db_connection.execute_query(sql, columns)
    
    def get_container_extend_by_celllist(self, items: List[str], proc: List[str]) -> pd.DataFrame:
        """获取同容器内的所有电池数据"""
        formatted_list = ', '.join(f"'{item}'" for item in items)
        table_names = self._gen_table_names(proc)

        sql = f'''
            WITH target AS (
                SELECT cell_id, DATE_FORMAT(out_time, '%Y-%m-%d %H') AS out_hour, container
                FROM (
                    SELECT cell_id, out_time, container,
                           ROW_NUMBER() OVER (PARTITION BY cell_id ORDER BY out_time) as rn
                    FROM {table_names[0]} 
                    WHERE cell_id IN ({formatted_list})
                ) subquery
                WHERE rn = 1
            )
            SELECT DISTINCT t.*
            FROM {table_names[0]} t
            JOIN target ON DATE_FORMAT(t.out_time, '%Y-%m-%d %H') = target.out_hour
            AND t.container = target.container
        '''
        
        columns = self.db_connection.get_multiple_table_columns(table_names)
        return self.db_connection.execute_query(sql, columns)
    
    def get_container_extend_by_celllist_raw(self, items: List[str], proc: List[str]) -> pd.DataFrame:
        """获取包含返工信息的托盘数据"""
        formatted_list = ', '.join(f"'{item}'" for item in items)
        table_names = self._gen_table_names(proc)

        sql = f'''
            WITH target AS (
                SELECT 
                    cell_id, 
                    DATE_FORMAT(out_time, '%Y-%m-%d %H') AS out_hour, 
                    container, 
                    rn - 1 AS test_type  -- 首测为0，复测为1，三测为2，以此类推
                FROM (
                    SELECT 
                        cell_id, 
                        out_time, 
                        container,
                        ROW_NUMBER() OVER (PARTITION BY cell_id ORDER BY out_time) AS rn
                    FROM {table_names[0]}
                    WHERE cell_id IN ({formatted_list})
                ) subquery
            )
            SELECT DISTINCT t.*, target.test_type
            FROM {table_names[0]} t
            JOIN target 
            ON DATE_FORMAT(t.out_time, '%Y-%m-%d %H') = target.out_hour
            AND t.container = target.container
        '''
        
        columns = self.db_connection.get_multiple_table_columns(table_names) + [f'{proc[0].lower()}_rework_num']
        result = self.db_connection.execute_query(sql, columns)
        return result.sort_values(f'{proc[0].lower()}_out_time').reset_index(drop=True)
    
    def get_container_extend_by_cellid(self, cell_id: str, proc: List[str]) -> pd.DataFrame:
        """获取特定电池所在容器的所有电池数据"""
        table_names = self._gen_table_names(proc)
        
        sql = f'''
            WITH target AS (
                SELECT DATE_FORMAT(out_time, '%Y-%m-%d %H') AS out_hour, container
                FROM {table_names[0]} 
                WHERE cell_id = '{cell_id}'
                ORDER BY out_hour
                LIMIT 1
            )
            SELECT t.*
            FROM {table_names[0]} t
            JOIN target ON DATE_FORMAT(t.out_time, '%Y-%m-%d %H') = target.out_hour
            AND t.container = target.container
        '''
        
        columns = self.db_connection.get_multiple_table_columns(table_names)
        return self.db_connection.execute_query(sql, columns)
    
    def get_ftp_curves_by_celllist_optimized(self, 
                             items: List[str], 
                             proc: str = 'CAP', 
                             step_sequence_no: Optional[List[int]] = None, 
                             extend: bool = False, 
                             take_10_as_temp: bool = False, 
                             chunk_size: int = 1000,  # 增加默认批量大小
                             parallel: bool = False,
                             max_workers: int = 8,  # 控制最大并行线程数
                             max_retries: int = 3) -> pd.DataFrame:
        """获取电池曲线数据"""
        import time
        from .config import DatabaseConfig
        
        # 如果需要扩展电池列表
        if extend:
            print('扩展容器中的电池...')
            items = self.get_container_extend_by_celllist(items, [proc]).cell_id.tolist()
        
        # 根据基地和产线确定表名
        if self.config.base == 'jy':
            table_name = f"{self.config.base}_ods.ODS_MES_FTP_N1{proc.upper()}01_PRODUCT"
            if self.config.wip_line and 'JYP2' in self.config.wip_line:
                table_name += '_JYP2'
        elif self.config.base == 'sy':
            table_name = f"{self.config.base}_ods.ODS_MES_FTP_LA{proc.upper()}01_PRODUCT"
        elif self.config.base == 'ordos':
            table_name = f"os_datalake.ODS_MES_FTP_LA{proc.upper()}01_PRODUCT"
        elif self.config.table_prefix == 'CYLINDER':
            table_name = f"os_datalake.ODS_MES_FTP_LJ{proc.upper()}01_PRODUCT"
        else:
            raise ValueError(f"不支持的基地: {self.config.base}")
        
        # SQL模板
        sql_template = (
            "SELECT OBJECTNO, DATETIME, STEPSEQUENCENO, SEQUENCENO, "
            "PARAMETERCODE2, PARAMETERCODE3, PARAMETERCODE4, {param_code} "
            "FROM {table} "
            "WHERE OBJECTNO IN ({cell_list})"
        )
        
        # 添加步骤过滤条件
        step_clause = ""
        if step_sequence_no is not None:
            formatted_steps = ', '.join(str(step) for step in step_sequence_no)
            step_clause = f' AND STEPSEQUENCENO IN ({formatted_steps})'
        
        # 参数代码字段
        param_code = 'PARAMETERCODE10' if take_10_as_temp else 'PARAMETERCODE11'
        
        # 结果列名
        columns = ['cell_id', 'datetime', 'step_no', 'sequence_no', 
                'voltage', 'current', 'capacity', 'temperature']
        
        # 分块查询
        chunks = [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]
        results = []
        
        # 带重试机制的查询函数
        def run_query_with_retry(chunk):
            for attempt in range(max_retries):
                try:
                    # 为每个查询创建新的连接配置和连接
                    temp_config_dict = self.config.database_config.to_dict()
                    temp_config_dict['database'] = self.config.base + "_ods"
                    temp_config = DatabaseConfig(**temp_config_dict)
                    
                    # 格式化查询
                    formatted_list = ', '.join(f"'{item}'" for item in chunk)
                    sql = sql_template.format(
                        param_code=param_code,
                        table=table_name,
                        cell_list=formatted_list
                    )
                    sql += step_clause + " ORDER BY DATETIME, OBJECTNO"
                    
                    # 创建新连接并执行查询
                    with DatabaseConnection(temp_config) as temp_db:
                        result = temp_db.execute_query(sql, columns)
                        return result
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"查询尝试 {attempt+1} 失败: {e}")
                        print(f"等待 {2 * (attempt+1)} 秒后重试...")
                        time.sleep(2 * (attempt+1))  # 递增延迟
                    else:
                        print(f"查询失败，已达最大重试次数: {e}")
                        print(f"SQL: {sql}")
                        raise
        
        # 执行单个查询
        def process_chunk(chunk, i, total):
            try:
                result = run_query_with_retry(chunk)
                print(f"完成查询批次 {i}/{total} - 获取到 {len(result)} 行数据")
                return result
            except Exception as e:
                print(f"批次 {i}/{total} 处理失败: {e}")
                # 返回空DataFrame而不是None，保持一致的返回类型
                return pd.DataFrame(columns=columns)
        
        # 并行或顺序执行查询
        if parallel:
            # 限制并发量
            actual_workers = min(max_workers, len(chunks))
            print(f"使用 {actual_workers} 个并行线程处理 {len(chunks)} 个批次...")
            
            with ThreadPoolExecutor(max_workers=actual_workers) as executor:
                # 传递更多上下文信息到进度条
                futures = [
                    executor.submit(process_chunk, chunk, i+1, len(chunks)) 
                    for i, chunk in enumerate(chunks)
                ]
                
                for future in tqdm(as_completed(futures), total=len(futures), desc="执行查询"):
                    try:
                        result = future.result()
                        if not result.empty:
                            results.append(result)
                    except Exception as e:
                        print(f"处理批次时发生未捕获异常: {e}")
        else:
            for i, chunk in enumerate(tqdm(chunks, desc="执行查询")):
                result = process_chunk(chunk, i+1, len(chunks))
                if not result.empty:
                    results.append(result)
        
        # 合并结果
        if results:
            print(f"合并 {len(results)} 个结果集...")
            df_concat = pd.concat(results, ignore_index=True)
            print(f"总计获取到 {len(df_concat)} 行数据")
            # 排序数据
            return df_concat.sort_values(['cell_id', 'datetime', 'sequence_no']).reset_index(drop=True)
        else:
            print("未获取到任何数据")
            return pd.DataFrame(columns=columns)
    
    # def get_ftp_curves_by_celllist(self, 
    #                              items: List[str], 
    #                              proc: str = 'CAP', 
    #                              step_sequence_no: Optional[List[int]] = None, 
    #                              extend: bool = False, 
    #                              take_10_as_temp: bool = False, 
    #                              chunk_size: int = 36, 
    #                              parallel: bool = False) -> pd.DataFrame:
    #     """获取电池曲线数据"""
    #     # 如果需要扩展电池列表
    #     if extend:
    #         print('扩展容器中的电池...')
    #         items = self.get_container_extend_by_celllist(items, proc).cell_id.tolist()
        
    #     # 根据基地和产线确定表名
    #     if self.config.base == 'jy':
    #         table_name = f"{self.config.base}_ods.ODS_MES_FTP_N1{proc.upper()}01_PRODUCT"
    #         if self.config.wip_line and 'JYP2' in self.config.wip_line:
    #             table_name += '_JYP2'
    #     elif self.config.base == 'sy':
    #         table_name = f"{self.config.base}_ods.ODS_MES_FTP_LA{proc.upper()}01_PRODUCT"
    #     elif self.config.base == 'ordos':
    #         table_name = f"os_datalake.ODS_MES_FTP_LA{proc.upper()}01_PRODUCT"
    #     else:
    #         raise ValueError(f"不支持的基地: {self.config.base}")
        
    #     # SQL模板
    #     sql_template = (
    #         "SELECT OBJECTNO, DATETIME, STEPSEQUENCENO, SEQUENCENO, "
    #         "PARAMETERCODE2, PARAMETERCODE3, PARAMETERCODE4, {param_code} "
    #         "FROM {table} "
    #         "WHERE OBJECTNO IN ({cell_list})"
    #     )
        
    #     # 添加步骤过滤条件
    #     step_clause = ""
    #     if step_sequence_no is not None:
    #         formatted_steps = ', '.join(str(step) for step in step_sequence_no)
    #         step_clause = f' AND STEPSEQUENCENO IN ({formatted_steps})'
        
    #     # 参数代码字段
    #     param_code = 'PARAMETERCODE10' if take_10_as_temp else 'PARAMETERCODE11'
        
    #     # 结果列名
    #     columns = ['cell_id', 'datetime', 'step_no', 'sequence_no', 
    #               'voltage', 'current', 'capacity', 'temperature']
        
    #     # 分块查询
    #     chunks = [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]
    #     results = []
        
    #     # 执行单个查询
    #     def run_query(chunk):
    #         formatted_list = ', '.join(f"'{item}'" for item in chunk)
    #         sql = sql_template.format(
    #             param_code=param_code,
    #             table=table_name,
    #             cell_list=formatted_list
    #         )
    #         sql += step_clause + " ORDER BY DATETIME"
            
    #         # 使用临时配置执行查询
    #         from config import DatabaseConfig
    #         temp_config_dict = self.config.database_config.to_dict()
    #         temp_config_dict['database'] = self.config.base + "_ods"
    #         temp_config = DatabaseConfig(**temp_config_dict)  # Create a DatabaseConfig object
    #         temp_db = DatabaseConnection(temp_config)
    #         return temp_db.execute_query(sql, columns)
        
    #     # 并行或顺序执行查询
    #     if parallel:
    #         with ThreadPoolExecutor() as executor:
    #             futures = [executor.submit(run_query, chunk) for chunk in chunks]
    #             for future in tqdm(as_completed(futures), total=len(futures), desc="执行查询"):
    #                 results.append(future.result())
    #     else:
    #         for chunk in tqdm(chunks, desc="执行查询"):
    #             results.append(run_query(chunk))
        
    #     # 合并结果
    #     if results:
    #         df_concat = pd.concat(results, ignore_index=True)
    #         return df_concat.sort_values(['cell_id', 'datetime', 'sequence_no']).reset_index(drop=True)
    #     else:
    #         return pd.DataFrame(columns=columns)
    
    def get_cps_by_cell_operation_test_step(self, 
                                         cell_id: List[str], 
                                         operation_codes: Optional[List[str]] = None,
                                         test_items: Optional[List[str]] = None,
                                         steps: Optional[List[str]] = None) -> pd.DataFrame:
        """根据操作码、测试项和步骤获取电池数据"""
        formatted_list = ', '.join(f"'{item}'" for item in cell_id)
        database_name = f"DWD_{'PS' if self.config.table_prefix == 'POUCH' else 'PW'}_MES_CELL_ALL_PROCESS_CPS"
        
        if self.config.base == 'jy':
            database_name += f"_JYP{'2' if 'JYP2' in self.config.wip_line else '1'}"
        
        sql = f'''
        SELECT * 
        FROM {database_name}
        WHERE cell_id in ({formatted_list})
        '''
        
        if operation_codes:
            sql += f'''
                    AND operation_code IN ({', '.join(f"'{item.upper()}'" for item in operation_codes)})
                    '''
        if test_items:
            sql += f'''
                    AND test_item IN ({ ', '.join(f"'{item}'" for item in test_items)})
            '''
        if steps:
            sql += f'''
                    AND step_no IN ({', '.join(f"'{item}'" for item in steps)})
                    '''
        
        # 获取列信息
        columns = self.db_connection.get_single_column(database_name, True)
        return self.db_connection.execute_query(sql, columns)
    def get_cps_by_cell_operation_test_step_module(self, 
                                                cell_id: List[str],
                                                operation_codes: Optional[List[str]] = None,
                                                test_items: Optional[List[str]] = None,
                                                steps: Optional[List[str]] = None) -> pd.DataFrame:
        """获取模块级别的电池数据（采用批量查询，避免 IN 子句超过数据库限制）"""
        # 构造目标数据库名称
        database_name = f"DWD_{'PS' if self.config.table_prefix == 'POUCH' else 'PW'}_MES_MODULE_ALL_PROCESS_CPS"
        if self.config.base == 'jy' and self.config.wip_line is not None:
            database_name += f"{'_JYP2' if 'JYP2' in self.config.wip_line else 'JYP1'}"

        # 定义每个批次的大小，确保不会超过数据库对于子表达式的限制（这里设为5000）
        batch_size = 5000
        result_dfs = []
        # 获取表中所有字段名称
        columns = self.db_connection.get_table_columns(database_name, True)

        # 针对 cell_id 列表进行分批查询
        for i in range(0, len(cell_id), batch_size):
            batch_ids = cell_id[i:i+batch_size]
            formatted_list = ', '.join(f"'{item}'" for item in batch_ids)
            sql = f'''
            SELECT * 
            FROM {database_name}
            WHERE cell_id IN ({formatted_list})
            '''
            
            # 对 operation_codes 添加查询条件（如果传入了）
            if operation_codes:
                formatted_ops = ', '.join(f"'{item.upper()}'" for item in operation_codes)
                sql += f'''
                        AND operation_code IN ({formatted_ops})
                        '''
            # 对 test_items 添加查询条件（如果传入了）
            if test_items:
                formatted_tests = ', '.join(f"'{item}'" for item in test_items)
                sql += f'''
                        AND test_item IN ({formatted_tests})
                        '''
            # 对 steps 添加查询条件（如果传入了）
            if steps:
                formatted_steps = ', '.join(f"'{item}'" for item in steps)
                sql += f'''
                        AND step_no IN ({formatted_steps})
                        '''
            
            # 执行查询并将结果添加到列表中
            batch_df = self.db_connection.execute_query(sql, columns)
            result_dfs.append(batch_df)
        
        # 将所有批次的结果合并成一个 DataFrame 返回
        if result_dfs:
            combined_df = pd.concat(result_dfs, axis=0, ignore_index=True)
        else:
            combined_df = pd.DataFrame(columns=columns)
        
        return combined_df
    # def get_cps_by_cell_operation_test_step_module(self, 
    #                                            cell_id: List[str],
    #                                            operation_codes: Optional[List[str]] = None,
    #                                            test_items: Optional[List[str]] = None,
    #                                            steps: Optional[List[str]] = None) -> pd.DataFrame:
    #     """获取模块级别的电池数据"""
    #     formatted_list = ', '.join(f"'{item}'" for item in cell_id)
    #     database_name = f"DWD_{'PS' if self.config.table_prefix == 'POUCH' else 'PW'}_MES_MODULE_ALL_PROCESS_CPS"
        
    #     if self.config.base == 'jy' and self.config.wip_line is not None:
    #         database_name += f"{'_JYP2' if 'JYP2' in self.config.wip_line else 'JYP1'}"
        
    #     sql = f'''
    #     SELECT * 
    #     FROM {database_name}
    #     WHERE cell_id in ({formatted_list})
    #     '''
        
    #     if operation_codes:
    #         sql += f'''
    #                 AND operation_code IN ({', '.join(f"'{item.upper()}'" for item in operation_codes)})
    #                 '''
    #     if test_items:
    #         sql += f'''
    #                 AND test_item IN ({ ', '.join(f"'{item}'" for item in test_items)})
    #         '''
    #     if steps:
    #         sql += f'''
    #                 AND step_no IN ({', '.join(f"'{item}'" for item in steps)})
    #                 '''
        
    #     columns = self.db_connection.get_table_columns(database_name, True)
    #     return self.db_connection.execute_query(sql, columns)
    
    def get_cps_by_operation_test_step_day_period(self,
                                              start_date: str,
                                              end_date: str,
                                              operation_codes: Optional[List[str]] = None,
                                              test_items: Optional[List[str]] = None,
                                              steps: Optional[List[str]] = None,
                                              local_cache: Optional[bool] = None) -> pd.DataFrame:
        """获取日期范围内的按操作码、测试项和步骤过滤的数据"""
        database_name = f"DWD_{'PS' if self.config.table_prefix == 'POUCH' else 'PW'}_MES_CELL_ALL_PROCESS_CPS"
        
        if self.config.base == 'jy' and self.config.wip_line is not None:
            database_name += f"{'_JYP2' if 'JYP2' in self.config.wip_line else 'JYP1'}"
        
        sql = f'''
        SELECT * 
        FROM {database_name} as t1
        {f"WHERE t1.wip_line = '{self.config.wip_line}'" if self.config.wip_line else 'WHERE 1=1'}
        '''
        
        if operation_codes:
            sql += f'''
                    AND operation_code IN ({', '.join(f"'{item.upper()}'" for item in operation_codes)})
                    '''
        if test_items:
            sql += f'''
                    AND test_item IN ({ ', '.join(f"'{item}'" for item in test_items)})
            '''
        if steps:
            sql += f'''
                    AND step_no IN ({', '.join(f"'{item}'" for item in steps)})
                    '''
        
        # 获取列信息
        columns = self.db_connection.get_single_column(database_name, True)
        
        # 生成日期范围并查询
        date_list = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()
        multiple_data = []
        
        for day in tqdm(date_list):
            try:
                day_sql = sql + f'''
                    AND t1.out_time <= DATE_SUB('{day} 23:59:59', INTERVAL 8 HOUR)
                    AND t1.out_time >= DATE_SUB('{day} 00:00:00', INTERVAL 8 HOUR)
                '''
                
                single_day_data = self.db_connection.execute_query(day_sql, columns)
                
                if local_cache:
                    os.makedirs('data', exist_ok=True)
                    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                    single_day_data.to_csv(f"data/{day}_{self.config.base}_{timestamp}.csv")
                
                multiple_data.append(single_day_data)
            except Exception as e:
                print(f"获取{day}数据出错: {e}")
        
        if multiple_data:
            return pd.concat(multiple_data).reset_index(drop=True)
        else:
            return pd.DataFrame(columns=columns)
    
    def get_defect_by_celllist(self, items: List[str], batch_size: int = 8000) -> pd.DataFrame:
        """获取电池列表的缺陷数据"""
        # 确定数据库
        if self.config.base == 'ordos':
            db = 'os_datalake'
        elif self.config.base == 'jy':
            db = 'jy2_ods' if 'JYP2' in self.config.wip_line else 'jy_ods'
        elif self.config.base == 'sy':
            db = 'sy_ods'
        else:
            raise ValueError(f"不支持的基地: {self.config.base}")
        
        # 分批处理
        result_frames = []
        chunks = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
        
        from .config import DatabaseConfig  # 导入 DatabaseConfig
        
        for chunk in tqdm(chunks, desc="获取缺陷数据"):
            formatted_list = ', '.join(f"'{item}'" for item in chunk)
            sql = f'''
                    SELECT * 
                    FROM {db}.ODS_MES_QUALITY_DEFECT AS t1
                    JOIN {db}.ODS_MES_BAT_QUALITY_DEFECT AS t2 
                    ON t1.ID = t2.QUALITYDEFECTID 
                    WHERE t1.SERIALNO IN ({formatted_list}) 
            '''
            
            # 创建临时数据库连接，使用 with 语句确保连接正确关闭
            temp_config = self.config.database_config.to_dict()
            temp_config['database'] = db
            # 将字典转换为 DatabaseConfig 对象
            temp_db_config = DatabaseConfig(**temp_config)
            with DatabaseConnection(temp_db_config) as temp_db:
                # 获取列信息并执行查询
                columns1 = temp_db.get_table_columns('ODS_MES_QUALITY_DEFECT', True)
                columns2 = temp_db.get_table_columns('ODS_MES_BAT_QUALITY_DEFECT', True)
                
                batch_result = temp_db.execute_query(sql, columns1 + columns2)
                result_frames.append(batch_result)
        
        if result_frames:
            return pd.concat(result_frames, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def get_defect_by_code(self, items: List[str], batch_size: int = 3000) -> pd.DataFrame:
        """根据缺陷代码获取缺陷数据"""
        # 确定数据库
        if self.config.base == 'ordos':
            db = 'os_datalake'
        elif self.config.base == 'jy':
            db = 'jy2_ods' if 'JYP2' in self.config.wip_line else 'jy_ods'
        elif self.config.base == 'sy':
            db = 'sy_ods'
        else:
            raise ValueError(f"不支持的基地: {self.config.base}")
        
        # 分批处理
        result_frames = []
        chunks = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
        
        for chunk in tqdm(chunks, desc="获取缺陷数据"):
            formatted_list = ', '.join(f"'{item}'" for item in chunk)
            sql = f'''
                    SELECT * 
                    FROM {db}.ODS_MES_QUALITY_DEFECT AS t1
                    JOIN {db}.ODS_MES_BAT_QUALITY_DEFECT AS t2 
                    ON t1.ID = t2.QUALITYDEFECTID 
                    WHERE t1.DEFECTREASONCODE IN ({formatted_list}) 
            '''
            
            # 创建临时数据库连接
            temp_config = self.config.database_config.to_dict()
            temp_config['database'] = db
            temp_db = DatabaseConnection(temp_config)
            
            # 获取列信息并执行查询
            columns1 = temp_db.get_table_columns('ODS_MES_QUALITY_DEFECT', True)
            columns2 = temp_db.get_table_columns('ODS_MES_BAT_QUALITY_DEFECT', True)
            
            batch_result = temp_db.execute_query(sql, columns1 + columns2)
            result_frames.append(batch_result)
        
        if result_frames:
            return pd.concat(result_frames, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def get_dynamic_k_by_hour(self, start: str, end: str) -> pd.DataFrame:
        """按小时获取动态K值数据"""
        # 创建临时配置
        config_with_new_db = self.config.database_config.to_dict()
        
        if self.config.base == 'ordos':
            config_with_new_db['database'] = 'ordos_gd_dws'
        elif self.config.base == 'sy':
            config_with_new_db['database'] = 'sy_gd_dws'
        else:
            raise ValueError(f"不支持的基地: {self.config.base}")
        
        sql = f'''
            SELECT * FROM {config_with_new_db['database']}.DWS_PW_MES_DYNAMIC_K_RL
            WHERE CONVERT_TZ(ads_out_time, '+00:00', '+08:00') < '{end}'
                    AND CONVERT_TZ(ads_out_time, '+00:00', '+08:00') >= '{start}'
        '''
        
        # 创建临时数据库连接
        temp_db = DatabaseConnection(config_with_new_db)
        columns = temp_db.get_table_columns('DWS_PW_MES_DYNAMIC_K_RL', True)
        
        return temp_db.execute_query(sql, columns)
    
    def get_dynamic_k_by_id(self, cell_id: str) -> pd.DataFrame:
        """按ID获取动态K值数据"""
        # 创建临时配置
        config_with_new_db = self.config.database_config.to_dict()
        
        if self.config.base == 'ordos':
            config_with_new_db['database'] = 'ordos_gd_dws'
        elif self.config.base == 'sy':
            config_with_new_db['database'] = 'sy_gd_dws'
        else:
            raise ValueError(f"不支持的基地: {self.config.base}")
        
        sql = f'''
            SELECT * FROM {config_with_new_db['database']}.DWS_PW_MES_DYNAMIC_K_RL
            WHERE cell_id = '{cell_id}'
        '''
        
        # 创建临时数据库连接
        temp_db = DatabaseConnection(config_with_new_db)
        columns = temp_db.get_table_columns('DWS_PW_MES_DYNAMIC_K_RL', True)
        
        return temp_db.execute_query(sql, columns)
    
    def upload_to_doris(self, df: pd.DataFrame, table_name: str) -> bool:
        """上传数据到Doris数据库"""
        from sqlalchemy import create_engine
        
        try:
            # 创建引擎
            engine = create_engine(
                f"mysql+pymysql://{self.config.database_config.user}:{self.config.database_config.password}@"
                f"{self.config.database_config.host}:{self.config.database_config.port}/{self.config.base}_gd_ads?charset=utf8"
            )
            
            # 添加更新时间
            df['update_time'] = datetime.datetime.now()
            
            # 获取列信息
            config_with_new_db = self.config.database_config.to_dict()
            config_with_new_db['database'] = f'{self.config.base}_gd_ads'
            temp_db = DatabaseConnection(config_with_new_db)
            columns = temp_db.get_table_columns(table_name, True)
            
            print('上传数据中...')
            df[columns].to_sql(name=table_name, con=engine, if_exists='append', index=False)
            print('上传成功!')
            return True
            
        except Exception as e:
            print(f'上传失败: {e}')
            return False
    
    def give_mark_by_cellids(self, cell_ids: Union[str, List[str]], defectcode: str, wipline_jy: Optional[str] = None) -> bool:
        """标记电池缺陷"""
        # 确定API地址
        if self.config.base == 'jy':
            if wipline_jy is None:
                raise ValueError("jy基地必须提供wipline_jy参数")
            
            if wipline_jy == 'JYP1':
                ip = '10.202.12.43'
            elif wipline_jy == 'JYP2':
                ip = '10.210.91.202'
            else:
                raise ValueError(f"不支持的产线: {wipline_jy}")
                
        elif self.config.base == 'sy':
            ip = '10.206.134.80'
        elif self.config.base == 'ordos':
            ip = '10.205.129.13'
        elif self.config.base == 'cz':
            ip = '10.209.82.122'
        else:
            raise ValueError(f"不支持的基地: {self.config.base}")
        
        # 确保cell_ids是列表
        if isinstance(cell_ids, str):
            cell_ids = [cell_ids]
        
        # 调用API标记缺陷
        url = f"http://{ip}/Apriso/HttpServices/api/extensions/1/Cell/BatchAddDefectCodeForJson?producttype=C"
        
        success = True
        for cell_id in cell_ids:
            data = [{"serialno": cell_id, "defectcode": defectcode, "operationcode": "", "employeeno": "james"}]
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                print(f'{cell_id} 标记成功')
            else:
                print(f'{cell_id} 标记失败')
                success = False
        
        return success
    
    def make_sql(self, sql: str, table_names: Optional[List[str]] = None) -> pd.DataFrame:
        """执行自定义SQL查询"""
        columns = None
        if table_names:
            columns = []
            for table in table_names:
                columns.extend(self.db_connection.get_table_columns(table, True))
        
        return self.db_connection.execute_query(sql, columns)
    # def get_long_k_by_cellids(self, cell_ids: List[str]) -> pd.DataFrame:
    #     """获取电池的长K值"""
    #     if self.config.base == 'ordos':
    #         test_items = 'LONG_K'

    #     elif self.config.base == 'sy':
    #         pass
    #     elif self.config.base == 'jy':
    #         if self.config.wip_line == 'JYP1':
    #             test_items = ['JY_M5CPT_AR003','JY_M5CPT_AR501']
    #         elif self.config.wip_line == 'JYP2':
    #             test_items = ['JY_M5CPT_AR003','JY_M5CPT_AR501']
    #         else:
    #             raise ValueError(f"不支持的产线: {self.config.wip_line}")
            
    #     else:
    #         raise ValueError(f"不支持的基地: {self.config.base}")
        
    #     # raw_df = self.get_cps_by_cell_operation_test_step_module(cell_ids,test_items=)
    #     pass
    def get_long_k_by_cellids(self, cell_ids: List[str]) -> pd.DataFrame:
        """获取电池的长K值"""
        pass
        # if self.config.base == 'ordos':
        #     test_item = 'LONG_K'

        # elif self.config.base == 'sy':
        #     config_with_new_db['database'] = 'sy_gd_dws'
        # elif self.config.base == 'jy':
        #     config_with_new_db['database'] = 'sy_gd_dws'
        # else:
        #     raise ValueError(f"不支持的基地: {self.config.base}")
        # formatted_list = ', '.join(f"'{item}'" for item in cell_ids)
        # sql = f'''
        #     SELECT * FROM {self.config.base}_ods.ODS_MES_LONG_K
        #     WHERE cell_id IN ({formatted_list})
        # '''
        
        # columns = self.db_connection.get_table_columns('ODS_MES_LONG_K', True)
        # return self.db_connection.execute_query(sql, columns)