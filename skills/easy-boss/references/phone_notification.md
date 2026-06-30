# Phone Notification Setup

Use this reference when the task requires mobile or web progress reports.

## Default no-server mode

This skill does not require the user to own a VPS or have ntfy preinstalled. On first use, run setup with a task/action description:

```bash
python scripts/setup_notifications.py --task "<short task>" --action "<current action>"
```

The setup script will:

- Generate a random `ntfy.sh` topic.
- Save it locally in the user's config directory.
- Print a Codex chat start-work message with the current task, current action, report link, ntfy subscription details, bundled Android APK path, and report frequency.
- Avoid sending a test notification unless `--test` is explicitly used.

The user can receive updates in these ways:

- Open the printed `https://ntfy.sh/<topic>` URL on a phone browser.
- Android: install the bundled `assets/ntfy-android.apk`, then subscribe to the printed Server + Topic.
- iPhone: install ntfy from the App Store, then subscribe to the printed Server + Topic.

## Sending reports

Send only after a small-stage task completes, when stuck, when user confirmation is needed, when 10 minutes pass without any report during active work, or when the whole task finishes.

Frequency rules:

- Routine stage reports are limited to once every 5 minutes by default.
- If work continues for 10 minutes without any report, send a heartbeat with `--force`.
- Final completion, stuck, blocked, and confirmation-needed messages should use `--force`.
- Local send history is pruned automatically: after every 4 successful sends, the oldest stored record is removed.

Preferred command from the skill directory:

```bash
python scripts/notify_phone.py "Codex 工作汇报" "当前进度一句话"
```

Forced immediate send:

```bash
python scripts/notify_phone.py "Codex: 完成" "任务已完成，请回到对话查看结果。" --force
```

From Windows PowerShell with an absolute path:

```powershell
python "$env:USERPROFILE\.codex\skills\easy-boss\scripts\notify_phone.py" "Codex 工作汇报" "当前进度一句话"
```

If no config exists, `notify_phone.py` automatically creates one and prints connection instructions.

## Resetting the channel

Use this when the user wants a new private-looking topic:

```bash
python scripts/setup_notifications.py --reset
```

## Optional custom ntfy server

If the user has a self-hosted ntfy server:

```bash
python scripts/setup_notifications.py --server-url https://notify.example.com --reset
```

## Safety

- Keep messages short: one outcome, one next step.
- Do not send secrets, tokens, passwords, private keys, full logs, or sensitive file contents.
- Public `ntfy.sh` topics are unlisted but not a substitute for end-to-end secret storage; treat topic names as bearer URLs.
- If notification fails, continue the task when safe and mention the failure in normal chat.
