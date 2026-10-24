# CLAUDE.md

This repo is a fork of a collection of agent skills for video work (upstream name: cstack). Each skill is a folder under `skills/` with a `SKILL.md` that Claude loads when the task matches its `description`.

## Layout

- `skills/<name>/SKILL.md`: the skill's instructions. Supporting material sits beside it in `references/`, `styles/`, `scripts/`, `templates/`, `assets/` and `evals/`. Read those only when `SKILL.md` points to them.
- `examples/realistic-3d/`: a runnable Remotion + three.js example shot.
- `icons/`: "Charade" animated line icons (plain SVG and CSS, no dependencies).

## Which skill to use

| Task | Skill |
| --- | --- |
| Brainstorm video ideas, write or tighten a script, learn from a posted video's analytics | `video-script` (writes the script, then stops) |
| Edit camera footage: talking heads, reels, skits, demos, screen recordings | `video-edit` |
| Make an animated film in code (Remotion, 2D or 3D) | `animated-video` |
| Reuse footage, images, music, characters or 3D sets across projects | `asset-library` (shared by video-edit and animated-video) |
| Review a finished, incomplete or failed session and propose instruction improvements | `reflect` |
| Test a change to skills, instructions or workflow against the current version | `rsi` |

The deliverable decides who owns the final timeline. An edit with animated shots belongs to `video-edit`, which asks `animated-video` for the shots. An animated film belongs to `animated-video`, even with one camera insert.

## Working rules

- Keep each skill self-contained and focused on one recurring need.
- Skills stay general. Anything personal (audience, taste, numbers, machine, accounts) goes in the skill's `~/.<skill>/profile.md`, never in the repo. Before editing a skill, ask whether the change would be right for a stranger making their own videos.
- Never commit transcripts, credentials, personal project history, machine-specific paths, or the creator's own footage or likeness.
- Bundle assets only if their license allows redistribution. Preserve attribution for third-party contributions and confirm license compatibility.
- Do not edit installed reusable instructions without the user's approval. `reflect` and `rsi` propose changes first.
- New or changed skills should come with examples or evaluation cases (see `skills/*/evals/evals.json`) that expose meaningful mistakes.

## Requirements

- video-edit: FFmpeg, Python 3, uv (runs `scripts/preflight.py` on first use). DaVinci Resolve is optional; without it, renders use FFmpeg.
- animated-video: shell, Node.js with Remotion, FFmpeg/ffprobe, Python 3 with faster-whisper. Blender is optional for realistic 3D.
- asset-library: Python 3 and FFmpeg.
- video-script: Python 3 with Pillow and numpy for `scripts/retention_curve.py`.

## Checks

```sh
python3 skills/video-edit/scripts/test_make_captions.py
python3 skills/asset-library/scripts/test_library.py
```

These do not validate a Resolve install, listening quality, visual taste, or an end-to-end edit.

## Installing the skills in Claude Code

From the repo root, once per skill (`reflect`, `rsi`, `video-edit`, `animated-video`, `video-script`, `asset-library`):

```sh
skill_name=video-script
mkdir -p "$HOME/.claude/skills"
test ! -e "$HOME/.claude/skills/$skill_name" && \
  ln -s "$PWD/skills/$skill_name" "$HOME/.claude/skills/$skill_name"
```

Linking follows changes in this checkout. Copy the folder instead if you want a frozen version. Reload the Claude Code session afterwards.
