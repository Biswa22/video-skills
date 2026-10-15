# Review: motion, judges, mute test, restart

## Motion at the animatic
Stills can't show the difference between a second where one thing drifts and a second where many
things transform, so motion is checked moving, at the animatic and again on each act.
- **Something changes about every second** at delivery speed, in every shot, start to end.
- **Several things at once.** Each beat has the hero action plus secondary action it causes
  (debris, recoil, the light it throws), ambient life of the place, and a camera that answers the
  event.
- **Energy.** Anticipation before moves, speed ramps, overshoot and settle, staggered multi-part
  motion, collisions with consequences, a camera that moves through the action (whip, orbit,
  push-through).
- **Effects are punctuation.** Sparks, flashes and rings are tied to an event, brief, and keep the
  hero in view.
- **Every sentence is carried by a beat** inside its span, so no line is told by the voice alone.

To measure a cut that feels static, `templates/remotion-film/motion_check.py film CUT.mp4 --bar
BAR.mp4` counts separately moving things second by second against a film the user accepted and
writes frame strips of the stillest seconds. Read it as a diagnosis, then fix with better pictures.

## Panel
Three independent judges per render, each with a lens and a structured critique: `{score 1–10,
verdict, issues[{start_sec, end_sec, severity, problem, fix}], keep[]}`. Tell each one to extract
frames itself, relate them to `words.json`, read the source for precise fixes, and write only
under `out/judge/`. Judge against the current brief and platform.
- **Animation or motion director:** on-model consistency, acting, anticipation and overshoot,
  continuity across cuts, and broken frames (missing limbs, z-order, pops, ghosting, empty frames).
- **Story and ideas:** does frame 0 stop the scroll in 1.5s; can a newcomer retell what physically
  happens in each line with the sound off; which pictures would a viewer screenshot or share, and
  which are the literal default that a better idea would beat; dead stretches over 3s; an ending
  that loops.
- **Design and sound:** the finish bar against each shot's anchor frame, composition, the colour
  key (is the hero accent always where the eye should go?), safe zones, caption legibility, and the
  audio measured with ffmpeg (VO-to-bed ratio, masking, loudness, true peak, effects on their
  events).

## Routing fixes
- Route each issue to the owner of its time range (the act files). Issues spanning 20s or more go
  to a global owner (`Film.tsx`: captions, mix, transitions). Run fixers in parallel on disjoint
  files, and pass the judges' `keep` lists so fixes don't break what works.
- Scores plateau fast and aren't comparable across rounds, because judges recalibrate. Track open
  issues, not the number. After two rework rounds the top issue is usually one only the user can
  decide: stop and ask.
- Your own spot-check after each render still catches things (a per-word duck that pumps, a
  see-through character, floating legs, a blurred last frame). Pull frames at every flagged time
  before reporting "done".

When a film reads as flat, compare it and its anchor the same way, a frame every second or so:
share of near-flat and near-black area, edge density, mean chroma, repeated frames (perceptual
hash), and motion with camera movement separated from objects moving. Put matched beats side by
side at the same size.

## Mute test
Does the picture tell the story without the voice? Run it on the animatic and on the final cut.
1. Render the cut with no captions and no sound; captions would hand the judge the narration.
2. Give a fresh judge (it has never seen the script, the plans or your notes) three frames per two
   seconds in order, with timestamps, and ask: "Describe what happens and what it explains, second
   by second. Say where you can't tell."
3. List the script's claims, one per sentence. A claim is recovered when the judge's account
   states it or shows its mechanism.
4. Pass: at least 80% recovered. Each missed claim goes back to its shot with the judge's words.

## Restart after a rejected cut
When the user rejects a whole cut ("low quality", "not immersive", "start over"), the problem is
the pictures or the concept, not the shots.
1. Stop all builds and renders.
2. Run an independent evaluator: a fresh agent that judges from the finished film (and any
   reference film) first, then reads the plans only to diagnose process causes. Give it the films
   and the script, not your own diagnosis. It writes a verdict, ranked problems with timestamps and
   frames, what to keep, and two or three different directions.
3. Take the user's notes on it, write the lessons into the project, and record what the user locks
   (often the script, the voice and any camera footage).
4. Restart at step 1 of the skill, finding the pictures again. A new agent with the lessons file
   avoids inheriting the old plan's assumptions.
