# SP Database MCP Server

一个用于实时获取数据库表结构信息的 Model Context Protocol (MCP) 服务器。通过 MCP 协议，可以让 AI 助手实时获取数据库的表结构信息，解决信息不及时更新的问题。

## 功能特性

- **智能表结构查询**：支持两种查询模式
  - **低代码系统 Schema 查询**：通过 `da_logic_entity` 和 `da_entity_attribute` 表获取详细的业务字段信息
  - **传统数据库元数据查询**：直接从数据库系统表获取技术字段信息
- 🔄 实时获取数据库表结构信息
- 📊 支持多种数据库类型 (MySQL, PostgreSQL)
- 🚀 通过 API 接口动态获取最新的表字段信息
- 🔍 支持表信息查询和字段详情获取
- 📝 自动生成表结构文档

## 安装

```bash
cd ~/Project/sp-database-mcp
uv sync
```

## 配置

创建 `.env` 文件：

```env
# 数据库连接配置
DATABASE_URL=mysql://username:password@localhost:3306/database_name
# 或者 PostgreSQL
# DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# API 接口配置（如果通过 API 获取）
API_BASE_URL=https://your-api-server.com
API_TOKEN=your-api-token
```

## 使用方式

### 启动 MCP 服务器

```bash
uv run sp-database-mcp
```

### 在 Claude Desktop 中配置

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "sp-database": {
      "command": "uv",
      "args": ["run", "sp-database-mcp"],
      "cwd": "/Users/alexliu/Project/sp-database-mcp"
    }
  }
}
```

### 使用示例

- "介绍一下活动表有哪些字段"
- "获取 activity_node 表的结构信息"
- "查看用户表的字段定义"

## 使用示例

### 查询表结构信息

现在支持两种查询模式，系统会自动优先使用低代码系统的 schema 查询：

```python
# 通过 MCP 工具查询表信息
# 输入：请获取 activity_node 表的详细信息

# 输出示例（低代码系统 schema 查询结果）：
# activity_node 表结构信息
# 
# **表说明**: 活动
# 
# ## 字段信息
# 
# | 字段名 | 类型 | 可空 | 默认值 | 主键 | 说明 |
# |--------|------|------|--------|------|---------|
# | id | BIGINT | 否 | - | 是 | 主键ID |
# | name | VARCHAR(1000) | 是 | - | 否 | 活动名称 |
# | activity_code | VARCHAR(64) | 是 | - | 否 | 活动编码 |
# | business_object_id | BIGINT | 是 | - | 否 | 业务对象id |
# | ... | ... | ... | ... | ... | ... |
```

### 查询模式说明

1. **低代码系统 Schema 查询**（优先）
   - 查询 `da_logic_entity` 表获取实体基本信息
   - 查询 `da_entity_attribute` 表获取字段详细信息
   - 提供中文字段名、业务描述、数据类型等丰富信息
   - 支持外键关系解析

2. **传统数据库元数据查询**（回退）
   - 当低代码系统查询失败时自动回退
   - 直接从数据库系统表获取技术字段信息
   - 提供基础的字段类型、约束等信息

## 项目结构

```
sp-database-mcp/
├── src/
│   └── sp_database_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP 服务器主文件
│       ├── database.py        # 数据库连接和查询
│       ├── api_client.py      # API 客户端
│       └── models.py          # 数据模型
├── tests/
├── .env.example
├── pyproject.toml
└── README.md
```

## 开发

```bash
# 安装开发依赖
uv sync --dev

# 运行测试
uv run pytest

# 代码格式化
uv run black .
uv run isort .

# 类型检查
uv run mypy .
```
