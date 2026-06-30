from __future__ import annotations

import json
import os
import secrets
import time
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

APP_NAME = "codex-easy-boss"
DEFAULT_SERVER_URL = "https://ntfy.sh"
PRUNE_EVERY_N_MESSAGES = 4
SKILL_ROOT = Path(__file__).resolve().parents[1]
BUNDLED_ANDROID_APK = SKILL_ROOT / "assets" / "ntfy-android.apk"


def config_dir() -> Path:
    override = os.environ.get("CODEX_REPORT_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / APP_NAME
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / APP_NAME
    return Path.home() / ".config" / APP_NAME


def config_path() -> Path:
    return config_dir() / "config.json"


def state_path() -> Path:
    return config_dir() / "state.json"


def normalize_server_url(value: str) -> str:
    value = value.strip().rstrip("/")
    if not value:
        return DEFAULT_SERVER_URL
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value.rstrip("/")


def make_topic() -> str:
    return "codex-report-" + secrets.token_urlsafe(18).replace("_", "x").replace("-", "z")


def make_public_ntfy_config(server_url: str = DEFAULT_SERVER_URL, topic: str | None = None) -> dict[str, Any]:
    return {
        "provider": "ntfy",
        "server_url": normalize_server_url(server_url),
        "topic": topic or make_topic(),
    }


def load_config() -> dict[str, Any] | None:
    path = config_path()
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_config(config: dict[str, Any]) -> Path:
    directory = config_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = config_path()
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_state() -> dict[str, Any]:
    path = state_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(state: dict[str, Any]) -> Path:
    directory = config_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = state_path()
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def should_send(min_interval_seconds: int, force: bool = False) -> tuple[bool, int]:
    if force or min_interval_seconds <= 0:
        return True, 0
    state = load_state()
    now = int(time.time())
    last_sent = int(state.get("last_sent_at", 0) or 0)
    elapsed = now - last_sent
    if elapsed >= min_interval_seconds:
        return True, 0
    return False, min_interval_seconds - elapsed


def prune_history(history: list[dict[str, Any]], sent_count: int) -> list[dict[str, Any]]:
    if sent_count > 0 and sent_count % PRUNE_EVERY_N_MESSAGES == 0 and history:
        return history[1:]
    return history


def mark_sent(title: str = "", message: str = "") -> None:
    state = load_state()
    now = int(time.time())
    sent_count = int(state.get("sent_count", 0) or 0) + 1
    history = state.get("history", [])
    if not isinstance(history, list):
        history = []
    history.append({
        "sent_at": now,
        "title": title[:80],
        "message": message[:200],
    })
    history = prune_history(history, sent_count)
    state["last_sent_at"] = now
    state["sent_count"] = sent_count
    state["history"] = history
    save_state(state)


def ensure_config(server_url: str = DEFAULT_SERVER_URL, topic: str | None = None, reset: bool = False) -> tuple[dict[str, Any], bool, Path]:
    if not reset:
        current = load_config()
        if current:
            return current, False, config_path()
    config = make_public_ntfy_config(server_url=server_url, topic=topic)
    path = save_config(config)
    return config, True, path


def topic_url(config: dict[str, Any]) -> str:
    server_url = normalize_server_url(str(config["server_url"]))
    topic = urllib.parse.quote(str(config["topic"]), safe="")
    return f"{server_url}/{topic}"


def android_apk_line() -> str:
    if BUNDLED_ANDROID_APK.exists():
        return f"Android 安装包：{BUNDLED_ANDROID_APK}"
    return "Android 安装包：未随 skill 打包；可使用应用商店或项目发布页安装 ntfy。"


def ntfy_publish(config: dict[str, Any], title: str, message: str, priority: str = "default") -> None:
    server_url = normalize_server_url(str(config["server_url"]))
    priority_value: int | str
    priority_map = {"min": 1, "low": 2, "default": 3, "normal": 3, "high": 4, "max": 5}
    if isinstance(priority, str):
        priority_value = priority_map.get(priority.lower(), 3)
    else:
        priority_value = priority
    payload = {
        "topic": str(config["topic"]),
        "title": title,
        "message": message,
        "priority": priority_value,
        "tags": ["computer"],
    }
    request = urllib.request.Request(
        server_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            response.read()
        mark_sent(title, message)
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to publish notification to {topic_url(config)}: {exc}") from exc


def connection_instructions(config: dict[str, Any], path: Path | None = None, task: str = "这个长任务", action: str = "拆分任务并执行第一个阶段") -> str:
    url = topic_url(config)
    topic = str(config["topic"])
    server_url = normalize_server_url(str(config["server_url"]))
    config_line = f"配置文件：{path}" if path else f"配置文件：{config_path()}"
    apk_line = android_apk_line()
    return f"""工作已经开始，我正在执行：{task}。
我会先进行小范围侦察，把任务拆成几个检查点，然后优先展开当前阶段，避免浪费 token。
当前动作：{action}。

你可以在手机上通过以下方式查看我的工作报告：

1. 最快方式：用手机浏览器打开这个链接
   {url}

2. App 方式：安装 ntfy，然后添加订阅
   Server: {server_url}
   Topic:  {topic}

3. Android 用户可以直接使用随 skill 打包的安装包
   {apk_line}

4. iPhone 用户可从 App Store 安装 ntfy
   https://apps.apple.com/app/ntfy/id1625396347

汇报频率：普通进度最多每 5 分钟 1 次；超过 10 分钟没消息会发心跳；完成、卡住或需要你确认时会立刻通知。

{config_line}
"""


def print_error(message: str) -> None:
    print(message, file=sys.stderr)
