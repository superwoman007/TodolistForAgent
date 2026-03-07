"""命令行界面"""

import click
from tabulate import tabulate

from .todo import TodoList


# 优先级 emoji
PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}
STATUS_EMOJI = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}


@click.group()
@click.option("--storage", "-s", default=None, help="指定存储文件路径")
@click.pass_context
def cli(ctx, storage):
    """📝 TodoList for Agent - 任务管理工具"""
    ctx.ensure_object(dict)
    ctx.obj["todo"] = TodoList(storage_path=storage)


@cli.command()
@click.argument("title")
@click.option("--priority", "-p", type=click.Choice(["high", "medium", "low"]), default="medium", help="优先级")
@click.option("--tag", "-t", multiple=True, help="标签（可多个）")
@click.option("--due", "-d", default=None, help="截止日期 (YYYY-MM-DD)")
@click.option("--desc", default="", help="任务描述")
@click.pass_context
def add(ctx, title, priority, tag, due, desc):
    """添加新任务"""
    todo = ctx.obj["todo"]
    task = todo.add(title=title, priority=priority, tags=list(tag), due_date=due, description=desc)
    emoji = PRIORITY_EMOJI.get(priority, "")
    click.echo(f"✅ 已添加任务: {emoji} {task['title']} (ID: {task['id']})")


@cli.command(name="list")
@click.option("--status", type=click.Choice(["pending", "in_progress", "completed"]), default=None, help="按状态筛选")
@click.option("--priority", "-p", type=click.Choice(["high", "medium", "low"]), default=None, help="按优先级筛选")
@click.option("--tag", "-t", default=None, help="按标签筛选")
@click.pass_context
def list_tasks(ctx, status, priority, tag):
    """查看任务列表"""
    todo = ctx.obj["todo"]
    tasks = todo.list_tasks(status=status, priority=priority, tag=tag)

    if not tasks:
        click.echo("📭 没有找到任务")
        return

    headers = ["ID", "状态", "优先级", "标题", "标签", "截止日期"]
    rows = []
    for t in tasks:
        status_icon = STATUS_EMOJI.get(t["status"], "")
        priority_icon = PRIORITY_EMOJI.get(t["priority"], "")
        tags_str = ", ".join(t["tags"]) if t["tags"] else "-"
        due = t["due_date"] or "-"
        rows.append([t["id"], status_icon, priority_icon, t["title"], tags_str, due])

    click.echo(tabulate(rows, headers=headers, tablefmt="simple"))
    click.echo(f"\n📊 共 {len(tasks)} 个任务")


@cli.command()
@click.argument("task_id")
@click.pass_context
def done(ctx, task_id):
    """标记任务完成"""
    todo = ctx.obj["todo"]
    result = todo.complete(task_id)
    if result:
        click.echo(f"✅ 任务已完成: {result['title']}")
    else:
        click.echo(f"❌ 未找到任务: {task_id}")


@cli.command()
@click.argument("task_id")
@click.pass_context
def start(ctx, task_id):
    """标记任务为进行中"""
    todo = ctx.obj["todo"]
    result = todo.start(task_id)
    if result:
        click.echo(f"🔄 任务进行中: {result['title']}")
    else:
        click.echo(f"❌ 未找到任务: {task_id}")


@cli.command()
@click.argument("task_id")
@click.option("--title", default=None, help="新标题")
@click.option("--priority", "-p", type=click.Choice(["high", "medium", "low"]), default=None, help="新优先级")
@click.option("--tag", "-t", multiple=True, help="新标签")
@click.option("--due", "-d", default=None, help="新截止日期")
@click.option("--desc", default=None, help="新描述")
@click.pass_context
def update(ctx, task_id, title, priority, tag, due, desc):
    """更新任务信息"""
    todo = ctx.obj["todo"]
    tags = list(tag) if tag else None
    result = todo.update(task_id, title=title, priority=priority, tags=tags, due_date=due, description=desc)
    if result:
        click.echo(f"📝 任务已更新: {result['title']}")
    else:
        click.echo(f"❌ 未找到任务: {task_id}")


@cli.command()
@click.argument("task_id")
@click.pass_context
def remove(ctx, task_id):
    """删除任务"""
    todo = ctx.obj["todo"]
    if todo.remove(task_id):
        click.echo(f"🗑️  任务已删除: {task_id}")
    else:
        click.echo(f"❌ 未找到任务: {task_id}")


@cli.command()
@click.pass_context
def summary(ctx):
    """查看任务摘要"""
    todo = ctx.obj["todo"]
    s = todo.summary()

    click.echo("📊 任务摘要")
    click.echo("=" * 30)
    click.echo(f"  总计:     {s['total']}")
    click.echo(f"  ⏳ 待办:   {s['pending']}")
    click.echo(f"  🔄 进行中: {s['in_progress']}")
    click.echo(f"  ✅ 已完成: {s['completed']}")
    click.echo(f"  ⚠️  已过期: {s['overdue']}")
    click.echo()
    click.echo("按优先级（未完成）:")
    click.echo(f"  🔴 高: {s['priority']['high']}")
    click.echo(f"  🟡 中: {s['priority']['medium']}")
    click.echo(f"  🟢 低: {s['priority']['low']}")


@cli.command()
@click.pass_context
def clear(ctx):
    """清除所有已完成任务"""
    todo = ctx.obj["todo"]
    count = todo.clear_completed()
    if count > 0:
        click.echo(f"🧹 已清除 {count} 个已完成任务")
    else:
        click.echo("📭 没有已完成的任务需要清除")


if __name__ == "__main__":
    cli()
