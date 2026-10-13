#!/usr/bin/env python3
"""Choreography gates (references/choreography.md). Three checks, all strict by default:

  python3 motion_check.py script MOTION.json [--words words.json] [--gap 0.75] [--layers 2]
      the motion script before anything is built: beats close enough together, enough happening
      at once in each beat, and every spoken sentence carried by a beat the picture can teach.
  python3 motion_check.py events MOTION.json out/events.json [--tol 3]
      the build against the script: every scripted hero event exported by the scenes, on its frame.
  python3 motion_check.py film RENDER.mp4 --bar BAR.mp4 [--shots shots.json] [--strips DIR]
      the render against the bar film, second by second: how many separate things move, how often
      almost nothing moves, how fast the picture changes. Flags shots below the bar and writes a
      strip of consecutive frames for each flagged second, so a reviewer who only sees stills can
      see that it is still.

MOTION.json: {"fps": 30, "shots": [{"id": "S07", "from": 530, "to": 670, "beats": [
  {"at": 536, "line": "press play", "learn": "what the viewer learns from the picture here",
   "hero": {"id": "play-flip", "does": "the play glyph flips to pause and the screen ripples"},
   "layers": ["the ribbon starts to lift off the glass", "dust drifts through the screen light"],
   "camera": "pushes in, settles on the flip"}]}]}
Frames are output frames of the delivered film. shots.json: [{"id", "from", "to"}] in the same frames.
Exit status 1 when any check fails, so it can gate a render script.
"""
import json, re, subprocess, sys
from pathlib import Path


def arg(k, d=None):
    return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d


def sentences(words):
    """Spoken sentences [(start s, end s, text)] from aligned words ({w, s, e})."""
    out, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r'[.?!]["”]?$', w['w']):
            out.append((cur[0]['s'], cur[-1]['e'], ' '.join(x['w'] for x in cur)))
            cur = []
    if cur:
        out.append((cur[0]['s'], cur[-1]['e'], ' '.join(x['w'] for x in cur)))
    return out


def check_script(m, words=None, gap_s=0.75, min_layers=2):
    fps, fails = m.get('fps', 30), []
    beats = []
    for sh in m['shots']:
        bs = sorted(sh['beats'], key=lambda b: b['at'])
        if not bs:
            fails.append(f"{sh['id']}: no beats")
            continue
        edges = [sh['from']] + [b['at'] for b in bs] + [sh['to']]
        for a, b in zip(edges, edges[1:]):
            if (b - a) / fps > gap_s:
                fails.append(f"{sh['id']}: {(b - a) / fps:.2f} s with no beat (frames {a}-{b}); limit {gap_s} s")
        for b in bs:
            where = f"{sh['id']}@{b['at']}"
            if not str(b.get('learn', '')).strip():
                fails.append(f"{where}: no 'learn' (what the picture teaches here)")
            if not (b.get('hero') or {}).get('does'):
                fails.append(f"{where}: no hero action")
            if len([x for x in b.get('layers', []) if str(x).strip()]) < min_layers:
                fails.append(f"{where}: {len(b.get('layers', []))} other things moving; needs {min_layers}+ beside the hero")
            beats.append(b['at'] / fps)
    for s, e, text in sentences(words or []):
        if not any(s - 0.2 <= t <= e + 0.2 for t in beats):
            fails.append(f"sentence at {s:.2f}-{e:.2f} s has no beat: {text[:70]}")
    return fails


def check_events(m, events, tol=3):
    have = {}
    for ev in events:
        have.setdefault(ev['id'], []).append(ev['fr'])
    fails = []
    for sh in m['shots']:
        for b in sh['beats']:
            hid, at = b['hero'].get('id'), b['at']
            if not hid:
                fails.append(f"{sh['id']}@{at}: hero has no id to find in the events")
            elif hid not in have:
                fails.append(f"{sh['id']}@{at}: hero '{hid}' is not exported by any scene")
            elif min(abs(f - at) for f in have[hid]) > tol:
                fails.append(f"{sh['id']}@{at}: hero '{hid}' exported at {have[hid]}, not within {tol} frames")
    return fails


def readout(path, fps=10, w=108, h=192):
    """Per second of film: [second, separate movers per frame (median), frame change, picture change over 2 s]."""
    import numpy as np
    from scipy import ndimage as nd
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vf', f'fps={fps},scale={w}:{h},format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
    fr = np.stack([nd.gaussian_filter(f, 1.0) for f in fr])
    rows = []
    for s in range(1, len(fr) // fps):
        d = np.abs(np.diff(fr[s * fps - 1:(s + 1) * fps], axis=0))
        movers = []
        for k in d:  # separate moving things: blobs of change above the frame's own 90th percentile
            m = nd.binary_opening(k > max(6.0, np.percentile(k, 90)))
            lab, n = nd.label(m)
            movers.append(int((np.asarray(nd.sum(m, lab, range(1, n + 1))) >= 8).sum()) if n else 0)
        a, b = fr[(s - 1) * fps], fr[min(len(fr) - 1, (s + 1) * fps)]
        a, b = a - a.mean(), b - b.mean()
        rows.append((s, float(np.median(movers)), float(d.mean()), float(1 - (a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-9))))
    return rows


def check_film(render, bar, shots=None, strips=None):
    import numpy as np
    R, B = np.array(readout(render)), np.array(readout(bar))
    lo_movers = np.percentile(B[:, 1], 25)          # the bar's busy-ness: a quarter of its seconds are below this
    few = lambda X: (X[:, 1] <= 2).mean()           # share of seconds where at most two things move
    still = lambda X: (X[:, 2] < 2.0).mean()        # share of nearly still seconds
    print(f"bar {Path(bar).name}: movers median {np.median(B[:, 1]):.0f} (p25 {lo_movers:.0f}), <=2 movers {few(B) * 100:.0f}%, "
          f"still {still(B) * 100:.0f}%, change over 2 s median {np.median(B[:, 3]):.2f}")
    print(f"film {Path(render).name}: movers median {np.median(R[:, 1]):.0f}, <=2 movers {few(R) * 100:.0f}%, "
          f"still {still(R) * 100:.0f}%, change over 2 s median {np.median(R[:, 3]):.2f}")
    fails = []
    if np.median(R[:, 1]) < np.median(B[:, 1]):
        fails.append(f"film: fewer separate things move than in the bar film (median {np.median(R[:, 1]):.0f} vs {np.median(B[:, 1]):.0f})")
    if few(R) > few(B) + 0.02:
        fails.append(f"film: {few(R) * 100:.0f}% of seconds have at most two moving things (bar {few(B) * 100:.0f}%)")
    flagged = [int(s) for s, mv, en, ch in R if mv < lo_movers and ch < np.median(B[:, 3])]
    fps = 30
    for sh in shots or []:
        secs = R[(R[:, 0] * fps >= sh['from']) & (R[:, 0] * fps < sh['to'])]
        if len(secs) and np.median(secs[:, 1]) < lo_movers:
            fails.append(f"{sh['id']}: median {np.median(secs[:, 1]):.0f} separate movers, below the bar's quarter mark {lo_movers:.0f}")
    if flagged:
        fails.append(f"seconds below the bar on both movers and change: {flagged}")
    if strips and flagged:
        Path(strips).mkdir(parents=True, exist_ok=True)
        for s in flagged:  # six frames across the second: what the reviewer can't see in a single still
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s), '-t', '1', '-i', str(render), '-vf',
                            'fps=6,scale=180:-1,tile=6x1', '-frames:v', '1', str(Path(strips) / f'still-{s:04d}s.jpg')], check=True)
    return fails


def demo():
    m = {'fps': 10, 'shots': [{'id': 'A', 'from': 0, 'to': 20, 'beats': [
        {'at': 2, 'learn': 'x', 'hero': {'id': 'h', 'does': 'y'}, 'layers': ['a', 'b']},
        {'at': 9, 'learn': '', 'hero': {'id': 'g', 'does': 'y'}, 'layers': ['a']}]}]}
    f = check_script(m, [{'w': 'Hi.', 's': 0.0, 'e': 0.3}, {'w': 'Late.', 's': 1.95, 'e': 2.0}])
    assert not any('0.70 s with no beat' in x for x in f) and any('1.10 s with no beat' in x for x in f), f
    assert any("no 'learn'" in x for x in f) and any('needs 2+' in x for x in f) and any('sentence at 1.95' in x for x in f), f
    e = check_events(m, [{'id': 'h', 'fr': 3}, {'id': 'g', 'fr': 30}], tol=3)
    assert len(e) == 1 and "'g' exported at [30]" in e[0], e
    print('motion_check demo ok')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'demo'
    if cmd == 'demo':
        demo(); sys.exit()
    if cmd == 'script':
        m = json.loads(Path(sys.argv[2]).read_text())
        w = json.loads(Path(arg('--words')).read_text()) if arg('--words') else None
        fails = check_script(m, w, float(arg('--gap', 0.75)), int(arg('--layers', 2)))
    elif cmd == 'events':
        fails = check_events(json.loads(Path(sys.argv[2]).read_text()), json.loads(Path(sys.argv[3]).read_text()), int(arg('--tol', 3)))
    elif cmd == 'film':
        sh = json.loads(Path(arg('--shots')).read_text()) if arg('--shots') else None
        fails = check_film(sys.argv[2], arg('--bar'), sh, arg('--strips'))
    else:
        sys.exit(__doc__)
    print('\n'.join(['FAIL ' + f for f in fails]) or 'PASS')
    sys.exit(1 if fails else 0)
