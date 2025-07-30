"""SP Database MCP Server - 主服务器文件"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.lowlevel import NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    EmbeddedResource,
    ImageContent,
    LoggingLevel,
    Resource,
    TextContent,
    Tool,
)

from .api_client import APIClient
from .database import DatabaseClient
from .models import ColumnInfo, TableInfo

# 加载环境变量
load_dotenv()

# 创建服务器实例
server = Server("sp-database-mcp")

# 全局客户端实例
db_client: Optional[DatabaseClient] = None
api_client: Optional[APIClient] = None


@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """列出可用的资源"""
    resources = []

    # 如果有数据库连接，列出所有表作为资源
    if db_client:
        try:
            tables = db_client.get_all_tables()
            for table_name in tables:
                resources.append(
                    Resource(
                        uri=f"database://table/{table_name}",
                        name=f"表: {table_name}",
                        description=f"数据库表 {table_name} 的结构信息",
                        mimeType="application/json",
                    )
                )
        except Exception as e:
            print(f"Error listing database tables: {e}")

    # 如果有 API 客户端，也可以列出 API 资源
    if api_client:
        try:
            tables = await api_client.get_all_tables()
            for table_name in tables:
                resources.append(
                    Resource(
                        uri=f"api://table/{table_name}",
                        name=f"API表: {table_name}",
                        description=f"通过 API 获取的表 {table_name} 的结构信息",
                        mimeType="application/json",
                    )
                )
        except Exception as e:
            print(f"Error listing API tables: {e}")

    return resources


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """读取资源内容"""
    try:
        if uri.startswith("database://table/"):
            table_name = uri.replace("database://table/", "")
            if db_client:
                table_info = db_client.get_table_info(table_name)
                if table_info:
                    return json.dumps(
                        table_info.model_dump(), indent=2, ensure_ascii=False
                    )
                else:
                    return f"表 {table_name} 不存在或无法访问"
            else:
                return "数据库连接未配置"

        elif uri.startswith("api://table/"):
            table_name = uri.replace("api://table/", "")
            if api_client:
                table_info = await api_client.get_table_info(table_name)
                if table_info:
                    return json.dumps(
                        table_info.model_dump(), indent=2, ensure_ascii=False
                    )
                else:
                    return f"表 {table_name} 不存在或无法通过 API 访问"
            else:
                return "API 客户端未配置"

        else:
            return f"不支持的资源 URI: {uri}"

    except Exception as e:
        return f"读取资源时出错: {str(e)}"


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """列出可用的工具"""
    tools = [
        Tool(
            name="get_table_info",
            description="获取指定数据库表的结构信息，包括字段定义、类型、注释等。支持两种查询方式：1) 低代码系统schema查询（通过da_logic_entity和da_entity_attribute表）；2) 传统数据库元数据查询。优先使用低代码系统方式获取更详细的字段信息。",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "要查询的表名"},
                    "source": {
                        "type": "string",
                        "enum": ["database", "api", "auto"],
                        "description": "数据源类型：database(直连数据库)、api(通过API)、auto(自动选择)",
                        "default": "auto",
                    },
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="search_tables",
            description="根据关键词搜索数据库表",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "source": {
                        "type": "string",
                        "enum": ["database", "api", "auto"],
                        "description": "数据源类型",
                        "default": "auto",
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="list_all_tables",
            description="列出所有数据库表",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "enum": ["database", "api", "auto"],
                        "description": "数据源类型",
                        "default": "auto",
                    }
                },
            },
        ),
        Tool(
            name="get_table_documentation",
            description="获取表的详细文档说明",
            inputSchema={
                "type": "object",
                "properties": {"table_name": {"type": "string", "description": "表名"}},
                "required": ["table_name"],
            },
        ),
    ]

    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "get_table_info":
            table_name = arguments.get("table_name")
            source = arguments.get("source", "auto")

            if not table_name:
                return [TextContent(type="text", text="错误：缺少表名参数")]

            table_info = await _get_table_info(table_name, source)
            if table_info:
                # 格式化输出
                output = _format_table_info(table_info)
                return [TextContent(type="text", text=output)]
            else:
                return [
                    TextContent(type="text", text=f"未找到表 '{table_name}' 的信息")
                ]

        elif name == "search_tables":
            keyword = arguments.get("keyword")
            source = arguments.get("source", "auto")

            if not keyword:
                return [TextContent(type="text", text="错误：缺少搜索关键词")]

            tables = await _search_tables(keyword, source)
            if tables:
                output = f"找到 {len(tables)} 个匹配的表：\n\n"
                for table in tables:
                    output += f"## {table.name}\n"
                    if table.comment:
                        output += f"**说明**: {table.comment}\n"
                    output += f"**字段数**: {len(table.columns)}\n\n"
                return [TextContent(type="text", text=output)]
            else:
                return [
                    TextContent(type="text", text=f"未找到包含关键词 '{keyword}' 的表")
                ]

        elif name == "list_all_tables":
            source = arguments.get("source", "auto")

            tables = await _list_all_tables(source)
            if tables:
                output = f"数据库中共有 {len(tables)} 个表：\n\n"
                for table_name in sorted(tables):
                    output += f"- {table_name}\n"
                return [TextContent(type="text", text=output)]
            else:
                return [TextContent(type="text", text="未找到任何表")]

        elif name == "get_table_documentation":
            table_name = arguments.get("table_name")

            if not table_name:
                return [TextContent(type="text", text="错误：缺少表名参数")]

            # 首先尝试获取表信息
            table_info = await _get_table_info(table_name, "auto")
            if not table_info:
                return [
                    TextContent(type="text", text=f"未找到表 '{table_name}' 的信息")
                ]

            # 如果有 API 客户端，尝试获取文档
            documentation = ""
            if api_client:
                try:
                    documentation = await api_client.get_table_documentation(table_name)
                except Exception as e:
                    print(f"Error getting documentation: {e}")

            # 生成完整的文档
            output = _format_table_documentation(table_info, documentation)
            return [TextContent(type="text", text=output)]

        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"工具调用出错: {str(e)}")]


async def _get_table_info(table_name: str, source: str) -> Optional[TableInfo]:
    """获取表信息的内部方法"""
    if source == "database" and db_client:
        return db_client.get_table_info(table_name)
    elif source == "api" and api_client:
        return await api_client.get_table_info(table_name)
    elif source == "auto":
        # 优先使用数据库直连，然后是 API
        if db_client:
            result = db_client.get_table_info(table_name)
            if result:
                return result
        if api_client:
            return await api_client.get_table_info(table_name)

    return None


async def _search_tables(keyword: str, source: str) -> List[TableInfo]:
    """搜索表的内部方法"""
    if source == "database" and db_client:
        return db_client.search_tables(keyword)
    elif source == "api" and api_client:
        return await api_client.search_tables(keyword)
    elif source == "auto":
        # 优先使用数据库直连
        if db_client:
            result = db_client.search_tables(keyword)
            if result:
                return result
        if api_client:
            return await api_client.search_tables(keyword)

    return []


async def _list_all_tables(source: str) -> List[str]:
    """列出所有表的内部方法"""
    if source == "database" and db_client:
        return db_client.get_all_tables()
    elif source == "api" and api_client:
        return await api_client.get_all_tables()
    elif source == "auto":
        # 优先使用数据库直连
        if db_client:
            result = db_client.get_all_tables()
            if result:
                return result
        if api_client:
            return await api_client.get_all_tables()

    return []


def _format_table_info(table_info: TableInfo) -> str:
    """格式化表信息输出"""
    output = f"# {table_info.name} 表结构信息\n\n"

    if table_info.comment:
        output += f"**表说明**: {table_info.comment}\n\n"

    output += "## 字段信息\n\n"
    output += "| 属性名称 | 编码 | 数据类型 | 主键 | 系统字段 |\n"
    output += "|----------|------|----------|------|--------|\n"

    for column in table_info.columns:
        primary_key = "是" if column.is_primary_key else ""
        is_system = "是" if column.is_system else ""

        output += f"| {column.name} | {column.code} | {column.type} | {primary_key} | {is_system} |\n"

    if table_info.indexes:
        output += "\n## 索引信息\n\n"
        for index in table_info.indexes:
            index_type = "唯一索引" if index.get("unique") else "普通索引"
            columns = ", ".join(index.get("columns", []))
            output += f"- **{index.get('name')}** ({index_type}): {columns}\n"

    if table_info.foreign_keys:
        output += "\n## 外键关系\n\n"
        for fk in table_info.foreign_keys:
            output += f"- {fk.get('column')} → {fk.get('referenced_table')}.{fk.get('referenced_column')}\n"

    return output


def _format_table_documentation(
    table_info: TableInfo, documentation: Optional[str] = None
) -> str:
    """格式化表文档"""
    output = f"# {table_info.name} 表文档\n\n"

    if table_info.comment:
        output += f"## 表说明\n\n{table_info.comment}\n\n"

    if documentation:
        output += f"## 详细文档\n\n{documentation}\n\n"

    output += _format_table_info(table_info)

    return output


async def main():
    """主函数"""
    global db_client, api_client

    # 初始化数据库客户端
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        try:
            db_client = DatabaseClient(database_url)
            print("数据库连接已建立")
        except Exception as e:
            print(f"数据库连接失败: {e}")

    # 初始化 API 客户端
    api_base_url = os.getenv("API_BASE_URL")
    if api_base_url:
        try:
            api_client = APIClient()
            print("API 客户端已初始化")
        except Exception as e:
            print(f"API 客户端初始化失败: {e}")

    if not db_client and not api_client:
        print("警告: 没有配置任何数据源，请检查环境变量配置")

    # 启动服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sp-database-mcp",
                server_version="0.1.2",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities=None,
                ),
            ),
        )


def cli_main():
    """命令行入口点"""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
