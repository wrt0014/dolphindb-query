# DolphinDB 查询 Skill 安装说明

## 已创建的文件

1. **SKILL.md** - Skill 定义文件
2. **dolphindb_helper.py** - Python 查询辅助类

## 安装步骤

在聊天中输入以下命令安装 Skill：

```
/install /workspace/group/skills/dolphindb-query
```

## 依赖安装

在执行查询前，需要先安装 DolphinDB Python SDK：

```bash
pip install dolphindb
```

## 使用方法

安装后，可以直接通过对话查询数据，例如：

- "查询名称包含华夏的基金"
- "查询基金F_XXX的持仓"
- "查询股票S_XXX所属的行业"
- "查询基金经理M_XXX管理的所有基金"
- "查询近一年收益率最高的10只基金"
