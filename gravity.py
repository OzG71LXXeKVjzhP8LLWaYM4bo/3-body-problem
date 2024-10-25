import math

G = 6.67430e-11

class Body:
    def __init__(self, x, y, mass, vx=0, vy=0, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.mass = mass
        self.vx = vx
        self.vy = vy
        self.color = color

    def update_position(self, dt):
        """Update the position of the body based on its velocity."""
        self.x += self.vx * dt
        self.y += self.vy * dt

    def calculate_gravitational_force(self, other):
        """Calculate the gravitational force between this body and another body."""
        dx = other.x - self.x
        dy = other.y - self.y
        epsilon = 1e3
        distance = math.sqrt(dx ** 2 + dy ** 2 + epsilon ** 2)

        force = G * self.mass * other.mass / distance ** 2

        fx = force * dx / distance
        fy = force * dy / distance

        return fx, fy

def update_velocities(body1, body2, dt):
    """Update the velocities of two bodies based on the gravitational force they exert on each other."""
    fx, fy = body1.calculate_gravitational_force(body2)

    body1.vx += fx / body1.mass * dt
    body1.vy += fy / body1.mass * dt

    body2.vx -= fx / body2.mass * dt
    body2.vy -= fy / body2.mass * dt
