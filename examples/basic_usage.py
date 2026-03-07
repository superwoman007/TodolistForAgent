"""基本使用示例"""

from todoagent import TodoList


def main():
    # 创建 TodoList 实例
    todo = TodoList(storage_path="./example_tasks.json")

    # 添加几个任务
    task1 = todo.add("阅读 Python 文档", priority="medium", tags=["study"])
    task2 = todo.add("完成项目报告", priority="high", tags=["work"], due_date="2026-03-15")
    task3 = todo.add("买菜", priority="low", tags=["life"])

    print("📝 添加了 3 个任务")
    print()

    # 查看所有任务
    tasks = todo.list_tasks()
    print(f"📋 所有任务 ({len(tasks)}):")
    for t in tasks:
        print(f"  [{t['priority']}] {t['title']} - {t['status']}")
    print()

    # 完成一个任务
    todo.complete(task3["id"])
    print(f"✅ 完成了: {task3['title']}")
    print()

    # 查看摘要
    summary = todo.summary()
    print(f"📊 摘要: 总计 {summary['total']}, 待办 {summary['pending']}, 已完成 {summary['completed']}")

    # 清理示例文件
    import os
    os.remove("./example_tasks.json")


if __name__ == "__main__":
    main()
