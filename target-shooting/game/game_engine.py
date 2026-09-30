"""
GameEngine: owns the targets and handles player clicks.

Targets move horizontally, bouncing off the left and right window
edges. Two targets move at a faster speed and one moves much slower.
Targets are spawned in separate horizontal lanes, so they never overlap.
Hits build a combo multiplier that scales the score; a miss resets it.
No timer yet. That's Task 4.
"""

import random

from game.target import Target
from game.hit_detection import check_hit
from game.renderer import WIDTH, HEIGHT

TARGET_RADIUS = 28

# Pixels moved per frame. Two fast targets, one considerably slower.
FAST_SPEED = 3
SLOW_SPEED = 1
TARGET_SPEEDS = [FAST_SPEED, FAST_SPEED, SLOW_SPEED]
NUM_TARGETS = len(TARGET_SPEEDS)

# Minimum vertical distance between any two target centres. Two circles of
# radius r can't touch if their centres are at least 2r apart on one axis,
# so a small margin on top of the diameter keeps them visibly separate.
LANE_MARGIN = 6
MIN_Y_SEPARATION = 2 * TARGET_RADIUS + LANE_MARGIN

# Scoring
BASE_POINTS = 10       # points for a hit at multiplier x1
TEXT_MARGIN = 10       # gap between HUD text and the window edge


class GameEngine:
    def __init__(self):
        self.targets = []
        for speed in TARGET_SPEEDS:
            # Add one at a time so each new target is checked against
            # the ones already placed.
            self.targets.append(self._random_target(speed))
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.combo_multiplier = 1   # applies to the NEXT hit

    def _random_y(self):
        """Pick a y that is at least MIN_Y_SEPARATION from every target
        currently in self.targets."""
        y_min = TARGET_RADIUS + 10
        y_max = HEIGHT - TARGET_RADIUS - 10
        while True:
            y = random.randint(y_min, y_max)
            if all(abs(y - t.y) >= MIN_Y_SEPARATION for t in self.targets):
                return y

    def _random_target(self, speed):
        x = random.randint(TARGET_RADIUS + 10, WIDTH - TARGET_RADIUS - 10)
        y = self._random_y()
        target = Target(x, y, radius=TARGET_RADIUS)
        # Random starting direction, fixed speed magnitude.
        target.vx = random.choice([-1, 1]) * speed
        return target

    def handle_click(self, pos):
        target = check_hit(self.targets, pos)
        if target is not None:
            self.hits += 1

            # Score uses the multiplier as it stands *before* this hit,
            # then the combo grows for the next one.
            self.score += BASE_POINTS * self.combo_multiplier
            self.combo_multiplier += 1

            # Remove first, so the replacement is only checked against the
            # targets that remain (not the one it is replacing).
            self.targets.remove(target)
            # The replacement inherits the speed of the target it replaces,
            # so there are always two fast targets and one slow one.
            self.targets.append(self._random_target(abs(target.vx)))
        else:
            self.misses += 1
            self.combo_multiplier = 1   # a miss breaks the combo

    def update(self):
        for target in self.targets:
            target.x += target.vx

            # Bounce off the left/right edges: clamp inside the window and
            # flip direction so the target never leaves the screen.
            if target.x - target.radius <= 0:
                target.x = target.radius
                target.vx = abs(target.vx)
            elif target.x + target.radius >= WIDTH:
                target.x = WIDTH - target.radius
                target.vx = -abs(target.vx)

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.targets)

        # Top left: hit/miss counters
        renderer.draw_text(surface, font, f"Hits: {self.hits}  Misses: {self.misses}",
                           (TEXT_MARGIN, TEXT_MARGIN))

        # Top right: score
        score_text = f"Score: {self.score}"
        w, _ = font.size(score_text)
        renderer.draw_text(surface, font, score_text,
                           (WIDTH - w - TEXT_MARGIN, TEXT_MARGIN))

        # Bottom right: current combo multiplier
        combo_text = f"Combo: x{self.combo_multiplier}"
        w, h = font.size(combo_text)
        renderer.draw_text(surface, font, combo_text,
                           (WIDTH - w - TEXT_MARGIN, HEIGHT - h - TEXT_MARGIN))
