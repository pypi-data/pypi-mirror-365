"""数据库连接和查询模块"""

import os
from typing import List, Optional

from sqlalchemy import MetaData, Table, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from .models import ColumnInfo, DatabaseSchema, TableInfo


class DatabaseClient:
    """数据库客户端"""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL is required")

        self.engine: Optional[Engine] = None
        self._connect()

    def _connect(self):
        """建立数据库连接"""
        try:
            self.engine = create_engine(self.database_url)
            # 测试连接
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def get_table_info(self, table_name: str) -> Optional[TableInfo]:
        """获取指定表的结构信息"""
        if not self.engine:
            return None

        # 首先尝试通过低代码系统的 schema 表获取信息
        schema_info = self._get_table_info_from_schema(table_name)
        if schema_info:
            return schema_info

        # 如果低代码系统查询失败，回退到传统的数据库元数据查询
        return self._get_table_info_from_metadata(table_name)

    def _get_table_info_from_schema(self, table_name: str) -> Optional[TableInfo]:
        """通过低代码系统的 schema 表获取表信息"""
        try:
            with self.engine.connect() as conn:
                # 查询实体基本信息
                entity_query = text("""
                    SELECT id, name, code, table_name, data_type, table_type, 
                           status, created_at, updated_at, owners, description
                    FROM da_logic_entity 
                    WHERE code = :table_code
                """)
                entity_result = conn.execute(
                    entity_query, {"table_code": table_name}
                ).fetchone()

                if not entity_result:
                    return None

                entity_id = entity_result[0]
                entity_name = entity_result[1]
                entity_description = (
                    entity_result[10] if len(entity_result) > 10 else None
                )

                # 查询字段信息
                attr_query = text("""
                    SELECT name, code, column_name, data_type, data_length, data_scale,
                           primary_key, is_unique, required, default_value, description,
                           ref_entity_id, ref_attr_id, ref_type, is_editable, status, 
                           created_at, updated_at, created_by, updated_by, is_system
                    FROM da_entity_attribute 
                    WHERE entity_id = :entity_id
                    ORDER BY id
                """)
                attr_results = conn.execute(
                    attr_query, {"entity_id": entity_id}
                ).fetchall()

                columns = []
                for attr in attr_results:
                    # 解析数据类型
                    data_type = attr[3] or "string"
                    max_length = attr[4] if attr[4] else None

                    column_info = ColumnInfo(
                        name=attr[0],
                        type=data_type,
                        code=attr[1],
                        modifier=attr[19],
                        nullable=not bool(attr[8]),  # required 字段取反
                        default=attr[9],  # default_value
                        is_system=bool(attr[20]),
                        comment=f"{attr[0]} ({attr[1]})"
                        + (
                            f" - {attr[10]}" if attr[10] else ""
                        ),  # name (code) - description
                        is_primary_key=bool(attr[6]),  # primary_key
                        max_length=max_length,
                    )
                    columns.append(column_info)

                # 构建外键信息（基于 ref_entity_id 和 ref_type）
                foreign_keys = []
                for attr in attr_results:
                    if (
                        attr[11] and attr[13] == "foreign_key"
                    ):  # ref_entity_id 和 ref_type
                        # 查询引用的实体信息
                        ref_query = text("""
                            SELECT table_name FROM da_logic_entity WHERE id = :ref_entity_id
                        """)
                        ref_result = conn.execute(
                            ref_query, {"ref_entity_id": attr[11]}
                        ).fetchone()
                        if ref_result:
                            foreign_keys.append(
                                {
                                    "column": attr[2] or attr[1],
                                    "referenced_table": ref_result[0],
                                    "referenced_column": "id",  # 通常引用主键
                                }
                            )

                return TableInfo(
                    name=table_name,
                    comment=f"{entity_name} - {entity_description}"
                    if entity_description
                    else entity_name,
                    columns=columns,
                    indexes=[],  # 低代码系统中索引信息不在这些表中
                    foreign_keys=foreign_keys,
                )

        except SQLAlchemyError as e:
            print(f"Error getting table info from schema for {table_name}: {e}")
            return None

    def _get_table_info_from_metadata(self, table_name: str) -> Optional[TableInfo]:
        """通过数据库元数据获取表信息（传统方式）"""
        try:
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=self.engine)

            columns = []
            for column in table.columns:
                column_info = ColumnInfo(
                    name=column.name,
                    type=str(column.type),
                    nullable=column.nullable,
                    default=str(column.default) if column.default else None,
                    comment=column.comment,
                    is_primary_key=column.primary_key,
                    max_length=getattr(column.type, "length", None),
                )
                columns.append(column_info)

            # 获取外键信息
            foreign_keys = []
            for fk in table.foreign_keys:
                foreign_keys.append(
                    {
                        "column": fk.parent.name,
                        "referenced_table": fk.column.table.name,
                        "referenced_column": fk.column.name,
                    }
                )

            # 获取索引信息
            indexes = []
            for index in table.indexes:
                indexes.append(
                    {
                        "name": index.name,
                        "columns": [col.name for col in index.columns],
                        "unique": index.unique,
                    }
                )

            return TableInfo(
                name=table_name,
                comment=table.comment,
                columns=columns,
                indexes=indexes,
                foreign_keys=foreign_keys,
            )

        except SQLAlchemyError as e:
            print(f"Error getting table info from metadata for {table_name}: {e}")
            return None

    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        if not self.engine:
            return []

        try:
            metadata = MetaData()
            metadata.reflect(bind=self.engine)
            return list(metadata.tables.keys())
        except SQLAlchemyError as e:
            print(f"Error getting table list: {e}")
            return []

    def get_database_schema(self) -> Optional[DatabaseSchema]:
        """获取完整的数据库架构信息"""
        table_names = self.get_all_tables()
        if not table_names:
            return None

        tables = []
        for table_name in table_names:
            table_info = self.get_table_info(table_name)
            if table_info:
                tables.append(table_info)

        # 从连接字符串中提取数据库名
        database_name = self.database_url.split("/")[-1].split("?")[0]

        return DatabaseSchema(database_name=database_name, tables=tables)

    def search_tables(self, keyword: str) -> List[TableInfo]:
        """根据关键词搜索表"""
        all_tables = self.get_all_tables()
        matching_tables = [
            table for table in all_tables if keyword.lower() in table.lower()
        ]

        result = []
        for table_name in matching_tables:
            table_info = self.get_table_info(table_name)
            if table_info:
                result.append(table_info)

        return result

    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
