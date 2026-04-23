# Demo Plan — Lost in Time

**Time target:** 7–10 minutes total (gameplay ~5 min · iteration story ~2 min · Q&A ~2 min)

---

## Roles

| Role     | Who        | Responsibility                                                                             |
|----------|------------|--------------------------------------------------------------------------------------------|
| Player 1 (Cowboy) | _Christan_ | WASD controls                                                                              |                                                                            
| Player 2 (Roman) | _Quinn_    | Arrow key controls                                                                         |
| Narrator | _Blake_    | Talks over gameplay — explains what's happening, why decisions were made, fields questions |

The narrator should not also be playing. Splitting the roles keeps the demo clean and lets the players focus on not dying.

---

## Demo Flow

1. **Title screen (30 sec)** — Show menu, mute toggle, and the locked Level 4 padlock.

2. **Level 1 (90 sec)** — P1 climbs and pulls the lever to free caged P2; both reach the exit together and grab the green gem.

3. **Level 2 (90 sec)** — Each player's lever opens the other's gate; one holds the pressure button while the other exits; red gem.

4. **Level 3 (60 sec)** — Navigate the mirrored moving-spike staircases and grab the blue gem from the center platform.

5. **Level 4 (90 sec)** — Show the padlock gone in Level Select, then run the cross-gate finale where each player's lever only opens the other's side.

---

## Iteration Story (2 min, after gameplay)

Blake walks through what changed from the initial prototype to the shipped build:
- Physics: grid-based movement → gravity/acceleration/friction system
- Sprites were added → graphical improvement
- Music was added → overall game improvement
- UI: bare pygame rectangles → arcade-style HUD, pause menu, level complete/game over screens
- Progression: levels were always accessible → gem-collect unlock added late to give players a reason to replay L1–3
- More levels were added → more game to pleay
- Multiplayer: UDP server/client networking added in the final sprint as a stretch goal

---

## Best Moments

These are the 2–3 moments that best represent what the game is:

1. **The Level 1 lever release** — Player 2 is trapped behind a wall with nothing to do while Player 1 climbs. When Player 1 pulls the lever and the wall disappears, it's the clearest possible demonstration of asymmetric co-op. It's also a low-stakes moment so it's easy to land cleanly during a demo.

2. **Level 3 moving hazards gauntlet** — The mirrored staircase with patrolling spikes is the most visually striking part of the game. It shows that the platforming has real timing skill involved, and the symmetry makes it obvious both players are experiencing parallel challenges.

3. **Level 4 cross-gate reveal** — The moment where Player 1 pulls a lever and nothing opens for them — it opens for Player 2 across the map — is the design idea the whole game is building toward. If there's time for only one "wow" moment, this is it.

---

## Backup Plan

Video with level demo

---

## Time Budget

| Segment              | Target time |
|----------------------|-------------|
| 1. Title screen      | 0:30        |
| 2. Level 1           | 1:30        |
| 3. Level 2           | 1:30        |
| 4. Level 3           | 1:00        |
| 5. Level 4           | 1:30        |
| Iteration story      | 2:00        |
| Q&A                  | 2:00        |
| **Total**            | **~10:00**  |
