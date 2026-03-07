"""Agent 集成示例"""

from todoagent import TodoList


def agent_workflow():
    """模拟 Agent 的工作流程"""
    todo = TodoList(storage_path="./agent_tasks.json")

    print("🤖 Agent 启动，检查待办任务...")
    print()

    # 1. 检查是否有未完成的任务
    pending = todo.list_tasks(status="pending")
    in_progress = todo.list_tasks(status="in_progress")

    if in_progress:
        print(f"🔄 有 {len(in_progress)} 个进行中的任务:")
        for t in in_progress:
            print(f"   - [{t['priority']}] {t['title']}")
        print()

    if pending:
        print(f"⏳ 有 {len(pending)} 个待办任务:")
        for t in pending:
            print(f"   - [{t['priority']}] {t['title']}")
        print()
    else:
        print("✨ 没有待办任务！")

    # 2. Agent 接到新任务
    print("📩 收到新任务请求...")
    new_tasks = [
        {"title": "分析用户数据", "priority": "high", "tags": ["data"]},
        {"title": "生成周报", "priority": "medium", "tags": ["report"]},
        {"title": "更新文档", "priority": "low", "tags": ["docs"]},
    ]

    for task_info in new_tasks:
        task = todo.add(**task_info)
        print(f"   ✅ 已添加: {task['title']} (ID: {task['id']})")
    print()

    # 3. Agent 开始处理高优先级任务
    high_tasks = todo.list_tasks(priority="high", status="pending")
    if high_tasks:
        task = high_tasks[0]
        todo.start(task["id"])
        print(f"🔄 开始处理: {task['title']}")

        # 模拟完成
        todo.complete(task["id"])
        print(f"✅ 完成: {task['title']}")
    print()

    # 4. 查看最终摘要
    summary = todo.summary()
    print("📊 当前任务状态:")
    print(f"   总计: {summary['total']}")
    print(f"   待办: {summary['pending']}")
    print(f"   进行中: {summary['in_progress']}")
    print(f"   已完成: {summary['completed']}")

    # 清理
    import os
    os.remove("./agent_tasks.json")


if __name__ == "__main__":
    agent_workflow()
