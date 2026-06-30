#!/usr/bin/env python3
"""Create a no-server phone notification channel and print connection details."""

from __future__ import annotations

import argparse
import subprocess
import sys

from pathlib import Path

from reporter_common import (
    connection_instructions,
    ensure_config,
    ntfy_publish,
    remember_watchdog,
    start_task_state,
    stop_existing_watchdog,
    watchdog_log_path,
)


def start_watchdog() -> int:
    script = Path(__file__).resolve().with_name("watchdog.py")
    log_path = watchdog_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = log_path.open("a", encoding="utf-8")
    kwargs = {
        "stdout": log_file,
        "stderr": subprocess.STDOUT,
        "stdin": subprocess.DEVNULL,
    }
    if sys.platform.startswith("win"):
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    process = subprocess.Popen([sys.executable, str(script)], **kwargs)
    remember_watchdog(process.pid)
    return process.pid


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up phone progress reports for long Codex tasks.")
    parser.add_argument("--server-url", default="https://ntfy.sh", help="ntfy server URL; defaults to public ntfy.sh")
    parser.add_argument("--topic", default=None, help="custom topic; by default a random private-looking topic is generated")
    parser.add_argument("--reuse", action="store_true", help="reuse the existing local notification config instead of creating a new task topic")
    parser.add_argument("--test", action="store_true", help="send a setup test notification after printing connection details")
    parser.add_argument("--no-watchdog", action="store_true", help="do not start the background heartbeat watchdog")
    parser.add_argument("--task", default="这个长任务", help="short description of the task being started")
    parser.add_argument("--action", default="拆分任务并执行第一个阶段", help="what Codex is doing now")
    args = parser.parse_args()

    stop_existing_watchdog()
    config, created, path = ensure_config(server_url=args.server_url, topic=args.topic, reset=not args.reuse)
    start_task_state(task=args.task)
    print(connection_instructions(config, path, task=args.task, action=args.action))
    if args.no_watchdog:
        print("后台汇报守护进程未启动：当前为显式 no-watchdog 模式。")
    else:
        watchdog_pid = start_watchdog()
        print(f"后台汇报守护进程已启动：PID {watchdog_pid}。如果 Codex 忘记汇报，超过 10 分钟会自动发心跳。")

    if args.test:
        title = "Codex: 通知通道已就绪"
        body = "这个页面或 App 订阅成功后，长任务进度会发到这里。"
        ntfy_publish(config, title, body)
        if created:
            print("已发送一条测试通知。")
        else:
            print("已使用现有配置发送一条测试通知。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
