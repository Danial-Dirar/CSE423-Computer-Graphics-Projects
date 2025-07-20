import math
import random
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from bluetooth import discover_devices, lookup_name

# Radar parameters
window_size = 800
radius = 300
refresh_rate = 2  # seconds

# Detected devices
devices = []

def midpoint_circle(x_center, y_center, r):
    x = 0
    y = r
    d = 1 - r
    circle_points = []

    while x <= y:
        circle_points.extend([
            (x_center + x, y_center + y), (x_center - x, y_center + y),
            (x_center + x, y_center - y), (x_center - x, y_center - y),
            (x_center + y, y_center + x), (x_center - y, y_center + x),
            (x_center + y, y_center - x), (x_center - y, y_center - x)
        ])
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1

    return circle_points

def midpoint_line(x1, y1, x2, y2):
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

    return points

def draw_circle():
    for r in range(50, radius + 1, 50):
        points = midpoint_circle(0, 0, r)
        glBegin(GL_POINTS)
        for x, y in points:
            glVertex2i(x, y)
        glEnd()

def draw_lines():
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x = int(radius * math.cos(rad))
        y = int(radius * math.sin(rad))
        points = midpoint_line(0, 0, x, y)
        glBegin(GL_POINTS)
        for px, py in points:
            glVertex2i(px, py)
        glEnd()

def detect_devices():
    global devices
    devices = []
    nearby_devices = discover_devices(duration=4, lookup_names=True, lookup_class=False)
    for addr, name in nearby_devices:
        signal_strength = random.randint(1, 100)  # Mock signal strength
        devices.append((name, signal_strength))
    devices.sort(key=lambda x: x[1], reverse=True)

def draw_devices():
    if not devices:
        return

    for idx, (name, strength) in enumerate(devices):
        distance = int((1 - strength / 100) * radius)
        angle = random.uniform(0, 2 * math.pi)  # Random angle for display
        x = int(distance * math.cos(angle))
        y = int(distance * math.sin(angle))

        # Draw point
        glPointSize(5)
        glBegin(GL_POINTS)
        glVertex2i(x, y)
        glEnd()

        # Draw text
        glRasterPos2i(x + 10, y + 10)
        for ch in f"{name[:8]} ({strength}%)":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glPushMatrix()

    # Draw radar
    glColor3f(0.0, 1.0, 0.0)
    draw_circle()
    draw_lines()

    # Draw devices
    glColor3f(1.0, 0.0, 0.0)
    draw_devices()

    glPopMatrix()
    glutSwapBuffers()

def update(value):
    detect_devices()
    glutPostRedisplay()
    glutTimerFunc(int(refresh_rate * 1000), update, 0)

def setup():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-window_size // 2, window_size // 2, -window_size // 2, window_size // 2)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(window_size, window_size)
    glutCreateWindow(b"Live Bluetooth Radar")
    setup()
    glutDisplayFunc(display)
    glutTimerFunc(0, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()