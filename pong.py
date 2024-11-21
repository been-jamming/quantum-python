import pygame
import math
import cmath

screen_resolution = (640*2, 640*2)
resolution = 50

time_step = 0.0025/60
ticks_per_frame = 40
total_captured = 0.0
capture_rate = 1.0
pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode(screen_resolution)

def get_color(value, max_val):
    norm, phase = cmath.polar(value)
    phase = math.fmod(phase + math.pi, 2.0*math.pi)
    if phase <= math.pi/3.0 or phase >= 5.0*math.pi/3.0:
        red = 1.0
        if phase <= math.pi/3.0:
            green = phase*3.0/math.pi
            blue = 0.0
        else:
            green = 0.0
            blue = 1.0 - (phase - 5.0*math.pi/3.0)*3.0/math.pi
    elif phase >= math.pi/3.0 and phase <= math.pi:
        green = 1.0
        if phase <= 2.0*math.pi/3.0:
            red = (2.0*math.pi/3.0 - phase)*3.0/math.pi
            blue = 0.0
        else:
            red = 0.0
            blue = 1.0 - (math.pi - phase)*3.0/math.pi
    else:
        blue = 1.0
        if phase <= 4.0*math.pi/3.0:
            red = 0.0
            green = (4.0*math.pi/3.0 - phase)*3.0/math.pi
        else:
            red = 1.0 - (5.0*math.pi/3.0 - phase)*3.0/math.pi
            green = 0.0
    return [int(max(x*norm*norm/(max_val*max_val)*255.0, 0.0)) for x in (red, green, blue)]

def render(state, max_val):
    max_abs = 0.5
    #for n in range(resolution):
    #    if abs(state[n]) >= max_abs:
    #        max_abs = abs(state[n])
    prev_x = 0
    for n in range(resolution):
        prev_y = 0
        for m in range(resolution):
            color = get_color(state[n][m], max_val)
            x = int((n + 1.0)*screen_resolution[0]/resolution)
            y = int((m + 1.0)*screen_resolution[1]/resolution)
            pygame.draw.rect(window, color, (prev_x, prev_y, x - prev_x, y - prev_y))
            prev_y = y
        prev_x = x

def norm_state(state):
    norm_squared = 0
    for x in range(resolution):
        for y in range(resolution):
            norm_squared += abs(state[x][y])**2.0
    norm = math.sqrt(norm_squared)
    return norm

def normalize_state(state, captured):
    max_val = 0.0
    norm = norm_state(state)

    for x in range(resolution):
        for y in range(resolution):
            max_val = max(abs(state[x][y]), max_val)
            state[x][y] /= norm/(1.0 - captured)

    return state, max_val

def get_second_derivative(state, x, y):
    if x == 0:
        x0 = 0
    else:
        x0 = state[(x - 1)%resolution][y]
    if x == resolution - 1:
        x1 = 0
    else:
        x1 = state[(x + 1)%resolution][y]

    if y == 0:
        y0 = 0
    else:
        y0 = state[x][(y - 1)%resolution]
    if y == resolution - 1:
        y1 = 0
    else:
        y1 = state[x][(y + 1)%resolution]

    result = (x1 - 2.0*state[x][y] + x0, y1 - 2.0*state[x][y] + y0)
    return result

state = [[cmath.exp(complex(0.0, -(x*0.581 + 4.21*y)*2.5*2.0*math.pi/resolution))/(math.exp(((x - resolution/2.0)/5.0)**2 + ((y - resolution/2.0)/5.0)**2)) for y in range(resolution)] for x in range(resolution)]
#state = [cmath.exp(complex(0.0, -n*15.0*2.0*math.pi/resolution))/(math.exp(((n - resolution/2.0)/5.0)**2.0)) for n in range(resolution)]
state, _ = normalize_state(state, 0.0)

def simulate(state, dt):
    next_state = [[0 for y in range(resolution)] for x in range(resolution)]
    for x in range(resolution):
         for y in range(resolution):
            second_derivative = get_second_derivative(state, x, y)
            next_state[x][y] = state[x][y] + complex(0, -1)*(second_derivative[0] + second_derivative[1])*dt
    return next_state

running = True
max_val = 1.0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
    window.fill((0, 0, 0))
    render(state, max_val)
    pygame.display.update()
    dt = clock.tick(60)
    captured = total_captured
    for i in range(ticks_per_frame):
        state = simulate(state, time_step*dt)
        state, max_val = normalize_state(state, captured)

pygame.quit()

