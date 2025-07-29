import pymysql
import pandas as pd
from typing import Optional, List
import datetime
from .config import DatabaseConfig

class DatabaseConnection:
    """Manages database connections and query execution."""
    
    def __init__(self, config: DatabaseConfig):
            """
            初始化数据库连接
            
            参数:
                config: 数据库配置对象
            """
            self.config = config
            self._connection = None
    
    def __enter__(self):
        """作为上下文管理器入口点"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """作为上下文管理器出口点，确保连接关闭"""
        self.close()
    
    def connect(self) -> None:
        """创建数据库连接"""
        if self._connection is None or not self._connection.open:
            try:
                self._connection = pymysql.connect(
                    host=self.config.host,
                    port=self.config.port,
                    user=self.config.user,
                    password=self.config.password,
                    database=self.config.database,
                    charset=self.config.charset,
                    connect_timeout=60,      # 增加连接超时
                    read_timeout=7200,       # 增加读取超时，适应大查询
                    write_timeout=3600
                )
            except Exception as e:
                print(f"数据库连接失败: {e}")
                print(f"连接参数: {self.config}")
                raise
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self._connection and self._connection.open:
            try:
                self._connection.close()
            except Exception as e:
                print(f"关闭连接时发生错误: {e}")
            finally:
                self._connection = None
    
    def execute_query(self, sql: str, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """执行SQL查询并返回DataFrame结果"""
        self.connect()
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                
                if columns:
                    df = pd.DataFrame(result, columns=columns)
                    df = self._process_dates(df)
                else:
                    df = pd.DataFrame(result)
                    
                # 移除重复列
                return df.loc[:, ~df.columns.duplicated()]
        except Exception as e:
            print(f"查询执行错误: {e}")
            print(f"SQL: {sql}")
            raise
    
    def get_table_columns(self, table_name: str, original: bool = False) -> List[str]:
        """Get column names for a table."""
        sql = f"DESC {table_name}"
        self.connect()
        with self._connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        
        columns = [i[0] for i in result]
        
        if not original and "_" in table_name:
            # Add prefix based on table name
            flag = table_name.split('_')[-2].lower()
            return [f"{flag}_{col}" if col != 'cell_id' else col for col in columns]
        return columns
    
    def get_multiple_table_columns(self, table_names: List[str], original: bool = False) -> List[str]:
        """Get column names for multiple tables."""
        all_columns = []
        for table in table_names:
            all_columns.extend(self.get_table_columns(table, original))
        return all_columns
    
    def _process_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process date columns in a DataFrame."""
        for col in df.columns:
            if 'in_time' in col or 'out_time' in col:
                df[col] = pd.to_datetime(df[col]).dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai').dt.tz_localize(None)
                df[f'{col}_h'] = df[col].dt.floor('h')
                df[f'{col}_day'] = df[col].dt.floor('D')
        return df