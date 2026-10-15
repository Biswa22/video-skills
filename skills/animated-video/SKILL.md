---
name: animated-video
description: >-
  Make animated videos in code with Remotion (React, SVG, three.js): explainers, character
  stories, motion graphics, kinetic typography, paper collage and animated infographics, in 2D or 3D, from a
  script or voiceover, in any aspect ratio. Use when asked to animate a script, make an
  animated video or Reel, or motion graphics. Not for editing camera footage (video-edit) or
  AI-generated clips (higgsfield-*).
---

# Animated video

Turn a brief into a finished animated video in which every image is made in code: drawn
procedurally, or built from approved sourced assets placed and rendered deterministically.
Footage from image or video generators is a separate route (step 2). A film is finished when
every line is shown by a picture worth watching, the opening earns attention, every shot meets
the finish bar, and the review checks pass.

## What makes the film

**Be as inventive as the idea allows.** For every concept the film shows, look for the most
surprising picture that still makes it click. Wacky, impossible, funny or beautiful ideas are
welcome, and each is judged by one test: does the viewer understand the mechanism faster, or
remember it longer, than with the literal picture? The literal depiction is the fallback that
wins only when nothing beats it. Accuracy checks an idea; a metaphor the narration grounds stays.
Finding these pictures is your job, done before anything goes to the user
([find the pictures](references/explainer.md#find-the-pictures)).

**Colour tells the eye where to look.** Before style frames, write a colour key: a quiet ground
for the world (dark or pale, low in saturation); one hot accent reserved for the thing the viewer
follows, always the brightest, most saturated thing in frame; and one or two more colours, each
meaning exactly one thing (the infrastructure, the danger, the other side). Everything else stays
desaturated. A colour keeps its meaning for the whole film, and a new meaning is taught on screen
once. The palette is chosen per film; this structure holds in every style.

**Design fresh for each brief.** Every example in these references, and every past film, is one
choice among many: take the principle, then design this brief's own answer. A past film the user
liked sets the bar for finish and pace, never for ideas, devices or look.

**Feedback narrows a picture, never the imagination.** When the user rejects an idea, write down
what was wrong with that idea (it confused, felt forced, looked cheap) and find a better one of
any kind. A rejection becomes a rule about a whole category only when the user states it as one.

**Ask with a recommendation.** Each question to the user carries your recommended answer and a
one-line reason, so "yes" is a complete reply. At the start, say once that this skill works best
with Claude Opus 5.5 at high or max effort.

## Scale the production to the piece

- **Short (under about 60s):** one agent through every step, checking stills; add parallel
  animators or a judge panel only when a review shows a problem they fix. Finding the pictures and
  the mute test always run.
- **Longer, or many acts:** the full production below. When the user wants parallel agents early,
  give them research, recurring assets and audio; the pictures, concept and animatic stay with one
  agent until approved.
- **An insert for someone else's timeline** (an animated shot inside a camera edit, which
  video-edit owns): [inserts](references/remotion-pipeline.md#inserts-for-another-timeline). When
  it's unclear who owns the timeline, ask once.

## 1. Direct the story and find the pictures

Pick the spine: [a story](references/story.md) (a character who wants something) or
[an explainer](references/explainer.md) (how something works, why, what a number means). Either
way: intake questions in one message; find the pictures yourself (references for this topic,
several ideas per beat from a fresh agent, a pick for surprise and clarity); then three concepts
that genuinely differ, your recommendation, and the chosen one as a timed beat sheet with each
beat's picture. A finished script settles the words, not the pictures. When the video-script
skill is installed, check narration against its checklist. If the film will be sped up for
delivery, lock the speed now.

Done when: the user has approved the concept and the beat sheet with its pictures, for short
pieces too.

## 2. Lock the format and the visual style

- When the request names the format and style, confirm it in one line. Otherwise offer two or
  three styles that genuinely differ, each as a style frame of the same beat with its colour key
  ([visual styles](references/styles.md)).
- Ask about the route and its cost: made in code is free per shot and consistent; AI video costs
  per clip and drifts. For a photoreal or physically detailed world, read
  [realistic 3D](references/realistic-3d.md) first.
- Look up photos of the real objects, places and interfaces the film shows, so the drawing is true
  in its own style. If a real person appears, ask where their footage lives and pull frames with
  ffmpeg.
- Read `~/.animated-video/profile.md` if it exists: the user's preferences and past projects.

Done when: the user has picked a style frame and its colour key.

## 3. Build the audio spine

Every beat times off the narration (or, without one, the music bed, chosen first).
1. VO: prefer the user's recording; before it exists, use
   [stand-in word timings](references/remotion-pipeline.md#before-the-vo-exists). Label TTS as a
   stand-in.
2. `templates/remotion-film/align.py` gives word timestamps and a loudness envelope; derive every
   cue from words with `cue("phrase")`, so a new VO re-times the film.
3. Write captions by hand as sense units. The opening caption is the hook, its own composition:
   larger type revealed word by word, the key word landing hardest.
4. Plan music and effects now; they ship with the first cut. Source: the user's files, the asset
   library or samples on disk, then synthesis (`templates/parts/audio/designed.py`, labelled
   synthetic). Given a reference video, match its music's role.

Done when: every cue resolves against the transcript or stand-in.

## 4. Skeleton, animatic and key-frame board

Write `STORYBOARD.md`: logline, colour key, and a scene table of timing, picture, on-screen text
and transition. Plan what stands behind any presenter insert as part of the film
([compositing bar](references/realistic-3d.md#compositing-cg-with-camera-footage)). Unverified
facts go in `NOTES.md` and stay out of the film. Copy `templates/remotion-film/`, wire acts,
captions and audio, and render stills across the timeline
([pipeline](references/remotion-pipeline.md)).

When meaning lives in motion, build the **animatic**: blocked shapes performing every beat over
the real VO, something visibly changing about every second, checked as frame strips and with the
[mute test](references/review.md#mute-test). Then the **key-frame board**: one still per beat in
the approved style, as one contact sheet with each line beside its frame; wait for the user's notes.

Done when: every act renders end to end with captions and audio, and the user has approved the
animatic and the board. If they want to skip the animatic, say what it would catch, recommend it,
and report a skipped gate at delivery.

## 5. Recurring assets

Search the asset library first when it's installed. Build what appears in more than one shot
first (characters, props, sets, real interfaces, camera language, the finish), each holding at
every scale the story needs: rigs per [character lessons](references/character-rig.md), graphics
per [graphics lessons](references/motion-graphics.md). `templates/parts/` has a globe, an iPhone
running iMessage and designed sounds; restyle them to the film.

Done when: a showcase shows every recurring asset at its used size, with an API summary animators
can use; register reusable ones in the asset library.

## 6. Animate the shots

Write the art bible: look, colour key, cast, staging, safe zones, the style's bar, and this
**finish bar**, which holds in every style:
- **Full frame:** no more than about a quarter of the frame as flat colour; the picture continues
  calmly behind captions.
- **Depth:** foreground, subject, background, with parallax (flat styles use overlap and scale).
- **Light:** the brightest thing is the one the eye should follow, in the hero accent; light
  sources light their surroundings.
- **Real things:** a real object, interface, company or place shown is recognisably itself in the
  style's language; a stand-in gets the same care. A human action shows the hand doing it.
- **Life and intent:** a primary action, secondary action and ambient life in each shot, with
  anticipation and settle; every camera move answers an event.
- **Transitions through content:** a morph, a push through an object, particles that reform.
- **Detail in the picture,** from objects, light and motion; decorative scaffolding (HUD kickers,
  tick marks, corner brackets, fake readouts) stays out.

Per-act briefs point at the key frames and the animatic. The board fixes each beat's idea; the
animator owns how it moves and the details that delight, and proposes a better picture when they
see one. One animator per act, each owning its files; the shared kit stays read-only. The director
owns legibility: could a newcomer retell every shot? Each act exports sound events from the
constants that draw it ([sound events](references/remotion-pipeline.md#sound-events)), with hero
actions on their words. Draw every frame from the frame number and seeded randomness. For dense
three.js motion, use the [motion kit](templates/parts/src/kit/motion/README.md).

Done when: each act's contact sheet tells its beats with the sound off and meets the finish bar
beside its key frames, and the typecheck is clean.

## 7. Review

Extract frames (contact sheets, dense frames around cuts) and measure audio with ffmpeg; play or
listen only when a tool allows, and report which happened. Run independent judges, route issues to
owners by time range, fix in parallel, re-render ([review](references/review.md)).
- Spot-check every flagged moment yourself after each render.
- Compare each act with its anchor: the reference film's frame for that beat, or the key frame.
- Check consecutive frames across each shot's fastest second for flicker, pops and stutter; 3D
  shots also get the [temporal checks](references/realistic-3d.md#temporal-review).
- Keep open issues in `ISSUES.md`; stop when a round gains little or the top issue needs the user.
- When the user rejects a whole cut, restart from the pictures
  ([restart](references/review.md#restart-after-a-rejected-cut)).

## 8. Deliver

Before the first full cut goes out, a fresh judge runs the mute test on it; fix any named defect
that costs a render or less. Render the final (loudness normalized; long films in chunks), check
the first frame, the last second and the loudness. Report the path, open issues, skipped gates,
sourced images, and anything synthetic or invented. Commit each version in the project's git repo.
Small changes to a finished film take the cheapest route that keeps quality, such as an ffmpeg
pass. With the asset library installed, close its catalog (its steps 4–5); otherwise list reusable
pieces in `NOTES.md`.

On request, reflect with [the reflection protocol](references/reflection.md).
