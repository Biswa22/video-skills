# Review loop: judge panel, routing, stop rule

## Panel
Three independent judges per render, each with a lens and a structured critique: `{score 1–10,
verdict, issues[{start_sec, end_sec, severity, problem, fix}], keep[]}`. Tell each one to
extract frames itself, relate them to `words.json`, read the source for precise fixes, and
write only under `out/judge/`. Judge against the current brief and platform. Past films aren't the benchmark.
- **Animation or motion director:** on-model consistency against the reference, acting,
  anticipation and overshoot, continuity across cuts, and broken frames (missing limbs, z-order,
  pops, ghosting, empty frames).
- **Growth and story:** does frame 0 stop the scroll in 1.5s; is each line shown with the sound
  off; the emotional arc; dead stretches over 3s; comment or share moments; an ending that loops.
- **Design and sound:** the finish bar (full frame, depth, light, real objects, life,
  transitions) against each shot's anchor frame, composition, colour script, accent discipline,
  safe zones, caption legibility, and the audio measured with ffmpeg (VO-to-bed ratio, masking,
  loudness, true peak, effects landing on their events).

## Routing fixes
- Route each issue to the owner of its time range (the act files). Issues spanning 20s or more
  go to a global owner (`Film.tsx`: captions, mix, transitions). Run fixers in parallel on
  disjoint files. Pass the judges' `keep` lists so fixes don't break what works.
- The workflow shape used: kit (1 agent), then acts (8 in parallel), then render, then judges
  (3), then routed rework (up to 8), then render, and repeat for at most 2 rework rounds.

## One project's numbers (a 74s vertical short): evidence, not targets
| Track | Scores by round | Wall time | Agents / tokens |
|---|---|---|---|
| Motion graphics v1→v3 | 5/5/5 → 6/6/6.5 → 6/7/6.5 | about 45 min | 11 / 1.55M |
| v4 rework (resumed) | 6/6/6 | about 18 min | 4 live / 0.6M |
| v5 polish (single agent) | not judged | about 19 min | 1 / 0.23M |
| Cartoon kit+acts+2 reworks | 6/6/6.1 → 6.5/7/6.5 → 7/7/6.4 | about 2.5 h | 36 / 6.1M |

## Lessons
- Scores plateau fast. After round 2, the top issue in both tracks was something only the user
  could supply or decide (their face, the format). Stop and ask instead of adding rounds.
- Scores aren't comparable across rounds, because judges recalibrate (v3→v4 design went from 7
  to 6 while the film improved). Track the open issues, not the number.
- Your own spot-check after each render still catches things: a per-word duck that pumps, a
  see-through character, floating legs, a blurred last frame. Pull frames at every flagged
  time before reporting "done".
- Judges and stills can pass a film that fails as a whole. Ask the story judge, line by line, what
  physically happens on screen and whether a newcomer could retell it; a mechanism shown only as a
  label or a colour change fails that check even when every frame is pretty.

## Measures that separate a full film from an empty one
Cut count rarely explains a "flat" verdict; content does. Measure the film and its reference the
same way, from a frame every second or so:
- **Empty area:** the share of each frame that is near-flat (low local variance), and the share
  that is near-black.
- **Detail:** mean edge density or high-frequency energy per frame.
- **Colourfulness:** mean chroma.
- **Repetition:** the share of seconds whose frame looks like an earlier one (a perceptual hash
  distance under a threshold).
- **Motion:** frame-difference energy over time. Separate camera movement from objects moving,
  because a panning camera over a still subject reads as busy in the numbers and dead on screen.
- **Holds:** the share of time a frame matches the frame 4 s earlier (normalised correlation of
  small, blurred grey frames above about 0.75). Ambient motion over an unchanged composition
  counts as a hold. One example: a cut the user found "constant, playing in the background" held
  12% of its runtime; the accepted film it was judged against held 3–4%. It measures composition,
  not information, so pair it with the sound-off retell.
Put matched beats of the film and the reference side by side at the same size.

## Restart after a rejected cut
When the user rejects a whole cut ("low quality", "not immersive", "start over"), don't route
fixes; the problem is the concept, not the shots.
1. Stop all builds and renders.
2. Run an independent evaluator: a fresh agent that judges from the finished film and the
   reference first, then reads the plans only to diagnose process causes. Give it the films and
   the script, not your own diagnosis. It writes a verdict, ranked problems with timestamps and
   side-by-side frames, a line-by-line table, what to keep, and two or three different
   directions.
3. Take the user's notes on it, write the lessons into the project, and record what the user
   locks (often the script, the voice and any camera footage).
4. Restart at step 1 of the skill with a fresh concept. A new agent with the lessons file
   avoids inheriting the old plan's assumptions.
