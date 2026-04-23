# Postmortem — Lost in Time

## Team Details

| Field | Info |
|-------|------|
| **Team** | Team A — Lost in Time |
| **Repo** | https://github.com/cchavez09/COMP-323-Project |
| **Build Target** | Windows + Python 3.12 + requirements.txt |
| **Platforms Tested** | Mac & Windows |

> **Note:** Cross-platform multiplayer requires the host to open port 5555 through their firewall.

---

## What Worked Well

- **Co-op level design** — Levels are built so neither player can complete them alone; the collaborative mechanics are the core of what makes the game feel intentional.
- **Visual theming** — Graphics reflect the time-travel premise across all levels, with each era having a distinct look. The Space level stands out with its low-gravity mechanic as a final reward.

---

## What Went Wrong

- **Scope of levels** — We originally planned five levels plus a bonus level, but quickly realized we wouldn't have time to design them well. We cut down to four levels and focused on quality and historic theming over quantity.
- **Multiplayer connectivity** — Cross-platform testing hit a wall when the joining player (Blake, on macOS) couldn't get the screen to display. The fix was creating a firewall rule to open port 5555 on the host machine — not ideal. Even after connecting, macOS introduced noticeable lag. By demo time, we had both players on Windows to get stable performance.

---

## What We'd Do Differently

- **Start level design earlier** — We planned for each level to have a unique mechanic tied to player abilities but didn't have enough time to fully implement it. Starting level prototypes sooner would have given us more room to iterate.
- **Scalable resolution** — The game runs at a fixed 1920×1080, which doesn't adapt well to all machines. We'd make resolution configurable from the start.
- **Settings menu** — A settings option in the pause menu would let players remap keybinds and adjust audio without touching the code.
- **Themed audio** — Per-level music and varied sound effects were cut to keep focus on core gameplay. They'd be a priority in a follow-up.

---

## Playtesting Feedback

When Playtesting with Blake's roommates one of them noted that the bonus level was lacking a bit in new mechanics. One of them suggested a gravity change so that the players were able to jump higher and float like they would in space. We implemented moon gravity only in this level to vary the gameplay up and add a fun challenge to the end of the game. 
