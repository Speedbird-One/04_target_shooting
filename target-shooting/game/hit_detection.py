"""
hit_detection: figures out whether a click landed on a target.
"""


def check_hit(targets, click_pos):
    """
    Returns the target that was clicked, or None if the click missed
    every target.
    """
    for target in targets:
        rect = target.get_bounding_rect()
        cx, cy = rect.topleft          # actual centre of the circle
        radius = rect.width / 2
        dx, dy = click_pos[0] - cx, click_pos[1] - cy
        if dx * dx + dy * dy <= radius * radius:
            return target
    return None
