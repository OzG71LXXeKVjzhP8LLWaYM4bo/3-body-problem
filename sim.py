import pygame
from gravity import Body, update_velocities
from collision import check_collision, handle_collision
import math

# Constants
SCALE = 1e8  # Initial scale for rendering
TIMESTEP = 4000  # Adjust timestep for faster simulation
MASS_SCALE = 1e-10  # Adjust this value to control size scaling based on mass
PAN_SPEED = 0.5  # Slow down panning by applying this factor

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Define three celestial bodies with realistic masses
body1 = Body(x=1e11, y=0, mass=1.9885e30, vx=0, vy=36430.54, color=(255, 255, 0))  # Sun
body2 = Body(x=-1e11, y=0, mass=1.9885e30, vx=0, vy=36430.54, color=(0, 0, 255))  # Earth

bodies = [body1, body2]

# Zoom control variables
zoom_factor = 1.1  # Scale for zooming in and out
min_scale = 1e7
max_scale = 1e12

# Pan control variables
pan_offset_x, pan_offset_y = 0, 0  # Initial pan offsets
is_panning = False
mouse_start_x, mouse_start_y = 0, 0

def calculate_radius(mass):
    """
    Calculate the radius based on the mass of the body using cube root scaling.
    """
    a = math.cbrt(mass) * MASS_SCALE
    return int(a)

running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Zoom in or out with the mouse scroll wheel
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up -> zoom in
                mouse_x, mouse_y = pygame.mouse.get_pos()
                zoom_point_x = (mouse_x - WIDTH // 2 - pan_offset_x) * SCALE
                zoom_point_y = (mouse_y - HEIGHT // 2 - pan_offset_y) * SCALE
                SCALE /= zoom_factor
                pan_offset_x += int((zoom_point_x / SCALE - (mouse_x - WIDTH // 2)) / SCALE)
                pan_offset_y += int((zoom_point_y / SCALE - (mouse_y - HEIGHT // 2)) / SCALE)
                if SCALE < min_scale:
                    SCALE = min_scale
            elif event.button == 5:  # Scroll down -> zoom out
                mouse_x, mouse_y = pygame.mouse.get_pos()
                zoom_point_x = (mouse_x - WIDTH // 2 - pan_offset_x) * SCALE
                zoom_point_y = (mouse_y - HEIGHT // 2 - pan_offset_y) * SCALE
                SCALE *= zoom_factor
                pan_offset_x -= int((zoom_point_x / SCALE - (mouse_x - WIDTH // 2)) / SCALE)
                pan_offset_y -= int((zoom_point_y / SCALE - (mouse_y - HEIGHT // 2)) / SCALE)
                if SCALE > max_scale:
                    SCALE = max_scale

        # Start panning when the mouse is clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            is_panning = True
            mouse_start_x, mouse_start_y = pygame.mouse.get_pos()

        # Stop panning when the mouse is released
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            is_panning = False

        # Move the pan offset when panning
        if event.type == pygame.MOUSEMOTION and is_panning:
            mouse_current_x, mouse_current_y = pygame.mouse.get_pos()
            # Slow down panning using the PAN_SPEED factor
            pan_offset_x += (mouse_current_x - mouse_start_x) * PAN_SPEED
            pan_offset_y += (mouse_current_y - mouse_start_y) * PAN_SPEED
            mouse_start_x, mouse_start_y = mouse_current_x, mouse_current_y

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

    # Update positions and draw bodies
    for body in bodies:
        body.update_position(TIMESTEP)

        # Adjust body positions based on the current SCALE and pan offsets
        body_x = int(body.x / SCALE + WIDTH // 2 + pan_offset_x)
        body_y = int(body.y / SCALE + HEIGHT // 2 + pan_offset_y)

        # Calculate the radius based on mass
        body_radius = calculate_radius(body.mass)

        # Ensure a minimum size for visibility
        if body_radius < 1:
            body_radius = 1

        pygame.draw.circle(screen, body.color, (body_x, body_y), body_radius)

    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
