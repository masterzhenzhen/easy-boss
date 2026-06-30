# Easy Boss v0.1

Easy Boss is a Codex skill for long-running tasks. It splits broad work into token-aware checkpoints and sends quiet progress reports to a phone or web link through ntfy.

## Features

- Rolling task planning to avoid wasting tokens on premature detail.
- First-run setup that generates a private-looking ntfy topic and prints a mobile report link.
- Android APK bundled in the skill for users who do not want to download ntfy separately.
- Progress reports capped at one routine message every 5 minutes.
- Heartbeat after 10 minutes without updates during active work.
- Immediate reports for completion, blocked states, stuck checkpoints, and user-confirmation moments.
- Local send history pruning after every 4 successful messages.

## Install

### Windows PowerShell

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### macOS / Linux

From the repository root:

```bash
bash ./install.sh
```

The installer copies `skills/easy-boss` into your Codex skills directory:

- Windows: `%USERPROFILE%\.codex\skills\easy-boss`
- macOS/Linux: `~/.codex/skills/easy-boss`

Restart Codex or open a new conversation after installation.

## Use

Ask Codex:

```text
Use $easy-boss to execute this long task and keep me updated.
```

Or in Chinese:

```text
使用 $easy-boss 执行这个长任务，并持续给我汇报进度。
```

## Android app

The skill includes a bundled ntfy Android APK at:

```text
skills/easy-boss/assets/ntfy-android.apk
```

This APK is a third-party ntfy app build. See `THIRD_PARTY_NOTICES.md` before redistributing.

## License

Easy Boss code and skill text are released under the MIT License. The bundled ntfy Android APK is third-party software and remains under its upstream license terms.

