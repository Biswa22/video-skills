# Realistic 3D

How to build a photoreal or physically detailed world (a street, a field, a house, an engine
room) and move through it believably. A realistic film reads as real when its scale, materials,
light, air and motion obey physics; adding adjectives to a prompt or more objects to a frame does
not get there. This file is a workflow plus a tested starting kit for the three.js route
(`templates/parts/src/kit/realism/`, with a runnable example shot in `examples/realistic-3d/`).
The kit gives a detailed procedural 3D starting point, not photographic quality: its example
still reads as CGI (see "What the kit does not do"). Measure every setting on the shot you are
building; the kit's numbers are from one outdoor shot.

## 1. Read the references as physics

Collect three to six real photos or clips of the place or thing, at the distances the film
needs (wide, mid, close). Use the user's references first. Then write `LOOK.md`, one short
section each:

- **Scale.** Real dimensions in metres: door height, kerb, leaf size, vehicle length. Pick one
  scene unit (1 = 1 m) before modelling.
- **Materials.** Each surface: base colour, how rough it is, where it is worn, dirty, wet or
  weathered, and why (rain runs down, hands touch handles, sun bleaches the top).
- **Light.** Time of day, sun direction and hardness, sky colour, the colour of light bounced
  off the ground, which surfaces are in shadow.
- **Air.** How much haze at what distance, and its colour.
- **Density.** How much detail sits in one square metre at the hero distance: blades, pebbles,
  cracks, leaves.
- **Motion.** How the things in it move: grass and branches in wind, a car pitching as it brakes,
  water, people's weight shifts.

Done when: every hero surface and every moving thing in the beat sheet has a line in `LOOK.md`
that names a measurable property, not a mood.

## 2. Choose the route

Choose from the shot list, the look and the render budget, not by habit.

| Route | Choose it when | Costs |
| --- | --- | --- |
| three.js in Remotion (the template's `three-canvas.tsx` plus the realism kit) | Stylised to detailed 3D; many shots; tight sync to VO and captions; outdoor light from sun and sky; instanced vegetation and props | The raster setup has no global illumination, ambient occlusion pass or ray-traced reflections: faces turned away from the sun go very dark, contact shadows come only from the shadow map, and there is no depth of field or motion blur. Screen-space effects or a path-tracing add-on may close part of the gap; none is in the kit or tested here. Fast: the example shot renders at 0.3-0.4 s per 1280x720 frame |
| Blender (Cycles, or EEVEE for speed), rendered to an image sequence that Remotion composites | Close-ups that must pass as photographs; interiors lit by bounce; glass, liquids, caustics; cloth, fluid or rigid-body simulation; very dense scattered detail | Minutes per frame are common; a separate scene file and script to keep in sync with the cue frames |

Estimate the budget before choosing: seconds per frame on the test shot (step 4) times the
film's frame count, at the machine's real speed. Ask the user before a route whose estimate
runs past their deadline. Test the route you chose. Compare the other route only to settle a
real question (for example, the three.js test fails the reference on interior bounce light).

Blender is optional. Check for it in preflight; never assume it is installed. A Blender route
runs headless: `blender -b scene.blend -P build.py -- ARGS` to build or update the scene from a
script, then `blender -b scene.blend -o //frames/#### -F PNG -s START -e END -a` to render.

## The realism kit (three.js route)

Copy `templates/parts/src/kit/realism/` into the film's `src/kit/realism/` (it imports `three`
and its standard add-ons only), then build the set from it. Read `examples/realistic-3d/` first:
`src/set.ts` composes a whole outdoor set from the kit and `src/Shot.tsx` shows the per-frame
wiring. Start there and change the set, rather than writing these pieces again.

| File | Use it for |
| --- | --- |
| `sky.ts` | `skyLight(gl, {elevation, azimuth, turbidity, clouds, ground, visibility})` once: three's Preetham `Sky` for the background, a PMREM environment of that sky over a ground disc lit by it (bounce light), the sun's colour and intensity through the same atmosphere, and the haze colours read back from the sky |
| `sun.ts` | `makeSun({...sky, center, radius})`: a shadowing sun whose shadow box is fixed over the set; `followSun()` moves it only in whole shadow texels when the camera travels further |
| `shade.ts` | Patches for three's standard materials, composed with `patch(material, ...)`: `wind()` (frame-driven, in world space, also put into `depthFor()` so shadows sway with the plants), `weather()` (noise colour, roughness and relief, plus chips on edges, dust and moss on top faces, grime from the ground, streaks below sources, wetness, and per-vertex wear masks), `air()` (height haze lit by the sky, applied before tone mapping), `translucent()` (sun through blades and leaves), `leaf()` (a textureless leaf cut-out). Set `time.value = frame / fps` each frame |
| `plants.ts` | `scatter()` seeded placement with a density function (use it for both where things grow and level of detail); `instances()`; `tuft()`, `flower()`, `tree()`, `leafCard()` constructors |
| `shapes.ts` | `edges()` convexity attribute for edge wear; `paint()` per-vertex wear masks; seeded `rock()` and `slab()` |
| `camera.ts` | `track()` along a path at a focal length on a 36 mm sensor; `move()` eased progress |
| `noise.ts` | Seeded `rng`, CPU noise, and GPU noise with octaves faded below two pixels so detail doesn't crawl |

Wiring in Remotion: render with the template's `ThreeCanvas` at `dpr={2}` (2x supersampling;
thin grass shimmers without it), `shadows="percentage"`, and set `gl.toneMapping` and
`toneMappingExposure` in `onCreated`. Build the set once in `useMemo`; per frame set only the time
uniform, animated transforms and the camera, all from the frame number. Keep `Finish` at
`bloom={0}` (tone mapping already happened in three) for its vignette and grain.

Settings that the example shot settled, with the reason:

- **Sun from the sky's own disc.** The sky shader's units are its own; a sun derived from its
  disc radiance times the disc's solid angle (what `sunColor()` does) gives a direct-to-sky
  ratio near clear-sky measurements. At a 13 degree sun that is an intensity of about 25 with
  ACES exposure about 0.24. A sun five times weaker made the sky outshine the set.
- **Haze is strong for its number.** The horizon sky is several times brighter than sunlit grass,
  so even a few percent of in-scattered light lifts distant ground a lot. A visibility of 1.4 km
  washed the meadow into a beige band; 4 km read as late-afternoon air.
- **Rough ground still mirrors the horizon at grazing angles** under three's Fresnel, which shows
  as a bright band toward the horizon. Use `MeshPhysicalMaterial({specularIntensity: 0.25})` for
  soil and litter (micro-shadowing cuts their grazing reflectance).
- **Rocks need creased normals** (`toCreasedNormals`, done in `rock()`); smooth normals across
  fracture planes read as pillows or sandbags.
- **Weathering has to be bigger than feels right** at the distance it is seen from: chips, rust
  runs and moss sized for a close-up vanish at 4 m. Check a 1:1 crop of the hero still.
- **Light the side you show.** A wall whose camera-facing side was away from the sun read as a
  dark heap; the same wall on the other side of the path, facing the sun, read as stone.
- **Debug values in frame.** Browser console output did not reach the CLI log in these renders;
  the example's `debug` prop prints the sky and sun numbers into the frame instead.

Measured on the example (1280x720, 24 fps, 2x supersampled, about 60k near grass tufts of seven
blades, 150k far tufts, 150k leaf cards, one 4096 shadow map, on an Apple-silicon laptop shared
with other renders): a 60-frame sequence in 17-24 s at concurrency 1 including browser start
and scene build, so at most 0.3-0.4 s per frame; re-rendered frames were bit-identical, also
between two separate installs. `examples/realistic-3d/check.sh`
reproduces these numbers and fails if a re-rendered frame differs.

### What the kit does not do

Built only when a shot needs it, then validated on that shot: sub-frame motion blur, depth of
field, ambient occlusion or bounce beyond the environment map, cascaded shadows (one shadow box:
far trees cast no shadow on the meadow), volumetric light shafts, bloom in linear light,
per-frame level of detail (it has two density tiers by distance), the Blender bridge, and an
automatic contact-slip check. Its example still reads as CGI: tree crowns repeat one
constructor's shape on regular spacing, faces turned from the sun go nearly black, grass has no
seed heads or dead blades, and `Finish`'s grain is heavy for a realistic film. Its techniques
are general real-time ones (procedural geometry, instancing, PBR with a sky environment, haze,
frame-driven secondary motion); it is not a recreation of any particular creator's scene or code.

## 3. Build physical detail

Search the asset library first when it is installed: sets, constructors, materials and
characters from earlier films carry their scale and their tested settings. Sourced sky maps,
models and scanned materials are sourced assets: use them only where the brief allows sourced
material, check their licence, and record where each came from.

- **Model in real units** with real proportions from `LOOK.md`. Bevel edges; nothing real has a
  perfectly sharp edge, and bevels catch the light.
- **Write constructors, not one-off meshes.** A function that builds a fence, a tree or a
  building from parameters and a seed makes a hundred varied instances and can be registered
  for the next film. The example's `pump.ts` is one: lathe profiles and tubes in real units,
  weathered from where water runs and hands touch.
- **Most realism lives in roughness.** Vary roughness and colour across every surface with
  noise; add normal detail at the hero distance; drive wear, dirt and wetness from masks that
  follow the cause (height for grime, upward faces for dust, edges for chipping). Break up
  visible tiling.
- **Scatter by instancing** (`InstancedMesh` in three.js; distribute-and-instance nodes in
  Blender) with per-instance scale, rotation and colour variation, denser where the camera
  looks and coarser far away.
- **Light from the sky.** A sun plus an environment from a sky model or an HDR image, so every
  surface sees the sky's colour; in three.js, build the environment map with `PMREMGenerator`.
  Shadows on everything that touches the ground; darken contacts and creases with ambient
  occlusion (the three.js kit has no AO pass; see above).
- **Air.** Distance fog tinted toward the sky colour, stronger with distance and lower to the
  ground in the morning.
- **Exposure and tone mapping.** Work in linear light, set exposure like a camera, and tone map
  with a filmic curve (ACES or AgX) exactly once: in the renderer (three.js `toneMapping`,
  Blender's view transform) or in one later pass, never both. Bloom only real light sources.
  The template's `Finish` adds no tone curve; its bloom is an sRGB filter on the finished
  picture, plus vignette and grain. For a realistic shot, either bloom in linear light before
  the tone map (in the 3D pass) and set `Finish` `bloom={0}`, or keep `Finish` bloom and add
  none upstream; keep its grain either way.

Done when: a still of the hero framing sits beside the matching reference at the same size and
the remaining differences are listed in `LOOK.md`.

## 4. Animate with weight, then test one moving shot

- **Mass and inertia.** Heavy things accelerate and stop slowly; light things react first and
  settle with small overshoot. Derive ease durations from the mass you are showing.
- **Contact.** A planted foot, hoof or wheel does not slide: derive a wheel's rotation from the
  distance travelled (angle = distance ÷ radius) and lock feet to the ground for their contact
  frames.
- **Secondary motion** lags the cause: branches after the trunk, hair and cloth after the head,
  a car's body after its wheels.
- **Wind and ambient life** come from noise driven by the frame number, so every render matches.
- **Simulate offline, play by frame.** Run physics or cloth once, bake it to keyframes or a
  per-frame array, and look the frame up. Nothing reads a clock.
- **A real camera.** Set the lens by focal length (`PerspectiveCamera.setFocalLength(mm)` in
  three.js), move it like a dolly, crane or drone with limited acceleration, and add handheld
  shake only when the shot calls for a person holding it. Motion blur matches a 180° shutter;
  three.js needs sub-frame accumulation for it, Cycles has it built in.
- **Determinism.** Every random value is seeded. In Blender, fix the seed and sample count,
  bake simulations, and render with the same settings each time.

Before building the rest of the film, render the hardest two to three seconds at full size: the
fastest camera move through the densest detail. Run the temporal review below on it, show it to
the user beside the reference, and wait for their verdict. It replaces the style frame for a
realistic look, because a still cannot show whether the motion is believable.

## Temporal review

Stills cannot show what happens between frames. On the test shot, and later on every 3D shot:

When a tool can play the shot, watch it at full speed first; motion problems are easiest to see
moving. Then, or when nothing can play it:

1. **Consecutive frames.** Tile one second around the fastest motion and read it. One second is
   `fps` frames starting at frame `start_s × fps`; this example is 24 fps, seconds 2–3:
   `ffmpeg -i shot.mp4 -vf "select='between(n\,48\,71)',scale=480:-1,tile=6x4" -frames:v 1 -fps_mode vfr sheet.png`.
   At 30 fps use `between(n\,60\,89)` and `tile=6x5`. Look for popping detail, sliding
   contacts, shadow edges crawling, and textures swimming across surfaces.
2. **Flicker.** Measure mean brightness per frame:
   `ffprobe -v error -f lavfi -i "movie=shot.mp4,signalstats" -show_entries frame_tags=lavfi.signalstats.YAVG -of csv=p=0`.
   This is screening, not a pass mark. A pan toward the sun or an object crossing frame
   legitimately changes brightness; a one- or two-frame jump that the camera, the objects and
   the light don't explain is worth finding in the frames. Common causes: shadow maps whose
   camera moves with the view, noise that changes every frame, per-frame denoising.
3. **Determinism.** Render a few frames twice with the same settings and compare
   `ffmpeg -i a/%04d.png -f framemd5 -` with the same for `b/`. Also screening: identical hashes
   show the frames are reproducible on this machine and renderer; a difference points at an
   unseeded random value, a clock or a texture that loads late, but GPU path tracing and
   denoisers can also differ slightly between runs. Look at the differing frames before calling
   it a bug.
4. **Speed.** Record seconds per frame; it sets the budget for the rest of the film.

No number here passes a shot. Done when: the frames and measurements show no unexplained
popping, sliding, crawling, swimming or flicker, the frames hold up beside the reference, the
user has accepted the motion, and any criterion in `LOOK.md` still unmet is listed. Then
continue with the board and the production in SKILL.md.

## Handing Blender frames to Remotion

Render a numbered sequence at the film's fps and size, timed from the same cue frames as
everything else: export the cues to JSON and have the Blender script read them. Remotion
composites the sequence under captions and overlays and mixes the sound. Export the shot's
sound events from the same cue file.

Colour has to be transformed once on the way. Remotion composites display-ready sRGB images.

- **PNG** (8- or 16-bit) is written with the scene's view transform (AgX or Filmic) applied, so
  it arrives tone-mapped: composite it as is, with no second curve in Remotion.
- **EXR** stores scene-linear light with no view transform. Convert it to display sRGB in one
  step before Remotion, with the same view transform the look was approved with.

When Blender frames and three.js layers share a shot, give both the same transform and exposure,
or render the overlay from Blender too; mismatched curves show at the seam.
