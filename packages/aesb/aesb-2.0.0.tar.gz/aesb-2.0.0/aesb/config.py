from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class DatabaseConfig:
    """Configuration for database connection."""
    host: str
    port: int = 9030
    user: str = "flink_user"
    password: str = "Flinsql_39u1"
    database: str = ""
    charset: str = "utf8"
    
    @classmethod
    def from_base(cls, base: str, database_suffix: str = "gd_dwd") -> "DatabaseConfig":
        """Create database configuration based on the base location."""
        hosts = {
            "jy": "10.210.94.122", 
            "ordos": "10.205.128.109", 
            "sy": "10.206.121.39"
        }
        
        if base not in hosts:
            raise ValueError(f"Unsupported base: {base}. Supported: {list(hosts.keys())}")
        
        return cls(
            host=hosts[base],
            database=f"{base}_{database_suffix}"
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for pymysql."""
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "charset": self.charset
        }

@dataclass
class FetcherConfig:
    """Configuration for data fetching."""
    base: str
    wip_line: Optional[str] = None
    table_prefix: str = "POUCH"
    
    @property
    def database_config(self) -> DatabaseConfig:
        """Get the database configuration for this fetcher."""
        return DatabaseConfig.from_base(self.base)