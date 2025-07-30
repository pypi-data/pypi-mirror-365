"""数据模型定义"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ColumnInfo(BaseModel):
    """数据库列信息"""

    name: str
    type: str
    code: str
    nullable: bool
    default: Optional[str] = None
    comment: Optional[str] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    max_length: Optional[int] = None
    modifier: Optional[str] = None
    is_system: bool = False


class TableInfo(BaseModel):
    """数据库表信息"""

    name: str
    comment: Optional[str] = None
    columns: List[ColumnInfo]
    indexes: List[Dict[str, Any]] = []
    foreign_keys: List[Dict[str, Any]] = []


class DatabaseSchema(BaseModel):
    """数据库架构信息"""

    database_name: str
    tables: List[TableInfo]


class APIResponse(BaseModel):
    """API 响应模型"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None
