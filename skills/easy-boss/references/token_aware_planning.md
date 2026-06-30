# Token-Aware Long Task Planning

Use this reference when a long task is vague, broad, or likely to consume a lot of context.

## Rolling plan rule

Do not fully plan every detail up front. Use this loop:

```text
recon → coarse plan → expand current checkpoint → execute → compress findings → re-plan next checkpoint
```

## Recon budget

During the first pass:

- Prefer `rg`, file listings, status commands, and narrow log tails.
- Avoid opening whole large files unless search shows they are relevant.
- Avoid reading generated assets, dependency folders, build outputs, lockfiles, or large logs unless directly needed.
- Stop recon once you can name the next concrete checkpoint.

## Checkpoint contract

Before each checkpoint, know:

```text
Goal: one concrete outcome
Evidence: how to verify it
Limit: when to stop or ask
Next: likely follow-up if successful
```

## Compression rule

After each checkpoint, keep only:

- Decisions made.
- Files, services, commands, or state changed.
- Validation evidence.
- Remaining blocker or next action.

Drop exploratory dead ends unless they affect future choices.

## Stop rules

Stop and ask or notify when:

- The same blocker appears after one diagnosis and one harmless retry.
- The task scope is ambiguous enough to cause multiple incompatible paths.
- Continuing would require risky live-system, credential, billing, or destructive changes.
- More reading is only curiosity, not needed for the next checkpoint.
