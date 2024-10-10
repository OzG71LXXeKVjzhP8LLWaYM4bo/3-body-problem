import pygame
from gravity import Body, update_velocities
from collision import check_collision, handle_collision
import math

# Constants
SCALE = 1e8  # Initial scale for rendering
TIMESTEP = 1000000  # Adjust timestep for faster simulation
MASS_SCALE = 1e-10  # Adjust this value to control size scaling based on mass
PAN_SPEED = 0.5  # Slow down panning by applying this factor

# Pygame setup
def initialize_pygame():
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    return screen, clock

# Define celestial bodies
def create_celestial_bodies():
    # Sun
    body1 = Body(x=0, y=0, mass=1.9885e30, vx=0, vy=0, color=(255, 255, 0))

    # Mercury
    mercury_orbit = 5.791e10  # average distance from Sun
    mercury_velocity = math.sqrt(6.674e-11 * body1.mass / mercury_orbit)
    body2 = Body(x=mercury_orbit, y=0, mass=3.302e23, vx=0, vy=-mercury_velocity, color=(128, 128, 128))

    # Venus
    venus_orbit = 1.082e11  # average distance from Sun
    venus_velocity = math.sqrt(6.674e-11 * body1.mass / venus_orbit)
    body3 = Body(x=venus_orbit, y=0, mass=4.869e24, vx=0, vy=-venus_velocity, color=(255, 128, 128))

    # Earth
    earth_orbit = 1.496e11  # average distance from Sun
    earth_velocity = math.sqrt(6.674e-11 * body1.mass / earth_orbit)
    body4 = Body(x=earth_orbit, y=0, mass=5.972e24, vx=0, vy=-earth_velocity, color=(0, 0, 255))

    # Mars
    mars_orbit = 2.279e11  # average distance from Sun
    mars_velocity = math.sqrt(6.674e-11 * body1.mass / mars_orbit)
    body5 = Body(x=mars_orbit, y=0, mass=6.39e23, vx=0, vy=-mars_velocity, color=(255, 0, 0))

    # Jupiter
    jupiter_orbit = 7.783e11  # average distance from Sun
    jupiter_velocity = math.sqrt(6.674e-11 * body1.mass / jupiter_orbit)
    body6 = Body(x=jupiter_orbit, y=0, mass=1.898e27, vx=0, vy=-jupiter_velocity, color=(255, 255, 128))

    # Saturn
    saturn_orbit = 1.43e12  # average distance from Sun
    saturn_velocity = math.sqrt(6.674e-11 * body1.mass / saturn_orbit)
    body7 = Body(x=saturn_orbit, y=0, mass=5.68e26, vx=0, vy=-saturn_velocity, color=(128, 128, 255))

    # Uranus
    uranus_orbit = 2.88e12  # average distance from Sun
    uranus_velocity = math.sqrt(6.674e-11 * body1.mass / uranus_orbit)
    body8 = Body(x=uranus_orbit, y=0, mass=8.68e25, vx=0, vy=-uranus_velocity, color=(0, 255, 0))

    # Neptune
    neptune_orbit = 4.497e12  # average distance from Sun
    neptune_velocity = math.sqrt(6.674e-11 * body1.mass / neptune_orbit)
    body9 = Body(x=neptune_orbit, y=0, mass=1.02e26, vx=0, vy=-neptune_velocity, color=(0, 0, 128))

    return [body1, body2, body3, body4, body5, body6, body7, body8, body9]

# Zoom control variables
class ZoomController:
    def __init__(self):
        self.zoom_factor = 1.1  # Scale for zooming in and out
        self.min_scale = 1e7
        self.max_scale = 1e12
        self.pan_offset_x, self.pan_offset_y = 0, 0  # Initial pan offsets

    def zoom_in(self, mouse_x, mouse_y, scale):
        zoom_point_x = (mouse_x - 400 - self.pan_offset_x) * scale
        zoom_point_y = (mouse_y - 300 - self.pan_offset_y) * scale
        scale /= self.zoom_factor
        self.pan_offset_x += int((zoom_point_x / scale - (mouse_x - 400)) / scale)
        self.pan_offset_y += int((zoom_point_y / scale - (mouse_y - 300)) / scale)
        if scale < self.min_scale:
            scale = self.min_scale
        return scale

    def zoom_out(self, mouse_x, mouse_y, scale):
        zoom_point_x = (mouse_x - 400 - self.pan_offset_x) * scale
        zoom_point_y = (mouse_y - 300 - self.pan_offset_y) * scale
        scale *= self.zoom_factor
        self.pan_offset_x -= int((zoom_point_x / scale - (mouse_x - 400)) / scale)
        self.pan_offset_y -= int((zoom_point_y / scale - (mouse_y - 300)) / scale)
        if scale > self.max_scale:
            scale = self.max_scale
        return scale

# Pan control variables
class PanController:
    def __init__(self):
        self.is_panning = False
        self.mouse_start_x, self.mouse_start_y = 0, 0

    def start_panning(self, mouse_x, mouse_y):
        self.is_panning = True
        self.mouse_start_x, self.mouse_start_y = mouse_x, mouse_y

    def stop_panning(self):
        self.is_panning = False

    def pan(self, mouse_x, mouse_y):
        if self.is_panning:
            pan_offset_x = (mouse_x - self.mouse_start_x) * PAN_SPEED
            pan_offset_y = (mouse_y - self.mouse_start_y) * PAN_SPEED
            self.mouse_start_x, self.mouse_start_y = mouse_x, mouse_y
            return pan_offset_x, pan_offset_y
        return 0, 0

# Calculate radius based on mass
def calculate_radius(mass):
    a = math.cbrt(mass) * MASS_SCALE * 5
    return int(a)

# Main loop
def main():
    screen, clock = initialize_pygame()
    bodies = create_celestial_bodies()
    zoom_controller = ZoomController()
    pan_controller = PanController()
    scale = SCALE
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up -> zoom in
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    scale = zoom_controller.zoom_in(mouse_x, mouse_y, scale)
                elif event.button == 5:  # Scroll down -> zoom out
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    scale = zoom_controller.zoom_out(mouse_x, mouse_y, scale)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                pan_controller.start_panning(mouse_x, mouse_y)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                pan_controller.stop_panning()

            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                pan_offset_x, pan_offset_y = pan_controller.pan(mouse_x, mouse_y)
                zoom_controller.pan_offset_x += pan_offset_x
                zoom_controller.pan_offset_y += pan_offset_y

        # List to keep track of bodies to merge
        bodies_to_merge = []

        # Update forces and velocities
        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                if check_collision(bodies[i], bodies[j]):
                    # Mark these bodies for merging
                    merged_body = handle_collision(bodies[i], bodies[j])
                    bodies_to_merge.append((i, j, merged_body))
                else:
                    update_velocities(bodies[i], bodies[j], TIMESTEP)

        # Handle merging after all checks are done
        for (i, j, merged_body) in bodies_to_merge:
            bodies[i] = merged_body  # Replace one of the bodies with the merged body
            bodies.pop(j)  # Remove the other body

        # Update positions
        for body in bodies:
            body.update_position(TIMESTEP)

        # Clear the screen
        screen.fill((0, 0, 0))

        # Draw bodies
        for body in bodies:
            # Adjust body positions based on the current scale and pan offsets
            body_x = int(body.x / scale + 400 + zoom_controller.pan_offset_x)
            body_y = int(body.y / scale + 300 + zoom_controller.pan_offset_y)

            # Calculate the radius based on mass
            body_radius = calculate_radius(body.mass)

            # Ensure a minimum size for visibility
            if body_radius < 1:
                body_radius = 1

            pygame.draw.circle(screen, body.color, (body_x, body_y), body_radius)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()