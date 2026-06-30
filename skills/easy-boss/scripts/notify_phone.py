#!/usr/bin/env python3
"""Send a phone progress report, auto-creating a no-server ntfy channel if needed."""

from __future__ import annotations

import argparse
import sys

from reporter_common import connection_instructions, ensure_config, ntfy_publish, print_error, should_send


def main() -> int:
    parser = argparse.ArgumentParser(description="Send a short progress report to the user's phone/web notification channel.")
    parser.add_argument("title", nargs="?", default="Codex 工作汇报")
    parser.add_argument("message", nargs="?", default="任务状态有更新")
    parser.add_argument("--server-url", default="https://ntfy.sh")
    parser.add_argument("--topic", default=None)
    parser.add_argument("--reset", action="store_true", help="create a new topic before sending")
    parser.add_argument("--show-connection", action="store_true", help="print phone connection instructions")
    parser.add_argument("--min-interval", type=int, default=300, help="minimum seconds between routine reports; default 300")
    parser.add_argument("--force", action="store_true", help="send immediately, bypassing the routine report cooldown")
    parser.add_argument("--task", default="这个长任务", help="short description used when printing connection instructions")
    parser.add_argument("--action", default="继续执行当前阶段", help="current action used when printing connection instructions")
    args = parser.parse_args()

    config, created, path = ensure_config(server_url=args.server_url, topic=args.topic, reset=args.reset)
    if created or args.show_connection:
        print(connection_instructions(config, path, task=args.task, action=args.action))

    allowed, wait_seconds = should_send(args.min_interval, force=args.force or created)
    if not allowed:
        print(f"通知已跳过：距离上次发送不足 {args.min_interval} 秒，还需等待 {wait_seconds} 秒。", file=sys.stderr)
        return 0

    try:
        ntfy_publish(config, args.title, args.message)
    except Exception as exc:
        print_error(str(exc))
        return 1

    if created:
        print("通知通道已自动创建，且本次消息已发送。", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
