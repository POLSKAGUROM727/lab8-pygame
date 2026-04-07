import pygame
from pygame.locals import Rect
from random import randint, choice

pygame.init()

WIDTH, HEIGHT = 1000, 920
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Random Squares")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)


FRAMERATE = 60

MIN_SIZE, MAX_SIZE = 10, 100
MAX_SPEED, MIN_SPEED = 5, 1


def random_velocity(size):
    # Linearly scale speed: small squares are fast, big ones are slow
    speed = MAX_SPEED - int(
        (size - MIN_SIZE) / (MAX_SIZE - MIN_SIZE) * (MAX_SPEED - MIN_SPEED)
    )
    speed = max(MIN_SPEED, speed)
    vx = choice([-1, 1]) * speed
    vy = choice([-1, 1]) * speed
    return vx, vy


def max_speed():
    return


def random_color():
    return (randint(50, 255), randint(50, 255), randint(50, 255))


def make_square():
    size = randint(MIN_SIZE, MAX_SIZE)
    x = randint(1, max(1, WIDTH - size - 1))
    y = randint(1, max(1, HEIGHT - size - 1))
    vx, vy = random_velocity(size)
    return {"rect": Rect(x, y, size, size), "vx": vx, "vy": vy, "color": random_color()}


squares = [make_square() for _ in range(10)]

run = True
while run:
    clock.tick(FRAMERATE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    window.fill((30, 30, 30))

    for sq in squares:
        sq["rect"].x += sq["vx"]
        sq["rect"].y += sq["vy"]

        if sq["rect"].left <= 0 or sq["rect"].right >= WIDTH:
            sq["vx"] *= -1
            sq["vx"] += choice([-1, 0, 1])  # slight random nudge
        if sq["rect"].top <= 0 or sq["rect"].bottom >= HEIGHT:
            sq["vy"] *= -1
            sq["vy"] += choice([-1, 0, 1])

        pygame.draw.rect(window, sq["color"], sq["rect"])

    fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, (220, 220, 220))
    window.blit(fps_text, (WIDTH - fps_text.get_width() - 8, 8))

    pygame.display.update()

pygame.quit()
