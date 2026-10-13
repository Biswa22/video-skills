# Choreography: design the motion, check it, build it to spec, measure it

Rules like "something should change every couple of seconds" don't hold on their own. Reviewers
that see stills can't tell a second where one thing drifts from a second where twenty things
transform, a shot brief with one event per line gets built as one event per line, and dense motion
written from scratch under time pressure gets cut down. So the motion is designed in writing,
attacked by a critic, built to that design, and measured on the render.

## The motion script
`MOTION.json`, in output frames of the delivered film, written after the beat sheet and before the
animatic. Format and checks: `templates/remotion-film/motion_check.py`.

```json
{"fps": 30, "shots": [{"id": "S07", "from": 530, "to": 670, "beats": [
  {"at": 536, "line": "press play",
   "learn": "pressing play turns the song into a signal that leaves the phone",
   "hero": {"id": "play-flip", "does": "the play glyph flips to pause; the screen ripples outward"},
   "layers": ["the waveform peels off the glass in strips", "the strips' light rakes across the thumb"],
   "camera": "pushes in on the press, whips up as the waveform leaves"}]}]}
```

- **A beat every ~0.75 s** at delivery speed, every shot, start to end. Gaps are where a film goes
  stale.
- **Several things at once.** Each beat has the hero action plus at least two other moving things:
  secondary action the hero causes (debris, recoil, light it throws), ambient life of the place,
  and a camera that answers the event. A slow push over a still set is not a layer.
- **`learn` is what a viewer with the sound off learns right then.** If you can't write it, the
  beat is decoration; if it only restates the narration, show the mechanism doing the work
  instead (the parts moving, the thing being cut, sent, hit, copied).
- **Energy.** Anticipation before every move, speed ramps instead of constant speed, overshoot and
  settle, staggered multi-part motion (a thing assembles, splits or transforms from many parts,
  each offset in time), collisions with consequences, and a camera that moves through and around
  the action (whip, orbit, push-through, crash zoom). Avoid one object drifting, a glow pulsing, a
  looped ambient motion under narration, and holds while the voice explains.
- **Every sentence is carried by at least one beat** inside its span, so no line is told by the
  voice alone.

Density targets come from the bar film (step 7 of SKILL.md), measured the same way, not from these
defaults. One example: an accepted 2:28 explainer had a median of 20 separately moving things per
frame and only 3% of seconds with two or fewer; a cut its maker found "constant, playing in the
background" had 12 and 11%. Measure your own bar film.

## Who writes it
- A **choreographer** (one agent, no build duties) writes the motion script from the approved beat
  sheet, the world and the bar film's frames.
- A **critic** (a fresh agent with the script, the beat sheet and the bar film, not the
  choreographer's reasoning) attacks it: beats a newcomer couldn't read, moments where one thing
  moves, lines carried only by the voice, energy below the bar film's. Revise until the critic and
  `motion_check.py script` both pass.
- The **animatic** is built from the motion script (blocked shapes are enough, every beat in
  place), and the user approves it moving.

## The gates
1. `motion_check.py script MOTION.json --words words.json` before any build.
2. Builders implement the script. Each hero id is exported in the scene's events file (the same
   `EVENTS` the sound uses, [sound events](remotion-pipeline.md#sound-events)) on its frame:
   `motion_check.py events MOTION.json out/events.json`.
3. Every act preview and the full cut: `motion_check.py film cut.mp4 --bar BAR.mp4 --shots
   shots.json --strips out/still-strips`. Read every strip it writes; a shot below the bar goes
   back to its animator with its strips. This measures how many separate things move, not what
   they mean, so it pairs with the next gate.
4. The **mute test** at the animatic and at the final cut ([review loop](review-loop.md#mute-test)).

A gate the user waives is named in the delivery report.

## Making dense motion affordable
Density gets cut when each animator hand-writes it. Before the acts start, put the film's shared
motion into the kit: parametric staggers for multi-part motion, particle and debris systems,
trails and motion blur, impact flashes that light their surroundings, and camera moves with speed
ramps. Shots then call primitives instead of re-deriving them.
