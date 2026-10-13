---
name: asset-library
description: >-
  Keep a persistent local library of reusable video-production assets across projects: footage,
  images, music, sound effects, characters, animation code and 3D sets. Use when searching for an
  existing asset before sourcing or building one, registering something reusable as soon as it
  works, recording which assets a cut used, or checking a project's catalog at delivery.
---

# Asset library

One SQLite database plus the files it points at, under one library root. The database is the
record of every asset, every version of it and every cut it appeared in. The files stay on disk
where agents and editors can open them. Agents query it with a JSON command-line tool; there is
no server and no background process.

Five words carry the workflow:

- **Original**: one source work. A crop, a re-encode or a ducked mix is a variant of the same
  original, so reuse limits count originals, not filenames.
- **Version**: one immutable state of an asset. A media file's version is its content hash. A
  character, code kit or 3D set is a **bundle** (every file it needs, its dependencies, an
  example, a preview and how to validate it), and each registration snapshots a new version.
- **Use**: one row saying this project's cut used this version of this asset, at this cue, in
  this role.
- **Declaration**: the producing skill's list of the library entries one cut selected.
- **Delivery**: the close of a project cut, when every declared entry has its use and the
  project's registrations are accounted for.

The fields, kinds, bundle layout, declaration format and checks are in
[records](references/records.md). Read it before registering a bundle or changing the schema.

## Set up

`SKILL_DIR` is this skill's folder; `LIB` below means `python3 SKILL_DIR/scripts/library.py`
(Python 3.9+; FFmpeg for probing media and making previews).

1. Read `~/.asset-library/profile.md` if it exists. It names the library root, any local adapter
   to call instead of `LIB`, and the user's standing rules (when characters are reused, how
   opinions are recorded).
2. Run `LIB check`. It reports the root, schema version, missing files and stray bundle folders.
   The root comes from `--root`, else `ASSET_LIBRARY_ROOT`, else a ``Root: `PATH` `` line in the
   profile; with none, `check` says so.
3. With no library yet, ask once where it should live (recommend a folder beside the user's
   video projects) and run `LIB init ROOT` only after they agree. Offer to write
   ``Root: `ROOT` `` into the profile.

Every command prints JSON on stdout and exits 1 on failure with an `error` and a `hint`;
`search --text` prints rows for a human. `LIB COMMAND --help` shows each command's flags and an
example. Paths in records are relative to the root, so the root can move or sync as one folder.

## 1. Search before sourcing or building

Before downloading, recording, synthesising or modelling anything a project needs, search for
it by what the viewer sees or hears, not by the project's topic:

```sh
LIB search "keyboard typing" --kind sfx --max-duration 0.5 --unused-in PROJECT
LIB search "street at dusk" --kind model
LIB show ID
```

Read `show` before reusing: its uses (where it already appeared), its notes (the user's opinion
in their words, test results, caveats), rights, and versions. Then choose one:

- **Reuse** a specific version as is, when it fits the brief and the profile allows it. Copy
  that version's snapshot (`bundles/ID/VERSION/files/`) into the project and keep its version
  for the declaration.
- **Restyle** a bundle for this film's look. The use names the version you started from, marked
  modified; if the restyle is reusable, register it (step 3).
- **Build new**, when nothing fits. Reading an old bundle for its mechanics is always fine.

Provenance is not publication clearance. An asset with unknown rights stays a candidate until
the user decides.

Done when: every recurring asset and sourced media item in the plan was searched for, and each
pick names its ID and version, or "new".

## 2. Bring in new media as it arrives

Ingest each sourced or recorded media file when it becomes a candidate, so its provenance is
captured while it is known:

```sh
LIB ingest FILE --kind image|video|sfx|music --title "…" --source-url URL --creator "…" \
  --rights-status unknown --tags "a,b"
```

Ingest hashes the file, refuses an exact duplicate (it returns the existing ID as
`duplicate_of`), copies files from outside the root into `media/KIND/`, probes size, duration,
sample rate and peak level, and makes a preview for images and video. Keep rejected candidates
out of the library or `archive` them; never delete an asset that a past cut used.

## 3. Register reusable things as soon as they work

Don't wait for delivery: projects stall, and an unregistered rig dies with its folder. Register
a version when something the project built becomes reusable and has passed its own check (the
rig holds its model sheet, the kit renders its example, the sound was approved in the mix). Ask:
would another project plausibly want it? A character the user wants again, a rig, a kit that
models a real object, a set, a material, a synthesised sound, a helper script. One-off shots and
project glue do not qualify. This is judgment; no check can make it for you.

From the project folder (paths are relative to `--source`, default the current folder):

```sh
LIB register --kind code|character|model --id ID --title "…" --project PROJECT \
  --entry src/kit/street.tsx \
  --files src/index.ts src/Root.tsx 'src/kit/street*' public/street/ package.json package-lock.json \
  --example src/kit/street-demo.tsx --preview out/street.jpg \
  --validate-setup "npm ci" \
  --validate-command "npx remotion still src/index.ts StreetDemo out/check.jpg" \
  --planned-use "what it draws or does, and its parameters"
```

Register snapshots the files into the library, publishes them only after their hashes verify,
then runs the validation in a fresh temporary copy of the snapshot, not your project folder, with
only `PATH`, `HOME`, `LANG`, `TMPDIR` and the names you pass with `--validate-env`. A bundle that
needs the project to run isn't complete yet: when validation fails, the version is recorded as
failed and the command exits 1; add the missing files to `--files` and register again. Code and
characters need an example and a validation command (or `--no-validate REASON`, recorded as a
caveat); models need a preview, and validation is optional. Declare tools and packages with
`--dependency` (`npm:three@0.170.0`, `tool:blender@5`) and add `--dimensions` for anything whose
scale must match other objects. Registering the same content again returns the same version;
any changed file or setting adds a version, and old versions stay because past cuts point at
them.

## 4. Declare the cut and record its uses

When a cut is decided, write its declaration from your own manifest or cue sheet: every library
entry the cut shows or plays, with the version or file actually placed, and nothing it rejected
([format](references/records.md#cut-declaration)). Then record it:

```sh
LIB used --from library-v3.json
```

- The cut is the project's cut (`v3`, `final`), not the asset's version.
- A use pins the version that was placed. Never record "latest"; if you don't know which version
  is in the edit, find out from the file or the copied snapshot's `bundle.json`.
- Roles come from the fixed vocabulary in [records](references/records.md#uses); put detail
  such as "whoosh" in the cue.
- `used --from` records every entry or none: one bad entry is reported and nothing is written.

## 5. Deliver and check

```sh
LIB deliver --project PROJECT --cut CUT --declared library-v3.json \
  --registered ID@VERSION …    # or: --none "why nothing from this project is reusable"
```

`deliver` runs the project check first and records nothing while it fails. It fails when a
declared entry has no use for this project and this cut, a use names the wrong or no version, a
use points at something missing, the newest bundle version registered from this project is
incomplete or failed its validation, or a version registered from this project since its last
delivery is missing from `--registered`. Run the same check without recording anything with
`LIB check --project PROJECT --cut CUT --declared library-v3.json`. It also lists unrecorded
references: library assets that files in the declaration's folder name or contain but the
declaration leaves out. Most are rejected candidates; a real selection missing from the
declaration gets added there and recorded.

Report two things separately: the delivered video, and catalog status (delivered, or what is
still missing and why). A blocked catalog step does not block delivering the video; list the
missing records in the project notes so they can be added later.

## Notes, opinions and tests

`LIB note ID --kind opinion|test|rights|caveat --text "…" --source "where it was said"` appends a
dated note, tied to a version when you pass `--artifact-version`. Record the user's opinion in
their own words with its date and source; never infer that the user liked something. A passing
validation is a test result, not an opinion.

## Without the library

If this skill is installed but has no library and the user declines one, or the tool fails,
keep the project manifest that the producing skill describes and say the catalog was not
updated. Never edit the database by hand; use the commands, or `LIB export` for a full JSON copy.
