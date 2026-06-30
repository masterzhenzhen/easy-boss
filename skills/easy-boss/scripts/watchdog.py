#!/usr/bin/env python3
"""Background heartbeat watchdog for Easy Boss tasks."""

from __future__ import annotations

import argparse
import time

from reporter_common import load_config, load_state, ntfy_publish, print_error, update_state


def main() -> int:
    parser = argparse.ArgumentParser(description="Send heartbeat reports if Easy Boss forgets to report for too long.")
    parser.add_argument("--interval", type=int, default=60, help="seconds between watchdog checks")
    parser.add_argument("--heartbeat-after", type=int, default=600, help="seconds without any report before heartbeat")
    parser.add_argument("--max-runtime", type=int, default=21600, help="maximum watchdog runtime in seconds")
    args = parser.parse_args()

    started = int(time.time())
    update_state(watchdog_started_at=started, watchdog_stop=False)

    while True:
        now = int(time.time())
        state = load_state()
        if state.get("watchdog_stop") or not state.get("task_active", True):
            return 0
        if now - started > args.max_runtime:
            update_state(watchdog_stop=True, task_active=False)
            return 0

        last_sent = int(state.get("last_sent_at", 0) or 0)
        last_progress = int(state.get("last_progress_at", 0) or 0)
        last_activity = max(last_sent, int(state.get("task_started_at", started) or started))
        if last_progress > last_activity and now - last_sent < args.heartbeat_after:
            last_activity = last_progress

        if now - last_activity >= args.heartbeat_after:
            config = load_config()
            if not config:
                print_error("watchdog skipped heartbeat: missing config")
                return 1
            task = state.get("task", "当前任务")
            try:
                ntfy_publish(
                    config,
                    "Codex: 仍在处理",
                    f"我还在处理：{task}。目前暂无需要你操作的事项。",
                    priority="default",
                )
            except Exception as exc:
                print_error(str(exc))
            update_state(last_progress_at=int(time.time()))

        time.sleep(max(5, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
