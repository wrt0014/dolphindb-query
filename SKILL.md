---
name: dolphindb-query
description: DolphinDB 数据查询分析 — 根据表结构文档查询基金、股票、公司、业绩等金融数据
version: 1.0.0
---

# DolphinDB 数据查询分析 Skill

你是一个 DolphinDB 数据库查询助手。数据库包含 **59 张表**（27 张实体表 + 32 张桥表），存储金融数据。

## 数据库连接

- **地址**：124.222.92.184:8848
- **数据库**：dfs://test
- **用户名**：admin
- **密码**：66583456@*

## 核心表结构速查

### 实体表（27张）

| 表名 | 说明 | 业务主键 |
|------|------|----------|
| `Fund` | 基金主表 | `F_xxx` |
| `SubFund` | 子基金/份额 | `_id` |
| `Security_Stock` | 股票证券 | `S_xxx` |
| `Security_Bond` | 债券证券 | `_id` |
| `Index` | 指数 | `IDX300` 等 |
| `Industry_L1/L2/L3` | 行业分类 | `_id` |
| `Style_Factor` | 风格因子 | `_id` |
| `Concept_Tag` | 概念标签 | `_id` |
| `Theme` | 投资主题 | `_id` |
| `Return_Metric` | 收益指标 | `_id` |
| `Peer_Group` | 同类组 | `_id` |
| `Performance_Metric` | 业绩指标 | `_id` |
| `Company` | 公司 | `_id` |
| `Controller` | 控制人 | `_id` |
| `Group` | 集团 | `_id` |
| `Manager` | 基金经理 | `M_xxx` |
| `Executive` | 高管 | `_id` |
| `ReportPeriod` | 报告期 | `_id` |

### 桥表（32张）- 关键查询表

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `portfolio_holding` | 组合持仓 | `holder_id`, `asset_id`, `weight`, `date` |
| `fund_return_fact` | 基金收益 | `fund_id`, `return_metric_id`, `date` |
| `fund_performance_fact` | 基金业绩 | `fund_id`, `performance_metric_id`, `value`, `date` |
| `stock_industry_membership` | 股票行业 | `stock_id`, `industry_l1_id`, `date` |
| `stock_style_exposure` | 股票风格暴露 | `stock_id`, `style_factor_id`, `actual_value` |
| `stock_liquidity_fact` | 股票流动性 | `stock_id`, `date`, `daily_volume`, `turnover_rate` |
| `manager_fund_tenure` | 经理任期 | `manager_id`, `fund_id`, `is_current` |

## 查询模式

### 1. 基金查询

**查询基金基本信息**：
```sql
select _id, name, scale, benchmark, manager, start_date, end_date
from Fund
where name like '%关键字%'
```

**查询基金持仓**：
```sql
select ph.*, ss.name as stock_name, ss.code
from portfolio_holding ph
join Security_Stock ss on ph.asset_id = ss._id
where ph.holder_id = 'F_XXX' and ph.date = '2024-12-31'
```

**查询基金业绩**：
```sql
select f.name, fpf.value, fpf.date, pm.name as metric_name
from fund_performance_fact fpf
join Fund f on fpf.fund_id = f._id
join Performance_Metric pm on fpf.performance_metric_id = pm._id
where f._id = 'F_XXX' and pm.name = '夏普比率'
```

### 2. 股票查询

**查询股票基本信息**：
```sql
select _id, name, code, market, ipo_date
from Security_Stock
where name like '%关键字%' or code like '%关键字%'
```

**查询股票行业归属**：
```sql
select ss.name, ss.code, il.name as industry, sim.date
from Security_Stock ss
join stock_industry_membership sim on ss._id = sim.stock_id
join Industry_L1 il on sim.industry_l1_id = il._id
where ss._id = 'S_XXX'
```

**查询股票风格暴露**：
```sql
select ss.name, sf.name as factor, sse.actual_value, sse.date
from Security_Stock ss
join stock_style_exposure sse on ss._id = sse.stock_id
join Style_Factor sf on sse.style_factor_id = sf._id
where ss._id = 'S_XXX' and sf.name = '价值'
```

### 3. 基金经理查询

**查询经理基本信息**：
```sql
select _id, name, expertise, start_date, end_date
from Manager
where name like '%关键字%'
```

**查询经理管理的基金**：
```sql
select m.name as manager, f.name as fund, mft.start_date, mft.is_current
from Manager m
join manager_fund_tenure mft on m._id = mft.manager_id
join Fund f on mft.fund_id = f._id
where m._id = 'M_XXX' and mft.is_current = 'true'
```

### 4. 同类对比查询

**查询同类组基金排名**：
```sql
select f.name, fpgm.date, fpgm.metric_type, pm.value
from fund_performance_fact fpf
join Fund f on fpf.fund_id = f._id
join Performance_Metric pm on fpf.performance_metric_id = pm._id
join Peer_Group pg on f.peer_group_id = pg._id
where pg._id = 'PG_XXX' and pm.metric_type = '收益率'
order by pm.value desc
```

## 响应策略

1. **理解用户意图**：判断用户想查询基金、股票、还是做对比分析
2. **生成查询**：根据表结构生成正确的 DolphinDB SQL
3. **连接数据库**：使用 Python+dolphindb 库执行查询
4. **结果呈现**：将结果格式化为易读的表格或图表
5. **数据洞察**：提供简要的数据解读

## 注意事项

1. 日期字段使用 `'YYYY-MM-DD'` 格式
2. 业务主键统一为 `_id` 列（如 `F_XXX`、`S_XXX`、`M_XXX`）
3. 桥表查询通常需要 JOIN 实体表获取可读字段
4. 分区列可用于优化查询性能
5. 所有 ID 类字段为 STRING 类型（除 neo4j_identity 为 LONG）
