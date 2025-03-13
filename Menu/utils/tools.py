from Menu.ui.elements import Particle
from shared.common_ui import *

import random


def generate_particles(particles, n, x1,y1,x2,y2):
    for i in range(n):
        particles.append(Particle(
            random.randint(x1,x2),
            random.randint(y1,y2),
            random.choice([SOFT_ORANGE, PASTEL_PINK, PASTEL_GREEN, PASTEL_YELLOW])
        ))