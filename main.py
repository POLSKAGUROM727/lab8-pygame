import pygame
from collections import deque
from pygame.locals import Rect
from pygame.math import Vector2
from random import randint, choice, uniform

pygame.init()

WIDTH, HEIGHT = 1000, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Random Squares")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)


FRAMERATE = 60
NUM_SQUARES = 5
MIN_SIZE, MAX_SIZE = 4, 25
MAX_SPEED, MIN_SPEED = 5 * 60, 1 * 60
MIN_LIFESPAN: float = 3.0
MAX_LIFESPAN: float = 20.0
FLEE_THRESHOLD = 55
FLEE_RADIUS = 200
NOISE_STRENGTH = 1.2 * 60
WANDER_TURN = 5 * 60
GROWTH_RATIO: float = 0.25
MAX_GROWTH_SIZE: int = 80
TRAILS_LENGTH: int = 30

# Refactoring: Dictionary key constants prevent typos and improve maintainability.
# Rather than using magic strings like sq["vx"], we use constants so typos are caught at definition time.
SQ_RECT = "rect"
SQ_VX = "vx"
SQ_VY = "vy"
SQ_COLOR = "color"
SQ_AGE = "age"
SQ_LIFESPAN = "lifespan"
SQ_TRAIL = "trail"

EFX_TYPE = "type"
EFX_CX = "cx"
EFX_CY = "cy"
EFX_COLOR = "color"
EFX_AGE = "age"
EFX_DURATION = "duration"
EFX_SIZE = "size"
EFX_MAX_RADIUS = "max_radius"

pygame.mixer.music.load("DOGsoundtrack.mp3")
pygame.mixer.music.play(-1)


def speed_for_size(size: int) -> float:
    speed = MAX_SPEED - int(
        (size - MIN_SIZE) / (MAX_SIZE - MIN_SIZE) * (MAX_SPEED - MIN_SPEED)
    )
    return float(max(MIN_SPEED, speed))


def random_velocity(size: int) -> tuple[float, float]:
    # Refactoring: This function remains unchanged but supports the refactored make_square.
    speed: float = speed_for_size(size)
    vx: float = choice([-1, 1]) * speed
    vy: float = choice([-1, 1]) * speed
    return vx, vy


def random_color() -> tuple[int, int, int]:
    return (randint(50, 255), randint(50, 255), randint(50, 255))


# old function to create squares
def make_square() -> dict:
    size: int = randint(MIN_SIZE, MAX_SIZE)
    x: int = randint(1, max(1, WIDTH - size - 1))
    y: int = randint(1, max(1, HEIGHT - size - 1))
    vx, vy = random_velocity(size)
    lifespan: float = uniform(MIN_LIFESPAN, MAX_LIFESPAN)
    return {
        SQ_RECT: Rect(x, y, size, size),
        SQ_VX: vx,
        SQ_VY: vy,
        SQ_COLOR: random_color(),
        SQ_AGE: 0.0,
        SQ_LIFESPAN: lifespan,
    }


def make_square_with_size(size: int) -> dict:
    x: int = randint(1, max(1, WIDTH - size - 1))
    y: int = randint(1, max(1, HEIGHT - size - 1))
    vx, vy = random_velocity(size)
    lifespan: float = uniform(MIN_LIFESPAN, MAX_LIFESPAN)
    return {
        SQ_RECT: Rect(x, y, size, size),
        SQ_VX: vx,
        SQ_VY: vy,
        SQ_COLOR: random_color(),
        SQ_AGE: 0.0,
        SQ_LIFESPAN: lifespan,
        SQ_TRAIL: deque(maxlen=TRAILS_LENGTH),
    }


# to actually change the amount of squares and the size
squares: list[dict] = (
    [make_square_with_size(25) for _ in range(5)]
    + [make_square_with_size(10) for _ in range(10)]
    + [make_square_with_size(4) for _ in range(30)]
)


# function to make the squares go to the other end of the screen instead of bouncing off the edge
def apply_screen_wrap(sq: dict) -> None:
    sq[SQ_RECT].x = sq[SQ_RECT].x % WIDTH
    sq[SQ_RECT].y = sq[SQ_RECT].y % HEIGHT


def draw_trail(surface: pygame.Surface, sq: dict) -> None:
    trail = sq[SQ_TRAIL]
    if len(trail) < 2:
        return
    r, g, b = sq[SQ_COLOR]
    points = list(trail)
    for k in range(1, len(points)):
        px, py = points[k - 1]
        cx, cy = points[k]
        if abs(cx - px) > WIDTH // 2 or abs(cy - py) > HEIGHT // 2:
            continue
        alpha = int(200 * k / len(points))
        color = (max(0, r - alpha), max(0, g - alpha), max(0, b - alpha))
        pygame.draw.line(surface, color, (px, py), (cx, cy), 1)


def check_collision(a: dict, b: dict) -> bool:
    return a[SQ_RECT].colliderect(b[SQ_RECT])


def grow_square(sq: dict, prey_size: int) -> None:
    old_size: int = sq[SQ_RECT].width
    new_size: int = min(
        old_size + max(1, int(prey_size * GROWTH_RATIO)), MAX_GROWTH_SIZE
    )
    if new_size == old_size:
        return
    center = sq[SQ_RECT].center
    sq[SQ_RECT].width = new_size
    sq[SQ_RECT].height = new_size
    sq[SQ_RECT].center = center
    vel: Vector2 = Vector2(sq[SQ_VX], sq[SQ_VY])
    if vel.length() > 0:
        new_speed: float = speed_for_size(new_size)
        vel = vel.normalize() * new_speed
        sq[SQ_VX], sq[SQ_VY] = vel.x, vel.y


def handle_collisions(squares: list[dict]) -> bool:
    any_eaten: bool = False
    for i in range(len(squares)):
        for j in range(i + 1, len(squares)):
            a = squares[i]
            b = squares[j]
            if check_collision(a, b):
                size_a = a[SQ_RECT].width
                size_b = b[SQ_RECT].width
                if size_a > size_b:
                    grow_square(a, size_b)
                    spawn_effect(b, "death")
                    squares[j] = make_square_with_size(size_b)
                    spawn_effect(squares[j], "rebirth")
                    any_eaten = True
                elif size_b > size_a:
                    grow_square(b, size_a)
                    spawn_effect(a, "death")
                    squares[i] = make_square_with_size(size_a)
                    spawn_effect(squares[i], "rebirth")
                    any_eaten = True
                else:
                    a[SQ_VX], b[SQ_VX] = b[SQ_VX], a[SQ_VX]
                    a[SQ_VY], b[SQ_VY] = b[SQ_VY], a[SQ_VY]
    return any_eaten


def wander(sq: dict, dt: float) -> None:
    # Refactoring: Updated to use dictionary key constants for consistency.
    vel: Vector2 = Vector2(sq[SQ_VX], sq[SQ_VY])
    if vel.length() == 0:
        return
    angle: float = uniform(-WANDER_TURN, WANDER_TURN) * dt
    vel = vel.rotate(angle)
    speed: float = speed_for_size(sq[SQ_RECT].width)
    vel = vel.normalize() * speed
    sq[SQ_VX], sq[SQ_VY] = vel.x, vel.y


def flee_velocity(small: dict, big_squares: list[dict]) -> tuple[float, float] | None:
    # Refactoring: Uses dictionary key constants instead of magic strings (e.g., SQ_RECT instead of "rect").
    # This prevents typos and makes code easier to maintain if the square structure changes.
    small_center: Vector2 = Vector2(small[SQ_RECT].center)
    escape: Vector2 = Vector2(0, 0)

    for big in big_squares:
        big_center: Vector2 = Vector2(big[SQ_RECT].center)
        diff: Vector2 = small_center - big_center
        distance: float = diff.length()

        if distance == 0:
            continue
        if distance > FLEE_RADIUS:
            continue

        escape += diff.normalize() * (FLEE_RADIUS - distance)

    if escape.length() == 0:
        return None

    escape = escape.normalize()
    noise: Vector2 = Vector2(uniform(-1, 1), uniform(-1, 1)) * NOISE_STRENGTH
    escape += noise

    if escape.length() == 0:
        escape = Vector2(1, 0)

    speed: float = speed_for_size(small[SQ_RECT].width)
    flee_impulse: Vector2 = escape.normalize() * speed
    return flee_impulse.x, flee_impulse.y


# Refactoring: Removed chase_velocity function (was unused).
# Why: Dead code clutters the codebase and confuses readers about what the program actually does.
# The main loop only uses flee_velocity for small squares avoiding large ones.


big_squares: list[dict] = [sq for sq in squares if sq[SQ_RECT].width >= FLEE_THRESHOLD]
small_squares: list[dict] = [sq for sq in squares if sq[SQ_RECT].width < FLEE_THRESHOLD]

effects: list[dict] = []


def update_square_state(
    i: int, sq: dict, dt: float, big_squares: list[dict], small_squares: list[dict]
) -> bool:
    # Refactoring: Extracted square update logic from the main loop into a helper function.
    # Why: Makes it easier to test and understand the logic step-by-step.
    # This function handles: age update, lifespan check, fleeing/wandering behavior, and position update.
    # Returns True if the square was reborn, False otherwise (used to update big/small square lists).
    size: int = sq[SQ_RECT].width

    # Update age and check for lifespan expiration
    sq[SQ_AGE] += dt
    if sq[SQ_AGE] >= sq[SQ_LIFESPAN]:
        spawn_effect(sq, "death")
        squares[i] = make_square_with_size(size)
        spawn_effect(squares[i], "rebirth")
        return True

    # Decide between fleeing (small squares near big ones) or wandering (default behavior)
    is_fleeing: bool = False
    if size < FLEE_THRESHOLD:
        flee_impulse: tuple[float, float] | None = flee_velocity(sq, big_squares)
        if flee_impulse is not None:
            vel: Vector2 = Vector2(sq[SQ_VX], sq[SQ_VY]) + Vector2(flee_impulse)
            max_speed: float = speed_for_size(size)
            if vel.length() > max_speed:
                vel = vel.normalize() * max_speed
            sq[SQ_VX], sq[SQ_VY] = vel.x, vel.y
            is_fleeing = True

    if not is_fleeing:
        wander(sq, dt)

    # Update position based on velocity and delta time
    sq[SQ_RECT].x += int(sq[SQ_VX] * dt)
    sq[SQ_RECT].y += int(sq[SQ_VY] * dt)

    return False


def spawn_effect(sq: dict, effect_type: str) -> None:
    # Refactoring: Consolidated spawn_death_effect and spawn_rebirth_effect into a single function.
    # Why: Reduces code duplication (DRY principle) and makes it easy to add new effect types.
    # Effect-specific values (duration, max_radius) are defined based on effect_type.
    effect_data = {
        EFX_TYPE: effect_type,
        EFX_CX: sq[SQ_RECT].centerx,
        EFX_CY: sq[SQ_RECT].centery,
        EFX_COLOR: sq[SQ_COLOR],
        EFX_AGE: 0.0,
    }
    # Type-specific configuration: death effect shrinks and fades; rebirth expands and fades
    if effect_type == "death":
        effect_data[EFX_SIZE] = float(sq[SQ_RECT].width)
        effect_data[EFX_DURATION] = 0.35
    elif effect_type == "rebirth":
        effect_data[EFX_MAX_RADIUS] = sq[SQ_RECT].width * 2.5
        effect_data[EFX_DURATION] = 0.45
    effects.append(effect_data)


def update_and_draw_effects(surface: pygame.Surface, dt: float) -> None:
    # Refactoring: Uses dictionary key constants (e.g., EFX_AGE instead of "age") for consistency.
    alive: list[dict] = []
    for fx in effects:
        fx[EFX_AGE] += dt
        t: float = min(fx[EFX_AGE] / fx[EFX_DURATION], 1.0)

        if fx[EFX_TYPE] == "death":
            current_size: int = max(1, int(fx[EFX_SIZE] * (1.0 - t)))
            alpha: int = int(255 * (1.0 - t))
            surf = pygame.Surface((current_size, current_size), pygame.SRCALPHA)
            r, g, b = fx[EFX_COLOR]
            surf.fill((r, g, b, alpha))
            rect = surf.get_rect(center=(fx[EFX_CX], fx[EFX_CY]))
            surface.blit(surf, rect)

        elif fx[EFX_TYPE] == "rebirth":
            radius: int = max(1, int(fx[EFX_MAX_RADIUS] * t))
            alpha = int(255 * (1.0 - t))
            diam: int = radius * 2 + 4
            surf = pygame.Surface((diam, diam), pygame.SRCALPHA)
            r, g, b = fx[EFX_COLOR]
            pygame.draw.circle(
                surf, (r, g, b, alpha), (diam // 2, diam // 2), radius, 3
            )
            rect = surf.get_rect(center=(fx[EFX_CX], fx[EFX_CY]))
            surface.blit(surf, rect)

        if fx[EFX_AGE] < fx[EFX_DURATION]:
            alive.append(fx)

    effects[:] = alive


# Refactoring: Simplified main loop by extracting update logic into helper functions.
# This makes the game flow much clearer: handle input → update squares → render → display.
# The loop now reads almost like pseudocode, with details hidden in well-named functions.
run: bool = True
while run:
    dt: float = clock.tick(FRAMERATE) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    window.fill((30, 30, 30))

    any_reborn: bool = False

    # Update all squares: age, lifespan, behavior (fleeing/wandering), and position
    for i, sq in enumerate(squares):
        reborn = update_square_state(i, sq, dt, big_squares, small_squares)
        if reborn:
            any_reborn = True
        else:
            apply_screen_wrap(sq)
            sq[SQ_TRAIL].append(sq[SQ_RECT].center)
            draw_trail(window, sq)
            pygame.draw.rect(window, sq[SQ_COLOR], sq[SQ_RECT])

    any_eaten: bool = handle_collisions(squares)

    if any_reborn or any_eaten:
        big_squares = [sq for sq in squares if sq[SQ_RECT].width >= FLEE_THRESHOLD]
        small_squares = [sq for sq in squares if sq[SQ_RECT].width < FLEE_THRESHOLD]

    update_and_draw_effects(window, dt)

    fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, (220, 220, 220))
    window.blit(fps_text, (WIDTH - fps_text.get_width() - 8, 8))

    pygame.display.update()

pygame.quit()
