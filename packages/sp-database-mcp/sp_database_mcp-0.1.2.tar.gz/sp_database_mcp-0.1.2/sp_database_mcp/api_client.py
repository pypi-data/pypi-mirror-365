"""API 客户端模块 - 用于通过 API 获取数据库信息"""

import os
from typing import List, Optional, Dict, Any
import httpx
from .models import TableInfo, ColumnInfo


class APIClient:
    """API 客户端，用于从远程 API 获取数据库表结构信息"""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        self.base_url = base_url or os.getenv("API_BASE_URL")
        self.token = token or os.getenv("API_TOKEN")

        if not self.base_url:
            raise ValueError("API_BASE_URL is required")

        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "SP-Database-MCP/0.1.0",
        }

        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def get_table_info(self, table_name: str) -> Optional[TableInfo]:
        """通过 API 获取指定表的结构信息"""
        # 首先尝试通过低代码系统的 schema API 获取信息
        schema_info = await self._get_table_info_from_schema_api(table_name)
        if schema_info:
            return schema_info
        
        # 如果低代码系统 API 查询失败，回退到传统的 API
        return await self._get_table_info_from_traditional_api(table_name)
    
    async def _get_table_info_from_schema_api(self, table_name: str) -> Optional[TableInfo]:
        """通过低代码系统的 schema API 获取表信息"""
        try:
            async with httpx.AsyncClient() as client:
                # 查询实体基本信息
                entity_response = await client.get(
                    f"{self.base_url}/api/schema/entity/{table_name}",
                    headers=self.headers,
                    timeout=30.0,
                )
                
                if entity_response.status_code != 200:
                    return None
                
                entity_data = entity_response.json()
                if not entity_data or not entity_data.get('data'):
                    return None
                
                entity = entity_data['data']
                entity_id = entity.get('id')
                entity_name = entity.get('name', table_name)
                entity_description = entity.get('description', '')
                
                # 查询字段信息
                attrs_response = await client.get(
                    f"{self.base_url}/api/schema/entity/{entity_id}/attributes",
                    headers=self.headers,
                    timeout=30.0,
                )
                
                if attrs_response.status_code != 200:
                    return None
                
                attrs_data = attrs_response.json()
                attributes = attrs_data.get('data', [])
                
                columns = []
                foreign_keys = []
                
                for attr in attributes:
                    # 解析字段信息
                    column_info = ColumnInfo(
                        name=attr.get('column_name') or attr.get('code'),
                        type=attr.get('data_type', 'string'),
                        nullable=not bool(attr.get('required', False)),
                        default=attr.get('default_value'),
                        comment=f"{attr.get('name', '')} ({attr.get('code', '')})" + 
                               (f" - {attr.get('description', '')}" if attr.get('description') else ""),
                        is_primary_key=bool(attr.get('primary_key', False)),
                        max_length=attr.get('data_length')
                    )
                    columns.append(column_info)
                    
                    # 处理外键关系
                    if attr.get('ref_entity_id') and attr.get('ref_type') == 'foreign_key':
                        # 查询引用的实体信息
                        ref_entity_response = await client.get(
                            f"{self.base_url}/api/schema/entity/by-id/{attr['ref_entity_id']}",
                            headers=self.headers,
                            timeout=30.0,
                        )
                        
                        if ref_entity_response.status_code == 200:
                            ref_entity_data = ref_entity_response.json()
                            ref_entity = ref_entity_data.get('data', {})
                            if ref_entity.get('table_name'):
                                foreign_keys.append({
                                    "column": attr.get('column_name') or attr.get('code'),
                                    "referenced_table": ref_entity['table_name'],
                                    "referenced_column": "id"
                                })
                
                return TableInfo(
                    name=table_name,
                    comment=f"{entity_name} - {entity_description}" if entity_description else entity_name,
                    columns=columns,
                    indexes=[],  # 低代码系统中索引信息通常不通过 API 提供
                    foreign_keys=foreign_keys
                )
                
        except httpx.RequestError as e:
            print(f"Schema API request error: {e}")
            return None
    
    async def _get_table_info_from_traditional_api(self, table_name: str) -> Optional[TableInfo]:
        """通过传统 API 获取表信息"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/database/tables/{table_name}",
                    headers=self.headers,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_table_info(data)
                else:
                    print(
                        f"Traditional API request failed: {response.status_code} - {response.text}"
                    )
                    return None

        except httpx.RequestError as e:
            print(f"Traditional API request error: {e}")
            return None

    async def get_all_tables(self) -> List[str]:
        """通过 API 获取所有表名"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/database/tables",
                    headers=self.headers,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "tables" in data:
                        return data["tables"]
                    elif isinstance(data, list):
                        return data
                    else:
                        return []
                else:
                    print(
                        f"API request failed: {response.status_code} - {response.text}"
                    )
                    return []

        except httpx.RequestError as e:
            print(f"API request error: {e}")
            return []

    async def search_tables(self, keyword: str) -> List[TableInfo]:
        """通过 API 搜索表"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/database/tables/search",
                    params={"q": keyword},
                    headers=self.headers,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    tables = []

                    if isinstance(data, dict) and "tables" in data:
                        table_list = data["tables"]
                    elif isinstance(data, list):
                        table_list = data
                    else:
                        return []

                    for table_data in table_list:
                        table_info = self._parse_table_info(table_data)
                        if table_info:
                            tables.append(table_info)

                    return tables
                else:
                    print(
                        f"API request failed: {response.status_code} - {response.text}"
                    )
                    return []

        except httpx.RequestError as e:
            print(f"API request error: {e}")
            return []

    def _parse_table_info(self, data: Dict[str, Any]) -> Optional[TableInfo]:
        """解析 API 返回的表信息数据"""
        try:
            if not isinstance(data, dict):
                return None

            table_name = data.get("name") or data.get("table_name")
            if not table_name:
                return None

            columns = []
            columns_data = data.get("columns", [])

            for col_data in columns_data:
                if not isinstance(col_data, dict):
                    continue

                column = ColumnInfo(
                    name=col_data.get("name", ""),
                    type=col_data.get("type", ""),
                    nullable=col_data.get("nullable", True),
                    default=col_data.get("default"),
                    comment=col_data.get("comment"),
                    is_primary_key=col_data.get("is_primary_key", False),
                    is_foreign_key=col_data.get("is_foreign_key", False),
                    max_length=col_data.get("max_length"),
                )
                columns.append(column)

            return TableInfo(
                name=table_name,
                comment=data.get("comment"),
                columns=columns,
                indexes=data.get("indexes", []),
                foreign_keys=data.get("foreign_keys", []),
            )

        except Exception as e:
            print(f"Error parsing table info: {e}")
            return None

    async def get_table_documentation(self, table_name: str) -> Optional[str]:
        """获取表的文档说明"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/database/tables/{table_name}/docs",
                    headers=self.headers,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("documentation", "")
                else:
                    return None

        except httpx.RequestError as e:
            print(f"API request error: {e}")
            return None
