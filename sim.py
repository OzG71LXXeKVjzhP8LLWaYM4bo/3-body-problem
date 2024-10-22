import pygame
from gravity import Body, update_velocities
from collision import check_collision, handle_collision
import math
import csv

# Constants
SCALE = 1e8  # Initial scale for rendering
TIMESTEP = 2000000  # Adjust timestep for faster simulation
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
    # Body 1 and 2: Same mass and stable orbit
    mass = 1e25
    orbit = 1e10
    velocity = math.sqrt(6.674e-11 * mass / orbit)
    body1 = Body(x=0, y=0, mass=mass, vx=0, vy=0, color=(255, 0, 0))
    body2 = Body(x=orbit, y=0, mass=mass, vx=0, vy=-velocity, color=(0, 0, 255))

    return [body1, body2]


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
    time_in_simulator = 0
    last_dump_time = 0

    with open('output.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'time',
            'distance',
            'body1_vx', 'body1_vy',
            'body2_vx', 'body2_vy',
        ])

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

        # Calculate distance between the two bodies
        if len(bodies) >= 2:
            distance = math.hypot(bodies[0].x - bodies[1].x, bodies[0].y - bodies[1].y)

        # Dump data to file once every year
        if time_in_simulator - last_dump_time >= 24 * 3600 * 365:
            with open('output.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    round(time_in_simulator / (24 * 3600 * 365), 2),
                    round(distance / 1000, 2),
                    round(bodies[0].vx / 1000, 2), round(bodies[0].vy / 1000, 2),
                    round(bodies[1].vx / 1000, 2), round(bodies[1].vy / 1000, 2),
                ])
            last_dump_time = time_in_simulator

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
        time_in_simulator += TIMESTEP

    pygame.quit()



if __name__ == "__main__":
    main()