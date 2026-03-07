# 📝 TodoList for Agent

> 给 AI Agent 使用的任务管理工具，让 Agent 知道自己还有什么任务没有完成。

## ✨ 功能特性

- ✅ 创建、查看、更新、删除任务
- 🏷️ 支持优先级（高/中/低）和标签分类
- 📅 支持截止日期设置
- 🔍 按状态、优先级、标签筛选任务
- 💾 JSON 文件持久化存储
- 🖥️ CLI 命令行界面 + Python API 双模式
- 🤖 专为 Agent 设计的简洁输出格式

## 📦 安装

```bash
# 克隆仓库
git clone https://github.com/superwoman007/TodolistForAgent.git
cd TodolistForAgent

# 安装依赖
pip install -e .
```

## 🚀 快速开始

### CLI 命令行使用

```bash
# 添加任务
todoagent add "完成项目报告" --priority high --tag work --due 2026-03-15

# 查看所有任务
todoagent list

# 查看待办任务
todoagent list --status pending

# 完成任务
todoagent done <task_id>

# 更新任务
todoagent update <task_id> --title "新标题" --priority medium

# 删除任务
todoagent remove <task_id>

# 查看任务摘要
todoagent summary

# 清除已完成任务
todoagent clear
```

### Python API 使用

```python
from todoagent import TodoList

# 初始化（默认存储在 ~/.todoagent/tasks.json）
todo = TodoList()

# 添加任务
task = todo.add("完成项目报告", priority="high", tags=["work"], due_date="2026-03-15")

# 查看所有任务
tasks = todo.list_tasks()

# 查看待办任务
pending = todo.list_tasks(status="pending")

# 完成任务
todo.complete(task["id"])

# 更新任务
todo.update(task["id"], title="更新后的标题", priority="medium")

# 删除任务
todo.remove(task["id"])

# 获取摘要
summary = todo.summary()

# 清除已完成任务
todo.clear_completed()
```

### Agent 集成示例

```python
from todoagent import TodoList

todo = TodoList(storage_path="./agent_tasks.json")

# Agent 在开始工作时检查待办任务
pending = todo.list_tasks(status="pending")
if pending:
    print(f"你还有 {len(pending)} 个待办任务:")
    for t in pending:
        print(f"  - [{t['priority']}] {t['title']}")
else:
    print("所有任务已完成！🎉")

# Agent 完成任务后标记
todo.complete(task_id)

# Agent 接到新需求时添加任务
todo.add("用户要求分析数据", priority="high", tags=["data", "analysis"])
```

## 📁 项目结构

```
TodolistForAgent/
├── README.md               # 项目说明
├── setup.py                # 安装配置
├── requirements.txt        # 依赖列表
├── todoagent/              # 核心代码
│   ├── __init__.py         # 包入口
│   ├── models.py           # 数据模型
│   ├── storage.py          # 持久化存储
│   ├── todo.py             # 核心逻辑
│   └── cli.py              # 命令行界面
├── tests/                  # 测试
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_storage.py
│   └── test_todo.py
├── examples/               # 使用示例
│   ├── basic_usage.py
│   └── agent_integration.py
└── .gitignore
```

## 🧪 运行测试

```bash
pytest tests/ -v
```

## 📄 License

MIT License
