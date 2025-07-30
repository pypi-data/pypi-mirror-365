"""简化版 SP Database MCP Server - 演示版本"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.lowlevel import NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
)

# 加载环境变量
load_dotenv()

# 创建服务器实例
server = Server("sp-database-mcp")

# 模拟的数据库表信息
MOCK_TABLES = {
    "activity_node": {
        "name": "activity_node",
        "comment": "活动节点表 - 用于记录流程活动中的关键节点",
        "columns": [
            {
                "name": "id",
                "type": "bigint",
                "nullable": False,
                "comment": "主键ID",
                "is_primary_key": True
            },
            {
                "name": "type",
                "type": "varchar(50)",
                "nullable": False,
                "comment": "节点分类 - 高阶分类，如 TASK(任务节点), APPROVAL(审批节点), TRIGGER(触发器节点)"
            },
            {
                "name": "activity_type",
                "type": "varchar(100)",
                "nullable": False,
                "comment": "具体类型 - 低阶分类，如 FILL_FORM(表单填报), AUTO_SCRIPT(自动化脚本)"
            },
            {
                "name": "activity_code",
                "type": "varchar(100)",
                "nullable": False,
                "comment": "活动编码 - 节点的唯一标识编码"
            },
            {
                "name": "development_status",
                "type": "varchar(20)",
                "nullable": True,
                "comment": "开发状态 - 当前节点的开发进展（已发布/草稿等）"
            },
            {
                "name": "latest",
                "type": "boolean",
                "nullable": False,
                "comment": "是否最新版本 - true 表示该记录是最新版本"
            },
            {
                "name": "status",
                "type": "varchar(20)",
                "nullable": True,
                "comment": "状态 - 活动当前使用状态（启用/停用）"
            },
            {
                "name": "business_object_name",
                "type": "varchar(200)",
                "nullable": True,
                "comment": "业务对象名称 - 与之绑定的业务对象展示名"
            },
            {
                "name": "business_object_id",
                "type": "bigint",
                "nullable": True,
                "comment": "业务对象ID - 与业务对象绑定的主键 ID"
            },
            {
                "name": "ref_dac_id",
                "type": "bigint",
                "nullable": True,
                "comment": "所属资产对象id - 资产l3节点id（来自 da_asset_object）"
            },
            {
                "name": "app_belong",
                "type": "varchar(100)",
                "nullable": True,
                "comment": "所属应用 - 节点所属应用"
            },
            {
                "name": "created_at",
                "type": "timestamp",
                "nullable": False,
                "comment": "创建时间"
            },
            {
                "name": "updated_at",
                "type": "timestamp",
                "nullable": False,
                "comment": "更新时间"
            }
        ]
    },
    "scene_activity": {
        "name": "scene_activity",
        "comment": "场景活动表 - 记录各种业务场景下的活动信息",
        "columns": [
            {
                "name": "id",
                "type": "bigint",
                "nullable": False,
                "comment": "主键ID",
                "is_primary_key": True
            },
            {
                "name": "scene_id",
                "type": "bigint",
                "nullable": False,
                "comment": "场景ID"
            },
            {
                "name": "activity_name",
                "type": "varchar(200)",
                "nullable": False,
                "comment": "活动名称"
            },
            {
                "name": "activity_desc",
                "type": "text",
                "nullable": True,
                "comment": "活动描述"
            },
            {
                "name": "status",
                "type": "varchar(20)",
                "nullable": False,
                "comment": "活动状态"
            }
        ]
    },
    "da_asset_object": {
        "name": "da_asset_object",
        "comment": "数据资产对象表 - 存储数据资产的基本信息",
        "columns": [
            {
                "name": "id",
                "type": "bigint",
                "nullable": False,
                "comment": "主键ID",
                "is_primary_key": True
            },
            {
                "name": "asset_name",
                "type": "varchar(200)",
                "nullable": False,
                "comment": "资产名称"
            },
            {
                "name": "asset_type",
                "type": "varchar(50)",
                "nullable": False,
                "comment": "资产类型"
            },
            {
                "name": "description",
                "type": "text",
                "nullable": True,
                "comment": "资产描述"
            }
        ]
    }
}


@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """列出可用的资源"""
    resources = []
    
    for table_name in MOCK_TABLES.keys():
        resources.append(
            Resource(
                uri=f"table://{table_name}",
                name=f"表: {table_name}",
                description=f"数据库表 {table_name} 的结构信息",
                mimeType="application/json"
            )
        )
    
    return resources


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """读取资源内容"""
    try:
        if uri.startswith("table://"):
            table_name = uri.replace("table://", "")
            if table_name in MOCK_TABLES:
                table_info = MOCK_TABLES[table_name]
                return json.dumps(table_info, indent=2, ensure_ascii=False)
            else:
                return f"表 {table_name} 不存在"
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
            description="获取指定数据库表的结构信息，包括字段定义、类型、注释等",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "要查询的表名，如：activity_node, scene_activity, da_asset_object"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="search_tables",
            description="根据关键词搜索数据库表",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="list_all_tables",
            description="列出所有数据库表",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_table_fields_summary",
            description="获取表字段的简要说明",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "表名"
                    }
                },
                "required": ["table_name"]
            }
        )
    ]
    
    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "get_table_info":
            table_name = arguments.get("table_name")
            
            if not table_name:
                return [TextContent(type="text", text="错误：缺少表名参数")]
            
            if table_name in MOCK_TABLES:
                table_info = MOCK_TABLES[table_name]
                output = format_table_info(table_info)
                return [TextContent(type="text", text=output)]
            else:
                available_tables = ", ".join(MOCK_TABLES.keys())
                return [TextContent(type="text", text=f"未找到表 '{table_name}'。可用的表有: {available_tables}")]
        
        elif name == "search_tables":
            keyword = arguments.get("keyword")
            
            if not keyword:
                return [TextContent(type="text", text="错误：缺少搜索关键词")]
            
            matching_tables = []
            for table_name, table_info in MOCK_TABLES.items():
                if (keyword.lower() in table_name.lower() or 
                    keyword.lower() in table_info.get("comment", "").lower()):
                    matching_tables.append((table_name, table_info))
            
            if matching_tables:
                output = f"找到 {len(matching_tables)} 个匹配的表：\n\n"
                for table_name, table_info in matching_tables:
                    output += f"## {table_name}\n"
                    if table_info.get("comment"):
                        output += f"**说明**: {table_info['comment']}\n"
                    output += f"**字段数**: {len(table_info['columns'])}\n\n"
                return [TextContent(type="text", text=output)]
            else:
                return [TextContent(type="text", text=f"未找到包含关键词 '{keyword}' 的表")]
        
        elif name == "list_all_tables":
            output = f"数据库中共有 {len(MOCK_TABLES)} 个表：\n\n"
            for table_name, table_info in MOCK_TABLES.items():
                output += f"- **{table_name}**: {table_info.get('comment', '无描述')}\n"
            return [TextContent(type="text", text=output)]
        
        elif name == "get_table_fields_summary":
            table_name = arguments.get("table_name")
            
            if not table_name:
                return [TextContent(type="text", text="错误：缺少表名参数")]
            
            if table_name in MOCK_TABLES:
                table_info = MOCK_TABLES[table_name]
                output = f"# {table_name} 表字段简要说明\n\n"
                if table_info.get("comment"):
                    output += f"**表说明**: {table_info['comment']}\n\n"
                
                output += "## 主要字段\n\n"
                for column in table_info["columns"]:
                    output += f"- **{column['name']}** ({column['type']}): {column.get('comment', '无描述')}\n"
                
                return [TextContent(type="text", text=output)]
            else:
                available_tables = ", ".join(MOCK_TABLES.keys())
                return [TextContent(type="text", text=f"未找到表 '{table_name}'。可用的表有: {available_tables}")]
        
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"工具调用出错: {str(e)}")]


def format_table_info(table_info: Dict[str, Any]) -> str:
    """格式化表信息输出"""
    output = f"# {table_info['name']} 表结构信息\n\n"
    
    if table_info.get("comment"):
        output += f"**表说明**: {table_info['comment']}\n\n"
    
    output += "## 字段信息\n\n"
    output += "| 字段名 | 类型 | 可空 | 主键 | 说明 |\n"
    output += "|--------|------|------|------|------|\n"
    
    for column in table_info["columns"]:
        nullable = "是" if column.get("nullable", True) else "否"
        primary_key = "是" if column.get("is_primary_key", False) else "否"
        comment = column.get("comment", "-")
        
        output += f"| {column['name']} | {column['type']} | {nullable} | {primary_key} | {comment} |\n"
    
    return output


async def main():
    """主函数"""
    print("SP Database MCP Server 启动中...")
    print("可用的表:")
    for table_name, table_info in MOCK_TABLES.items():
        print(f"  - {table_name}: {table_info.get('comment', '无描述')}")
    
    # 启动服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sp-database-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities=None,
                ),
            ),
        )


def cli_main():
    """CLI 入口点"""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
