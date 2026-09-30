# Target Shooting Lab

**Name:** Tanmay T A

**SRN:** PES1UG24CS492

**Section:** I

This project is a single-topic Target Shooting game using **Pygame**.
It introduces students to click-based hit detection, entity movement
within bounds, and streak-based scoring, using a small, readable
object-oriented codebase.

---

## What's Provided

A working Target Shooting game with:

- A handful of circular targets scattered around the play area
- Clicking a target removes it and spawns a fresh one elsewhere;
  clicking empty space counts as a miss
- A running hit/miss count

It has **one deliberate bug** and **three features** left for you to
build. You are expected to **analyze**, **interact with an AI
assistant**, and **complete/fix** the game to make it fully functional
and more interesting.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**

---

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the game:

```bash
python main.py
```

**Controls:** Left-click a target to hit it.

---

## Tasks to Complete

Each task must be completed using an iterative process involving LLM
suggestions and your critical code review.

### Task 1: Fix the hit-detection bug

> A click is supposed to register as a hit only when it lands inside
> the visible circle of a target. In the current build,
> `Target.get_bounding_rect` (in `game/target.py`) builds its hitbox
> as `pygame.Rect(self.x, self.y, radius*2, radius*2)` - but `x, y` is
> the **center** of the circle, not its top-left corner. That shifts
> the entire hitbox down and to the right of where the target actually
> appears, so clicks near one edge of a target can miss it, while
> clicks clearly outside the other edge can register as a hit. Fix the
> hit test in `check_hit` (in `game/hit_detection.py`) so it's based
> on the target's real circular shape.

### Task 2: Implement moving targets

> Make the targets move within the play area instead of sitting still,
> using at least two different speeds or movement patterns. Targets
> should bounce off the edges of the play area rather than leaving the
> screen, and clicking one accurately should still work while it's
> moving.

### Task 3: Implement combo scoring

> Add a score and combo multiplier. Each hit should add points based
> on the current combo multiplier, and consecutive hits (with no
> misses in between) should raise that multiplier so later hits are
> worth more. A miss should reset the combo. Display both the score
> and the current combo multiplier during play.

### Task 4: Implement a timed shooting round

> Add a 30-second countdown for the round. Display the remaining time
> on screen. Once it reaches zero, no further shots should be
> accepted, the final score should be shown clearly, and a new round
> should be startable with the score, combo, and timer all reset.

---

## Expected Behavior

- Clicking squarely inside a visible target should always register as
  a hit; clicking clearly outside every target should always register
  as a miss - test this specifically near the edges of a target, not
  just dead center.
- Targets move continuously and stay within the play area at all
  times.
- Hits build a combo (more points per hit the longer the streak); a
  single miss brings the combo back down.
- The round lasts exactly 30 seconds. Once time runs out, clicks
  should no longer do anything, and the final score should be shown
  clearly.

---

## Folder Structure

```
target-shooting/
├── main.py
├── requirements.txt
├── game/
│   ├── game_engine.py
│   ├── target.py
│   ├── hit_detection.py
│   └── renderer.py
└── README.md
```

---

## Submission Checklist

Submission is only the following three things:

- [ ] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [ ] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [ ] The Chat/LLM used page link, with the complete chat history
