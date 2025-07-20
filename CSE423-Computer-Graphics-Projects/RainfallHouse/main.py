from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# Global Variables
width, height = 800, 600
shooter_x = width // 2
shooter_width = 50
projectiles = []
falling_circles = []
missed_circles = 0
score = 0
is_game_over = False
game_paused = False
failed_bubbles = 0
last_time = time.time()

# Button Positions
button_size = 35
buttons = {
    "restart": (20, height - 60),
    "play_pause": (width // 2 - 20, height - 60),
    "exit": (width - 60, height - 60),
}


# Utility Functions
def draw_pixel(x, y):
    glVertex2i(int(x), int(y))


def midpoint_circle(xc, yc, r):
    x, y = 0, r
    p = 1 - r
    glBegin(GL_POINTS)
    while x <= y:
        draw_pixel(xc + x, yc + y)
        draw_pixel(xc - x, yc + y)
        draw_pixel(xc + x, yc - y)
        draw_pixel(xc - x, yc - y)
        draw_pixel(xc + y, yc + x)
        draw_pixel(xc - y, yc + x)
        draw_pixel(xc + y, yc - x)
        draw_pixel(xc - y, yc - x)
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
    glEnd()


def draw_rocket(x, y):
    glBegin(GL_LINES)
    glColor3f(1.0, 1.0, 1.0)

    # Rocket body
    glVertex2f(x - 15, y)
    glVertex2f(x + 15, y)
    glVertex2f(x - 15, y)
    glVertex2f(x, y + 40)
    glVertex2f(x + 15, y)
    glVertex2f(x, y + 40)

    # Rocket wings
    glVertex2f(x - 15, y)
    glVertex2f(x - 25, y - 20)
    glVertex2f(x + 15, y)
    glVertex2f(x + 25, y - 20)
    glEnd()


def collision(circle, projectile):
    dx = circle[0] - projectile[0]
    dy = circle[1] - projectile[1]
    return (dx * dx + dy * dy) ** 0.5 < 20


# Function to render text
def render_text(x, y, text, color=(1.0, 1.0, 1.0)):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


# Game Functions
def display():
    global is_game_over, score, missed_circles, failed_bubbles

    glClear(GL_COLOR_BUFFER_BIT)

    # Draw Shooter
    draw_rocket(shooter_x, 50)

    # Draw Projectiles
    glColor3f(0.0, 1.0, 0.0)  # Green for projectiles
    for projectile in projectiles:
        glBegin(GL_LINES)
        glVertex2f(projectile[0], projectile[1])
        glVertex2f(projectile[0], projectile[1] + 10)
        glEnd()

    # Draw Falling Circles
    glColor3f(0.8, 0.7, 0.5)  # Red for falling circles
    for circle in falling_circles:
        midpoint_circle(circle[0], circle[1], 15)

    # Draw Buttons
    draw_buttons()

    # Draw the score at the top left
    render_text(20, height - 30, f"Score: {score}", color=(1.0, 1.0, 0.0))

    # Display Game Over Message
    if is_game_over:
        render_text(width // 2 - 100, height // 2, f"Game Over! Final Score: {score}", color=(1.0, 0.0, 0.0))

    glutSwapBuffers()


def draw_buttons():
    glColor3f(0.5, 0.5, 0.5)

    # Restart Button (Left arrow shape)
    glBegin(GL_LINES)
    glVertex2f(buttons["restart"][0], buttons["restart"][1] - button_size // 2)
    glVertex2f(buttons["restart"][0] + button_size, buttons["restart"][1])
    glVertex2f(buttons["restart"][0], buttons["restart"][1] + button_size // 2)
    glVertex2f(buttons["restart"][0] + button_size, buttons["restart"][1])
    glEnd()

    # Play/Pause Button (Play triangle shape)
    glBegin(GL_LINES)
    glVertex2f(buttons["play_pause"][0] - button_size // 2, buttons["play_pause"][1] + button_size // 2)
    glVertex2f(buttons["play_pause"][0] + button_size // 2, buttons["play_pause"][1])
    glVertex2f(buttons["play_pause"][0] - button_size // 2, buttons["play_pause"][1] - button_size // 2)
    glVertex2f(buttons["play_pause"][0] + button_size // 2, buttons["play_pause"][1])
    glEnd()

    # Exit Button (Red Cross shape)
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex2f(buttons["exit"][0] - button_size // 2, buttons["exit"][1] - button_size // 2)
    glVertex2f(buttons["exit"][0] + button_size // 2, buttons["exit"][1] + button_size // 2)
    glVertex2f(buttons["exit"][0] - button_size // 2, buttons["exit"][1] + button_size // 2)
    glVertex2f(buttons["exit"][0] + button_size // 2, buttons["exit"][1] - button_size // 2)
    glEnd()


def keyboard(key, x, y):
    global shooter_x, is_game_over, game_paused

    if is_game_over:
        return

    if key == b'a':  # Move shooter left
        shooter_x = max(shooter_x - 20, 20)
    elif key == b'd':  # Move shooter right
        shooter_x = min(shooter_x + 20, width - 20)
    elif key == b' ':  # Shoot
        projectiles.append([shooter_x, 60])


def mouse(button, state, x, y):
    global is_game_over, game_paused, score, missed_circles, falling_circles, projectiles

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        y = height - y  # Invert y-coordinate

        # Restart Button
        if (x - buttons["restart"][0]) ** 2 + (y - buttons["restart"][1]) ** 2 < (button_size // 2) ** 2:
            print("Starting Over")
            score = 0
            missed_circles = 0
            failed_bubbles = 0  # Reset failed bubbles count
            falling_circles.clear()
            projectiles.clear()
            is_game_over = False

        # Play/Pause Button
        elif (x - buttons["play_pause"][0]) ** 2 + (y - buttons["play_pause"][1]) ** 2 < (button_size // 2) ** 2:
            game_paused = not game_paused  # Toggle pause state

        # Exit Button
        elif (x - buttons["exit"][0]) ** 2 + (y - buttons["exit"][1]) ** 2 < (button_size // 2) ** 2:
            print(f"Goodbye! Final Score: {score}")
            glutLeaveMainLoop()


def update(value):
    global projectiles, falling_circles, last_time, score, missed_circles, is_game_over, failed_bubbles

    # If game is paused, stop updating
    if game_paused or is_game_over:
        glutPostRedisplay()
        return

    # Time-based movement
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time

    # Move Projectiles
    for projectile in projectiles:
        projectile[1] += 300 * delta_time  # Move upward
    projectiles = [p for p in projectiles if p[1] < height]

    # Move Falling Circles
    for circle in falling_circles:
        circle[1] -= 100 * delta_time  # Move downward
    falling_circles = [c for c in falling_circles if c[1] > 0]

    # Spawn New Falling Circles
    if random.random() < 0.02:
        falling_circles.append([random.randint(20, width - 20), height])

    # Check Missed Circles
    for circle in falling_circles[:]:
        if circle[1] <= 0:
            falling_circles.remove(circle)
            failed_bubbles += 1  # Increase missed bubble count
            if failed_bubbles >= 3:  # Game over if 3 bubbles are missed
                is_game_over = True

    # Check Collisions
    for circle in falling_circles[:]:
        for projectile in projectiles[:]:
            if collision(circle, projectile):
                falling_circles.remove(circle)
                projectiles.remove(projectile)
                score += 1

    # Check for Game Over Condition (Shooter Hit)
    for circle in falling_circles:
        if abs(circle[0] - shooter_x) < 20 and circle[1] < 70:
            is_game_over = True

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


# OpenGL Setup
def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    gluOrtho2D(0, width, 0, height)


# Main Function
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(width, height)
glutCreateWindow(b"Bubble Shooter Game with Rocket Shooter")
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)
glutTimerFunc(16, update, 0)
init()
glutMainLoop()
