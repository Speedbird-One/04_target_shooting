"""
GameEngine: owns the targets and handles player clicks.

Targets move horizontally, bouncing off the left and right window
edges. Two targets move at a faster speed and one moves much slower.
Targets are spawned in separate horizontal lanes, so they never overlap.
Hits build a combo multiplier that scales the score; a miss resets it.

The game runs in rounds of ROUND_SECONDS. It has three states:
  WAITING  - "Click to Start" screen shown at launch
  PLAYING  - the round is running and the countdown is ticking
  GAME_OVER - final score shown; a click starts a fresh round
"""

import math
import random

import pygame

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

# Rounds
ROUND_SECONDS = 30
RESTART_DELAY_MS = 800  # ignore clicks briefly after time-up so a frantic
                        # final click doesn't skip the results screen

# Game states
WAITING = "waiting"
PLAYING = "playing"
GAME_OVER = "game_over"

COLOR_TEXT = (255, 255, 255)
COLOR_HIGHLIGHT = (255, 220, 80)
COLOR_DIM = (180, 180, 190)


class GameEngine:
    def __init__(self):
        self.state = WAITING
        self.targets = []
        self.round_start_ms = 0
        self.round_end_ms = 0
        self._reset_round_stats()

    # ------------------------------------------------------------------
    # Round management
    # ------------------------------------------------------------------
    def _reset_round_stats(self):
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.combo_multiplier = 1   # applies to the NEXT hit

    def start_round(self):
        """Reset the score and targets, then start the countdown."""
        self._reset_round_stats()
        self.targets = []
        for speed in TARGET_SPEEDS:
            # Add one at a time so each new target is checked against
            # the ones already placed.
            self.targets.append(self._random_target(speed))
        self.round_start_ms = pygame.time.get_ticks()
        self.state = PLAYING

    def time_remaining(self):
        """Seconds left in the round (float, never below 0)."""
        if self.state != PLAYING:
            return 0.0 if self.state == GAME_OVER else float(ROUND_SECONDS)
        elapsed = (pygame.time.get_ticks() - self.round_start_ms) / 1000
        return max(0.0, ROUND_SECONDS - elapsed)

    def _end_round(self):
        self.state = GAME_OVER
        self.round_end_ms = pygame.time.get_ticks()
        self.targets = []

    # ------------------------------------------------------------------
    # Target spawning
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Input / update
    # ------------------------------------------------------------------
    def handle_click(self, pos):
        if self.state == WAITING:
            self.start_round()
            return

        if self.state == GAME_OVER:
            if pygame.time.get_ticks() - self.round_end_ms >= RESTART_DELAY_MS:
                self.start_round()
            return

        # --- PLAYING ---
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
        if self.state != PLAYING:
            return

        if self.time_remaining() <= 0:
            self._end_round()
            return

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

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    @staticmethod
    def _draw_centered(surface, font, text, y, color=COLOR_TEXT):
        """Draw text horizontally centred, with its vertical centre at y."""
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, y))
        surface.blit(surf, rect)

    def draw(self, surface, font, big_font):
        from game import renderer

        if self.state == WAITING:
            renderer.draw_scene(surface, [])
            self._draw_centered(surface, big_font, "Target Shooting", HEIGHT // 2 - 50,
                                COLOR_TEXT)
            self._draw_centered(surface, font, "Click to Start", HEIGHT // 2 + 30,
                                COLOR_HIGHLIGHT)
            return

        if self.state == GAME_OVER:
            renderer.draw_scene(surface, [])
            self._draw_centered(surface, font, "Time's Up!", HEIGHT // 2 - 130, COLOR_DIM)
            self._draw_centered(surface, big_font, f"Score: {self.score}", HEIGHT // 2 - 60)
            self._draw_centered(surface, font,
                                f"Hits: {self.hits}   Misses: {self.misses}",
                                HEIGHT // 2 + 10, COLOR_DIM)
            self._draw_centered(surface, font, "Click to Start", HEIGHT // 2 + 90,
                                COLOR_HIGHLIGHT)
            return

        # --- PLAYING ---
        renderer.draw_scene(surface, self.targets)

        # Top left: hit/miss counters
        renderer.draw_text(surface, font, f"Hits: {self.hits}  Misses: {self.misses}",
                           (TEXT_MARGIN, TEXT_MARGIN))

        # Top centre: countdown (rounded up, so it reads 30 ... 1)
        secs = math.ceil(self.time_remaining())
        timer_text = f"Time: {secs}"
        w, _ = font.size(timer_text)
        renderer.draw_text(surface, font, timer_text,
                           ((WIDTH - w) // 2, TEXT_MARGIN))

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
