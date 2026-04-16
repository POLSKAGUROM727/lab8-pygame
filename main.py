import pygame
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

MIN_SIZE, MAX_SIZE = 10, 50
# Speeds are in pixels per second (multiply by 60 to keep the same feel at 60 FPS)
MAX_SPEED, MIN_SPEED = 5 * 60, 1 * 60
# Lifespan bounds in seconds
MIN_LIFESPAN: float = 30.0
MAX_LIFESPAN: float = 180.0
# all the fleeing things
FLEE_THRESHOLD = 55
FLEE_RADIUS = 200
NOISE_STRENGTH = 1.2 * 60
# Max degrees the velocity vector can rotate per second (wander)
WANDER_TURN = 5 * 60


def speed_for_size(size: int) -> float:
    """Linearly scale speed (px/s): small squares are fast, big ones are slow."""
    speed = MAX_SPEED - int(
        (size - MIN_SIZE) / (MAX_SIZE - MIN_SIZE) * (MAX_SPEED - MIN_SPEED)
    )
    return float(max(MIN_SPEED, speed))


def random_velocity(size: int) -> tuple[float, float]:
    speed: float = speed_for_size(size)
    vx: float = choice([-1, 1]) * speed
    vy: float = choice([-1, 1]) * speed
    return vx, vy


def random_color() -> tuple[int, int, int]:
    return (randint(50, 255), randint(50, 255), randint(50, 255))


def make_square() -> dict:
    size: int = randint(MIN_SIZE, MAX_SIZE)
    x: int = randint(1, max(1, WIDTH - size - 1))
    y: int = randint(1, max(1, HEIGHT - size - 1))
    vx, vy = random_velocity(size)
    lifespan: float = uniform(MIN_LIFESPAN, MAX_LIFESPAN)
    return {
        "rect": Rect(x, y, size, size),
        "vx": vx,
        "vy": vy,
        "color": random_color(),
        "age": 0.0,
        "lifespan": lifespan,
    }


def wander(sq: dict, dt: float) -> None:
    vel: Vector2 = Vector2(sq["vx"], sq["vy"])
    if vel.length() == 0:
        return
    angle: float = uniform(-WANDER_TURN, WANDER_TURN) * dt
    vel = vel.rotate(angle)
    speed: float = speed_for_size(sq["rect"].width)
    vel = vel.normalize() * speed
    sq["vx"], sq["vy"] = vel.x, vel.y


def resolve_collisions(squares: list[dict]) -> None:
    """Detect and resolve AABB collisions between every pair of squares.
    Pushes overlapping squares apart along the axis of least penetration
    and swaps the relevant velocity component (elastic-ish bounce)."""
    for i in range(len(squares)):
        for j in range(i + 1, len(squares)):
            a, b = squares[i], squares[j]
            if not a["rect"].colliderect(b["rect"]):
                continue

            # Overlap depth on each axis
            overlap_x = min(a["rect"].right, b["rect"].right) - max(
                a["rect"].left, b["rect"].left
            )
            overlap_y = min(a["rect"].bottom, b["rect"].bottom) - max(
                a["rect"].top, b["rect"].top
            )

            if overlap_x < overlap_y:
                # Separate horizontally
                half = overlap_x // 2 + 1
                if a["rect"].centerx < b["rect"].centerx:
                    a["rect"].x -= half
                    b["rect"].x += half
                else:
                    a["rect"].x += half
                    b["rect"].x -= half
                # Swap x velocities
                a["vx"], b["vx"] = b["vx"], a["vx"]
            else:
                # Separate vertically
                half = overlap_y // 2 + 1
                if a["rect"].centery < b["rect"].centery:
                    a["rect"].y -= half
                    b["rect"].y += half
                else:
                    a["rect"].y += half
                    b["rect"].y -= half
                # Swap y velocities
                a["vy"], b["vy"] = b["vy"], a["vy"]


def flee_velocity(small: dict, big_squares: list[dict]) -> tuple[float, float] | None:
    """Return a flee steering impulse (px/s²-scaled nudge) to add to current velocity,
    or None when no big square is within FLEE_RADIUS."""
    small_center: Vector2 = Vector2(small["rect"].center)
    escape: Vector2 = Vector2(0, 0)

    for big in big_squares:
        big_center: Vector2 = Vector2(big["rect"].center)
        diff: Vector2 = small_center - big_center
        distance: float = diff.length()

        if distance == 0:
            continue
        if distance > FLEE_RADIUS:
            continue

        # Weight repulsion by proximity: closer → stronger push
        escape += diff.normalize() * (FLEE_RADIUS - distance)

    if escape.length() == 0:
        return None

    # Normalise then scale to the square's max speed to get the desired flee direction
    escape = escape.normalize()
    noise: Vector2 = Vector2(uniform(-1, 1), uniform(-1, 1)) * NOISE_STRENGTH
    escape += noise

    if escape.length() == 0:
        escape = Vector2(1, 0)

    speed: float = speed_for_size(small["rect"].width)
    # Return a steering impulse: a fraction of the full flee vector to blend each frame
    flee_impulse: Vector2 = escape.normalize() * speed
    return flee_impulse.x, flee_impulse.y


squares = [make_square() for _ in range(15)]

# Classify once; squares don't change size
big_squares = [sq for sq in squares if sq["rect"].width >= FLEE_THRESHOLD]
small_squares = [sq for sq in squares if sq["rect"].width < FLEE_THRESHOLD]

run: bool = True
while run:
    dt: float = clock.tick(FRAMERATE) / 1000.0  # seconds elapsed since last frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    window.fill((30, 30, 30))

    any_reborn: bool = False

    for i, sq in enumerate(squares):
        size: int = sq["rect"].width

        # --- Lifespan: age the square and replace it when it expires ---
        sq["age"] += dt
        if sq["age"] >= sq["lifespan"]:
            squares[i] = make_square()
            any_reborn = True
            continue  # skip the rest of this frame's update for the newborn

        # --- Fleeing logic (small squares only) ---
        is_fleeing: bool = False
        if size < FLEE_THRESHOLD:
            flee_impulse: tuple[float, float] | None = flee_velocity(sq, big_squares)
            if flee_impulse is not None:
                # Add the flee impulse to the current velocity (vector addition),
                # then clamp the magnitude to the square's max speed to prevent runaway acceleration.
                vel: Vector2 = Vector2(sq["vx"], sq["vy"]) + Vector2(flee_impulse)
                max_speed: float = speed_for_size(size)
                if vel.length() > max_speed:
                    vel = vel.normalize() * max_speed
                sq["vx"], sq["vy"] = vel.x, vel.y
                is_fleeing = True

        # --- Wander: gradually rotate velocity so direction changes over time ---
        if not is_fleeing:
            wander(sq, dt)

        # --- Move (delta-time scaled: velocity is in px/s) ---
        sq["rect"].x += int(sq["vx"] * dt)
        sq["rect"].y += int(sq["vy"] * dt)

        # --- Boundary bounce ---
        if sq["rect"].left <= 0:
            sq["rect"].left = 0
            sq["vx"] = abs(sq["vx"])
        elif sq["rect"].right >= WIDTH:
            sq["rect"].right = WIDTH
            sq["vx"] = -abs(sq["vx"])

        if sq["rect"].top <= 0:
            sq["rect"].top = 0
            sq["vy"] = abs(sq["vy"])
        elif sq["rect"].bottom >= HEIGHT:
            sq["rect"].bottom = HEIGHT
            sq["vy"] = -abs(sq["vy"])

        pygame.draw.rect(window, sq["color"], sq["rect"])

    # --- Rebuild size-class lists if any square was reborn this frame ---
    if any_reborn:
        big_squares = [sq for sq in squares if sq["rect"].width >= FLEE_THRESHOLD]
        small_squares = [sq for sq in squares if sq["rect"].width < FLEE_THRESHOLD]

    # --- Square-to-square collision resolution ---
    resolve_collisions(squares)

    fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, (220, 220, 220))
    window.blit(fps_text, (WIDTH - fps_text.get_width() - 8, 8))

    pygame.display.update()

pygame.quit()
