import pygame
import math
import numpy as np
import typer
import logging
import json
import os

COLORS = [
    (217, 237, 146),
    (93, 115, 126),
    (30, 96, 145),
    (62, 63, 63),
    (143, 45, 86),
    (116, 0, 184),
    (56, 4, 14),
]

TRACES_FILE = "traces.json"

class Body:
    def __init__(
        self, x, y, mass, velocity, color, rebound_factor, screen_width, screen_height
    ):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = int(math.sqrt(mass) * 2)
        self.vx, self.vy = velocity
        self.color = color
        self.trace = []
        self.rebound_factor = rebound_factor
        self.screen_width = screen_width
        self.screen_height = screen_height

    def calculate_grav_force(self, bodies: list, g: float):
        force = (0, 0)
        for body in bodies:
            if body != self:
                force += calculate_gravitational_force(self, body, g)
        force1x, force1y = add_tuples(force)
        self.update(force1x, force1y)

    def update(self, force_x: float, force_y: float):
        ax = force_x / self.mass
        ay = force_y / self.mass
        self.vx += ax
        self.vy += ay
        self.x += self.vx
        self.y += self.vy
        self.check_boundaries()
        self.update_trace()

    def update_trace(self):
        self.trace.append((self.x, self.y))
        if len(self.trace) == 100:
            self.trace.pop(0)

    def check_boundaries(self):
        if self.y < 0:
            self.y = 0
            self.vy *= -self.rebound_factor
        elif self.y > self.screen_height:
            self.y = self.screen_height
            self.vy *= -self.rebound_factor
        if self.x < 0:
            self.x = 0
            self.vx *= -self.rebound_factor
        elif self.x > self.screen_width:
            self.x = self.screen_width
            self.vx *= -self.rebound_factor

    def draw(self, screen, previous=False):
        trace_color = (255, 0, 0) if previous else self.color
        trace_alpha = 100 if previous else 255
        for point in self.trace:
            pygame.draw.circle(screen, trace_color, (int(point[0]), int(point[1])), 1)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


def calculate_gravitational_force(p1: Body, p2: Body, g: float) -> tuple:
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    distance = max(1, math.sqrt(dx**2 + dy**2))
    if distance < 40:
        return (0, 0)
    force = (g * p1.mass * p2.mass) / (distance**2)
    angle = math.atan2(dy, dx)
    force_x = force * math.cos(angle)
    force_y = force * math.sin(angle)
    return (force_x, force_y)


def add_tuples(tuple: tuple) -> tuple:
    even = 0
    odd = 0
    for i in range(len(tuple)):
        if i % 2 == 0:
            even += tuple[i]
        else:
            odd += tuple[i]
    return (even, odd)


def save_traces(bodies):
    traces = [body.trace for body in bodies]
    with open(TRACES_FILE, "w") as file:
        json.dump(traces, file)


def load_traces():
    if os.path.exists(TRACES_FILE):
        with open(TRACES_FILE, "r") as file:
            return json.load(file)
    return []


def main(
    width: int = typer.Option(1920, help="Width of the screen"),
    height: int = typer.Option(1080, help="Height of the screen"),
    max_bodies: int = typer.Option(
        10, help="Maximum number of bodies to had to the simulation."
    ),
    rebound_factor: float = typer.Option(
        0.5,
        help="Factor strength to apply when bodies when bodies bounce off the limits of the screen.",
    ),
    mass: int = typer.Option(10, help="Default mass of the bodies."),
    g: int = typer.Option(9.8, help="The gravitational constant."),
    clock: int = typer.Option(
        60, help="Framerate to delay the game to the given ticks."
    ),
):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    previous_traces = load_traces()

    bodies = [
        Body(
            width / 2,
            height / 2,
            mass=mass,
            velocity=(0.1, 0.1),
            color=COLORS[0],
            rebound_factor=rebound_factor,
            screen_height=height,
            screen_width=width,
        )
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_traces(bodies)
                running = False

        screen.fill((0, 0, 0))

        for trace in previous_traces:
            for point in trace:
                pygame.draw.circle(screen, (255, 0, 0), (int(point[0]), int(point[1])), 1)

        for body in bodies:
            body.calculate_grav_force(bodies, g=g)
            body.draw(screen)

        pygame.display.update()
        clock.tick(clock)

    pygame.quit()


if __name__ == "__main__":
    typer.run(main)
