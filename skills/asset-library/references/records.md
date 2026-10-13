# Records and commands

The contract `scripts/library.py` implements. `scripts/test_library.py` exercises it on a
throwaway library.

## Storage

- **Root**: one folder. `library.db` (SQLite, WAL mode), `media/` for ingested files,
  `bundles/` for code, character and model versions, `previews/`, and `exports/`. That is the
  layout `init` creates; an existing library may keep media anywhere under its root, and older
  records may hold absolute paths outside it, which stay as they are.
- **Root lookup**: `--root`, else `ASSET_LIBRARY_ROOT`, else a ``Root: `PATH` `` line in
  `~/.asset-library/profile.md`.
- **Authority**: the database. Every write goes through a command in one transaction, so two
  agents recording uses at once cannot corrupt it or half-write a record; a writer waits up to
  30 s for another to finish. Files are published before the row that exposes them (see
  [publishing a version](#publishing-a-version)).
- **Import sources**: JSON catalog files (`[{id, kind, title, path, …}]`, or `{"assets": [...]}`)
  are read by `import`; relative paths are relative to the library root. Import adds IDs the
  database does not have, marks one whose file matches an existing asset as its duplicate
  (`canonical_id`), skips entries whose file is missing, and reports fields that differ for IDs
  it already has. A new ID outside the ID rules or a kind outside the vocabulary, and `tags` that
  are neither a list nor a comma-separated string, are reported as `invalid` and not added;
  existing rows are not re-judged. It changes an existing row only with `--update ID`, and then
  only the fields the entry states. Unknown keys are kept in `extra_json`. Nothing deletes rows.
- **Backups and portability**: `export` writes `exports/library.json` (every row of every table,
  including tables a local adapter added; only the derived search index is left out; a BLOB
  value is written as `{"base64": "…"}`) and the browsable `exports/index.html`. Copy the root
  folder to move the library.
- **Schema**: `meta.schema_version` (now 2). Opening an older database first writes
  `library.db.bak-<old>-<timestamp>` with SQLite's backup API, then migrates by adding tables
  and nullable columns in one transaction. Migrations never drop or rewrite existing rows. A
  newer or non-integer version is refused and left unchanged.
- **From code**: a local adapter can `import library` and use `Library(root)` and `main(argv,
  root=…, extend=…)`; the module docstring lists the interface.

## Assets

| Field | Notes |
| --- | --- |
| `id` | Stable, lowercase, hyphenated (`a-z0-9._-`). Never reused or renamed. |
| `kind` | `image`, `video`, `sfx`, `music`, `character`, `code`, `model` |
| `title`, `tags`, `planned_use` | What it is and what it can do. For sound, `planned_use` describes the feeling it gives, not where to cut it. |
| `path` | Media: the file. Bundles: the newest version's entry file, for browsing only; uses name a version. |
| `work_id`, `variant_role` | Groups variants of one original (`original`, `extended`, `ducked-bed`, `crop`). |
| `canonical_id` | Set when the file is byte-identical to another asset's; search hides it. |
| provenance | `source_url`, `creator`, `license`, `license_url`, `rights_status` (`verified`, `own work`, `unknown`, …), `downloaded_at`, `source_in`/`source_out`, and older free-text fields such as `review_notes` |
| `archived` | Hidden from search; kept for past uses. |
| `dimensions` | Bundles only, optional: `{"x": m, "y": m, "z": m, "up": "y"}` for models, sets and characters whose scale must match. |

Required by kind:

| Kind | Required beyond id, kind, title, path | Set by |
| --- | --- | --- |
| image, video | sha256, width, height; a preview | `ingest` (SVG: no size or preview) |
| sfx, music | sha256, duration, sample rate; peak level | `ingest` (peak empty for digital silence) |
| code, character | a bundle version with entry, example, preview and a validation command (or a recorded reason for none); `planned_use` | `register` |
| model | a bundle version with entry and preview; `planned_use`. Validation optional | `register` |

Media kinds need no validation command and no example; their content hash is their version. A
re-encode or crop is a new asset in the same `work_id`, not a new version.

## Versions and bundles

```text
bundles/<id>/<short-version>/
  bundle.json     {id, kind, version, content, record}
  files/…         snapshot of every listed file
```

`bundle.json` holds two groups of fields:

- **Content**, which defines the version: `entry`; `files` (path, sha256, size); `dependencies`
  (declared with `--dependency`, such as `npm:three@0.170.0`, `py:numpy==2.1`, `tool:ffmpeg`;
  a lockfile listed in `files` pins the rest); `example`; `preview`; `validate` (below);
  `dimensions` when given. `entry`, `example` and `preview` are files in `files`.
- **Record**, which does not: `origin`, `created_at`, `title`, `planned_use`. Notes live in the
  database, not here.

The **version** is the full SHA-256 of the canonical JSON (sorted keys, no whitespace) of the
content fields. The same content always gives the same version; any changed file, dependency,
entry, example, preview or validation setting gives a new one. Commands print a 12-hex short
form and accept any unique prefix of at least 4 hex; the database stores the full digest and
every lookup compares it, reporting an ambiguous prefix with its candidates. If a new version's
12-hex prefix is already taken by another version of the same asset, its folder name lengthens
until unique.

- Files come from `--files` (files, folders or quoted globs) under `--source`. A path that leaves
  the source, including through a symlink, is refused. Folders skip `.git`, `node_modules`,
  `__pycache__` and `.venv`.
- `origin` records where it came from: the source folder with its git commit and whether the
  tree was dirty, or the `--origin` text, such as a published skill and its commit
  (`cstack@<commit>:skills/animated-video/templates/parts/…`). A skill-relative path alone is
  not a version, because the skill changes; the snapshot is.
- `validate` is `{command, cwd, setup, env, timeout_s}`. `cwd` is relative to the snapshot;
  `setup` installs the pinned dependencies (`npm ci` against the captured lockfile); `env` lists
  the only variables passed through besides `PATH`, `HOME`, `LANG` and `TMPDIR`; `timeout_s`
  bounds each of setup and command. Validation runs in a fresh temporary copy of the published
  snapshot, never in the project folder, so it tests what was captured. Its result is the
  version's `validation` (`passed`, `failed`, `not-run`) and a `test` note with the exit status
  and output tail. Validation shows the command exits 0 from the snapshot; it does not judge how
  the result looks, and a setup that needs the network or a licensed tool fails without them.
- **Legacy**: assets registered before bundles existed have no known historical version. Their
  past uses keep `artifact_version` empty, meaning unknown. A bundle captured from today's files
  is a new version with today's `created_at`; it is never back-dated onto old uses. The first
  bundle moves the asset's `path` and preview into `bundles/`; the old pointer is kept in a
  `caveat` note.

### Publishing a version

`register` must never expose a version whose files are partial or differ from its digest. A
database transaction alone cannot make a file copy atomic, so:

1. **Stage.** Hash the listed files, then copy them into `bundles/.staging/<random>/files/` on
   the same filesystem as the library.
2. **Verify.** Hash the copies; refuse if any differs from the hash read before copying (the
   source changed mid-copy). Write `bundle.json`; compute the version.
3. **Publish.** If `bundles/<id>/<short-version>/` already holds the same full digest, discard
   the staging folder and use it (registering twice is harmless). Otherwise rename the staging
   folder into place; a rename on one filesystem is atomic.
4. **Record.** In one transaction, insert the version row. Only now does `search` or `show` see
   it. Then run validation and store its result.
5. **Clean up on failure.** A failure before step 4 removes the staging folder. A published
   folder with no row (a crash between steps 3 and 4) is reported by `check` as an orphan and
   adopted by the next `register` of the same content, after its files are re-verified; it is
   never served. Registering an identical version whose validation failed runs it again.

## Uses

| Field | Notes |
| --- | --- |
| `asset_id`, `project` | |
| `cut` | The project's cut that used it (`v3`, `final-1.15x`). Stored in the existing `version` column; the name in commands is `--cut`, and `--version` stays as an alias. |
| `artifact_version` | The asset version the cut used. Required for new rows: a media file's hash, or the bundle version that was copied into the project. Empty only on legacy rows, meaning unknown. Never filled in with "latest". |
| `modified` | True when the project changed a bundle's files after copying it; `artifact_version` is then the version it started from. Empty on legacy rows. |
| `role` | `visual`, `music`, `sfx`, `voice`, `character`, `code`, `model`. Older free-text roles stay as written and are reported, not rewritten. |
| `cue`, `output_time`, `used_at` | The word or event, seconds in the cut's output (finite, 0 or more), when recorded. |

`used` rejects an unknown ID, an unknown or ambiguous version, a `--file` that is not the
library's copy (naming the asset it does match, if any), a role outside the vocabulary, a
negative or non-finite `output_time`, and a missing version. Recording an identical use again changes nothing.

## Cut declaration

The producing skill knows which library entries a cut selected; the library cannot infer it from
a project folder. So the producer writes that list from its own record (video-edit's visual
manifest and cue sheet, animated-video's cue sheet and the bundles it copied) into one small file
per cut, and hands it to the library:

```json
{
  "project": "PROJECT",
  "cut": "v3",
  "selected": [
    {"id": "sfx-07", "role": "sfx", "file": "audio/sfx-07.flac", "cue": "keyboard", "output_time": 12.4},
    {"id": "street-kit", "role": "model", "artifact_version": "3f9a1c0b7d22"},
    {"id": "walk-rig", "role": "character", "artifact_version": "9c01d5e3aa40", "modified": true}
  ]
}
```

- `selected` lists only what the delivered cut shows or plays. Candidates the editor rejected,
  and assets merely mentioned in notes or source, stay out.
- Each entry gives `artifact_version`, or `file` for media (relative to the declaration's
  folder), which the library hashes and must match that asset. A mismatch is an error: the file
  in the edit is not the library's copy, so ingest it (as a variant if it was cropped or
  re-encoded).
- An empty `selected` list is a valid declaration: this cut used nothing from the library.
- The file lives with the project (for example `library-v3.json`); the producing skill names
  the path.

`used --from FILE` records every entry in one transaction, or none when any entry is invalid.
`deliver --declared FILE` stores the resolved list on the delivery row so later checks don't need
the file.

## Notes and deliveries

- `notes(asset_id, artifact_version?, kind, text, source, created_at)`; `kind` is `opinion`,
  `test`, `rights` or `caveat`. Opinions are the user's words, quoted, and need a `--source`.
  These four stay separate: passing a test is not liking, and `verified` rights are not an
  opinion. Availability (file present, not archived) is computed by `check`, not stored.
- `deliveries(project, cut, delivered_at, declared, registered, declined_reason)`: one row per
  delivered cut. `declared` is the cut declaration's list. `registered` lists the versions
  registered from this project (`register --project`) since its previous delivery, whenever
  they were registered; a version that failed validation can't be listed and doesn't need to be.
  `declined_reason` says why there were none. The row records one decision for the cut; it is
  not a log of every candidate the project considered.

## Commands

| Command | What it does |
| --- | --- |
| `init ROOT` | Create an empty library at ROOT, or open and migrate an existing one. |
| `search QUERY --kind --tag --max-duration --min-duration --rights --unused-in P --archived --limit --text` | Full-text search (titles, tags, notes, creator, cue) plus filters. Hides archived assets and exact duplicates unless `--archived`. |
| `show ID` | One asset with provenance, versions (full and short digest, validation status), notes and uses. |
| `ingest FILE --kind … [--title --id --tags --source-url --creator --license --rights-status --work-id --variant-role …]` | Add a media file: hash, probe, preview, copy into the root. Never overwrites a file: another file with the same name gets a `-<8-hex digest>` suffix. Returns the existing ID for an exact duplicate (`duplicate_of`), and puts its file back if the library's copy went missing (`restored`). `--source-out` must be after `--source-in`. |
| `register --kind character\|code\|model --id … --entry --files … [--source --title --example --preview --planned-use --project --dependency --dimensions --validate-command --validate-setup --validate-cwd --validate-env --validate-timeout \| --no-validate REASON]` | Stage, verify, publish and record a bundle version; then validate it. Exits 1 when validation fails. |
| `used ID --project P --cut C --role R (--artifact-version V \| --file F) [--modified --cue --output-time]` | Record one use. |
| `used --from FILE` | Record every entry of a cut declaration, all or nothing. |
| `note ID --kind K --text T [--source S] [--artifact-version V]` | Append a dated note. |
| `archive ID` | Hide from search; keep the row and its uses. |
| `deliver --project P --cut C --declared FILE (--registered ID@VERSION … \| --none REASON) [--project-dir D]` | Run the project check; if it passes, record the delivery decision. |
| `check [--project P --cut C [--declared FILE] [--project-dir D]]` | Library: files exist, uses point at known assets and versions, bundle folders match their manifests; warns about orphaned or staged folders and media files whose size differs from their record. Project: see below. |
| `import CATALOG.json [--update ID …]` | Add records from a catalog file. |
| `stats` | Counts by kind, uses, reuse (assets used in two or more projects), versions, notes, deliveries. |
| `export` | Write `exports/library.json` and `exports/index.html`. |

## Project check

`check --project P --cut C` reads the declaration from `--declared FILE`, or from the delivery
row when the cut has been delivered. It fails when:

1. there is no declaration for cut C (neither a file nor a delivery row), or the file names
   another project or cut;
2. a declared entry has no use row for P **and** C; a use in another cut does not count;
3. a declared entry's version differs from its use row's `artifact_version` (a legacy use with
   no version never matches);
4. a use row for P and C points at a missing asset, version, file or version folder;
5. the newest version of a bundle registered from P lacks a required content field or
   `planned_use`, its files differ from its manifest, or its validation failed.

`deliver` runs the same check, reading the declaration once and storing exactly the list it
checked, and also fails when a version registered from P since P's last
delivery (and not failed) is missing from `--registered`. It refuses to write the delivery row
while anything fails, so a delivery row means the cut's catalog was complete when it was
written. The video itself can ship without one; the producer then reports the catalog as
incomplete.

It lists, without failing:

- **unrecorded references**: library assets not in the declaration whose ID appears in a text
  file under the declaration's folder (or `--project-dir`), or whose bytes match a file there
  (same size, then same hash). The scan skips hidden folders, `node_modules` and the library
  itself, and stops after 20,000 files. Some are selections missing from the declaration; most
  are rejected candidates or leftovers. The agent decides which; fix the declaration, not the
  warning.
- uses in the cut that the declaration leaves out, uses with legacy roles, legacy uses with
  unknown versions, and bundles from P that were never validated.

It cannot judge whether something should have been registered or whether an asset was a good
choice. Those are the agent's and the user's calls, recorded in the delivery row and in notes.
