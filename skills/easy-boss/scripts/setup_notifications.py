#!/usr/bin/env python3
"""Create a no-server phone notification channel and print connection details."""

from __future__ import annotations

import argparse

from reporter_common import connection_instructions, ensure_config, ntfy_publish


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up phone progress reports for long Codex tasks.")
    parser.add_argument("--server-url", default="https://ntfy.sh", help="ntfy server URL; defaults to public ntfy.sh")
    parser.add_argument("--topic", default=None, help="custom topic; by default a random private-looking topic is generated")
    parser.add_argument("--reset", action="store_true", help="replace any existing local notification config")
    parser.add_argument("--test", action="store_true", help="send a setup test notification after printing connection details")
    parser.add_argument("--task", default="这个长任务", help="short description of the task being started")
    parser.add_argument("--action", default="拆分任务并执行第一个阶段", help="what Codex is doing now")
    args = parser.parse_args()

    config, created, path = ensure_config(server_url=args.server_url, topic=args.topic, reset=args.reset)
    print(connection_instructions(config, path, task=args.task, action=args.action))

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
