---
name: easy-boss
description: Break long Codex tasks into small checkpoints and keep the user updated with concise mobile or web progress reports. Use when a task is long-running, multi-step, likely to involve many tool calls, may continue while the user is away, or when the user asks for phone notifications, progress reports, checkpoint updates, task slicing, automatic work reporting, or setup of a notification connection.
---

# Easy Boss v0

Version: `v0`

Use this skill to turn a long task into visible, low-anxiety progress: plan it, set up a notification channel if needed, execute in checkpoints, and send short reports only when they are useful.

## First-Run Setup

Before substantial long-running work, ensure the user has a way to receive reports.

1. Run `python scripts/setup_notifications.py --task "<short task>" --action "<current action>"` from this skill directory if no notification channel is known for this user.
2. Paste the printed start-work message into the Codex chat immediately. It must say work has started, what Codex is executing, which mobile app/web link can show reports, the bundled Android APK path, and the report frequency.
3. Continue the task after setup; do not send a routine mobile start notification and do not wait for the user unless the task explicitly requires confirmation.

If setup has already been done and the user needs the connection link again, run:

```bash
python scripts/notify_phone.py "Codex: 连接方式" "我正在显示当前进度汇报连接方式。" --show-connection --task "<short task>" --action "<current action>" --force
```

## Core Workflow

1. Classify the task as long if it likely takes more than 5 minutes, uses many tool calls, touches multiple systems, waits on builds/tests/network, or has unclear failure points.
2. Run a small reconnaissance pass before planning deeply: inspect only the minimum files, commands, logs, or state needed to choose the next stage.
3. Create a compact rolling plan with 3-5 coarse checkpoints using the normal `update_plan` tool when available.
4. Fully expand only the current checkpoint; leave later checkpoints as short intent labels until the current stage finishes.
5. Work checkpoint by checkpoint; after each small-stage task is actually completed, compress findings into a short note, update the plan, and send a short phone/web report.
6. If stuck inside one checkpoint with no meaningful progress, stop and immediately send a confirmation request instead of silently continuing.
7. Send a final notification when the whole task is complete, blocked, or handed back to the user.

## Notification Rules

Send notifications only at these moments:

- **Stage complete**: after each planned small-stage task finishes and there is concrete progress to report.
- **Stuck / no progress**: immediately when one checkpoint is not advancing and another blind attempt would be guesswork.
- **User decision needed**: when a choice materially changes scope, safety, cost, risk, credentials, or live-system behavior.
- **Failure / blocked**: when retries are exhausted, validation cannot pass, or user action is needed.
- **Finish**: when all work is complete or when stopping with a clear handoff.

Respect the frequency window:

- Send routine progress reports at most once every 5 minutes.
- If work continues with no report for 10 minutes, send a brief heartbeat even if the current stage is not finished.
- Send stuck, user-confirmation, blocked, and final-complete messages immediately with `--force`.
- Do not notify merely because work has started; the first non-setup notification should be a completed stage, stuck request, or heartbeat after 10 minutes.
- Keep only a small local send history; after every 4 successfully sent messages, delete the oldest stored record.

## Token-Aware Task Slicing

Use rolling planning to avoid spending excessive tokens on premature detail:

Read `references/token_aware_planning.md` when the task is especially broad, ambiguous, or likely to require repeated exploration.

- **Recon first**: spend one short pass discovering the task shape before writing a detailed plan.
- **Coarse outer plan**: keep only 3-5 checkpoints visible at once.
- **Expand one stage**: detail only the current checkpoint; defer detailed substeps for future checkpoints.
- **Summarize then discard**: after a stage, retain only decisions, changed files/state, validation evidence, blockers, and next action.
- **Prefer targeted reads**: use search, filenames, status commands, and small snippets before opening large files or logs.
- **Cap retries**: after one diagnosis and one harmless retry, either change strategy or ask for confirmation.
- **Avoid speculative branches**: do not design multiple full solutions unless the choice materially affects safety, cost, or outcome.
- **Ask early when scope is ambiguous**: one precise question is cheaper than exploring several incompatible paths.

Before each checkpoint, define these four fields in brief internal notes or a concise user-visible plan:

```text
Goal: what this stage proves or changes
Evidence: command/file/output that verifies it
Limit: when to stop or ask
Next: what follows if successful
```

## Stuck Detection

Treat a checkpoint as stuck when any of these are true:

- The same error or blocking condition repeats after a reasonable diagnosis and one harmless retry.
- A command, download, build, test, or remote operation exceeds the expected time and produces no useful new output.
- Required information, credentials, approval, or external state is missing and cannot be safely inferred.
- Continuing would require risky changes outside the user's requested scope.

When stuck, send a `Codex: 卡住了` report, briefly say what is blocked, and ask the user to return to the chat to confirm the next step.

## Message Style

Keep messages short and useful:

For the initial Codex chat message after setup, use this shape:

```text
工作已经开始，我正在执行：<任务名>。
你可以在手机上的 ntfy App，或通过这个链接查看我的工作报告：<链接>
Android 用户可以直接使用随 skill 打包的安装包：<assets/ntfy-android.apk>
我会在小阶段完成、卡住、需要确认、超过 10 分钟无消息、或任务结束时汇报；普通进度最多每 5 分钟一次。
```

For mobile/web notification messages:

- Title: `Codex: 阶段完成`, `Codex: 卡住了`, `Codex: 需要确认`, or `Codex: 完成`.
- Body: one sentence with `done → next` or `problem → ask`.
- Do not include secrets, tokens, passwords, private keys, long logs, or sensitive file contents.

Examples:

```text
Title: Codex: 阶段完成
Body: 第 1 步已完成：项目结构已确认，接下来修改配置。
```

```text
Title: Codex: 卡住了
Body: 验证命令连续失败且原因不明，请回到对话确认下一步。
```

```text
Title: Codex: 需要确认
Body: 部署会改动防火墙规则，请回到对话确认是否继续。
```

## How To Send

Read `references/phone_notification.md` when you need exact setup commands, reset behavior, or custom ntfy server options.

Preferred command from this skill directory:

```bash
python scripts/notify_phone.py "Codex: 阶段完成" "当前小阶段已完成，接下来执行下一步。"
```

Use forced sending for final completion, stuck, blocked, or confirmation-needed messages:

```bash
python scripts/notify_phone.py "Codex: 完成" "任务已完成，请回到对话查看结果。" --force
```

Use heartbeat only when 10 minutes pass without any report while work is still active:

```bash
python scripts/notify_phone.py "Codex: 仍在处理" "我还在当前阶段工作，暂无需要你操作的事项。" --force
```

If the helper fails, continue the task when safe and mention the notification failure in normal chat.

## Task Slicing Pattern

Slice work into checkpoints that produce visible evidence:

- **Orient**: inspect context, constraints, files, services, or existing state.
- **Design**: choose the smallest safe path and identify risks.
- **Implement**: make focused changes or execute the planned operations.
- **Validate**: run targeted checks, tests, status commands, or manual verification.
- **Handoff**: summarize changes, evidence, remaining risks, and next actions.

For very large tasks, use nested checkpoints but expand only the active branch. Complete one feature, service, file group, or operational phase at a time before opening the next branch.

## Recovery Behavior

When a command fails:

1. Diagnose locally with the least disruptive read-only checks.
2. Retry only when the cause is clear or the retry is harmless.
3. If the checkpoint still has no meaningful progress after diagnosis or a harmless retry, send a `Codex: 卡住了` report with `--force` and request user confirmation.
4. Keep the final chat concise: state what failed, what was tried, and what the user should do next.

Never modify unrelated systems simply to make progress. For live servers, avoid changing firewall, proxy, SSH, billing, or account settings unless the user explicitly asked for that operation.
