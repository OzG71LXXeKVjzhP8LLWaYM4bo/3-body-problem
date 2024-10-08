import math

def check_collision(body1, body2):
    """
    Check if two bodies have collided.
    A collision is detected if the distance between the centers of the two bodies
    is less than the sum of their radii.
    """
    dx = body2.x - body1.x
    dy = body2.y - body1.y
    distance = math.sqrt(dx ** 2 + dy ** 2)
    
    # Calculate the radii of both bodies
    radius1 = calculate_radius(body1.mass)
    radius2 = calculate_radius(body2.mass)
    
    # If distance is smaller than the sum of their radii, we have a collision
    return distance < (radius1 + radius2)

def calculate_radius(mass):
    """
    Calculate the radius based on the mass of the body using cube root scaling.
    """
    MASS_SCALE = 1e-10  # Adjust this to control the radius scaling
    return int(math.cbrt(mass) * MASS_SCALE)

def handle_collision(body1, body2):
    """
    Handle the collision by merging the two bodies into one. 
    This follows the conservation of momentum and mass.
    """
    # Total mass is the sum of the two masses
    new_mass = body1.mass + body2.mass
    
    # Conservation of momentum to calculate new velocity
    new_vx = (body1.vx * body1.mass + body2.vx * body2.mass) / new_mass
    new_vy = (body1.vy * body1.mass + body2.vy * body2.mass) / new_mass
    
    # New position (choose the position of the more massive body)
    if body1.mass > body2.mass:
        new_x, new_y = body1.x, body1.y
    else:
        new_x, new_y = body2.x, body2.y

    # Blend the colors of the two bodies based on mass
    def blend_colors(color1, color2, weight1, weight2):
        return tuple(int((c1 * weight1 + c2 * weight2) / (weight1 + weight2)) for c1, c2 in zip(color1, color2))
    
    new_color = blend_colors(body1.color, body2.color, body1.mass, body2.mass)
    
    # Create a new body with the combined mass, velocity, position, and blended color
    new_body = Body(new_x, new_y, new_mass, new_vx, new_vy, color=new_color)

    return new_body
