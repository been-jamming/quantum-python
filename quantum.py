import pygame
import math
import cmath

screen_resolution = (640*2, 480*2)
resolution = 100

time_step = 0.025/60
ticks_per_frame = 40
total_captured = 0.0
capture_rate = 1.0
pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode(screen_resolution)

def get_color(value):
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
    return [int(max(x*255, 0.0)) for x in (red, green, blue)]

def render(state):
    max_abs = 0.5
    #for n in range(resolution):
    #    if abs(state[n]) >= max_abs:
    #        max_abs = abs(state[n])
    prev_x = 0
    for n in range(resolution):
        color = get_color(state[n])
        x = int((n + 1.0)*screen_resolution[0]/resolution)
        y = int((1.0 - abs(state[n])/max_abs)*screen_resolution[1])
        pygame.draw.rect(window, color, (prev_x, y, x - prev_x, screen_resolution[1] - y))
        prev_x = x

def norm_state(state):
    norm_squared = 0
    for n in range(resolution):
        norm_squared += abs(state[n])**2.0
    norm = math.sqrt(norm_squared)
    return norm

def normalize_state(state, captured):
    norm = norm_state(state)

    for n in range(resolution):
        state[n] /= norm/(1.0 - captured)

    return state

def get_second_derivative(state, x):
    if x == 0:
        a = 0
    else:
        a = state[(x - 1)%resolution]
    b = state[x]
    if x == resolution - 1:
        c = 0
    else:
        c = state[(x + 1)%resolution]

    result = c - 2.0*b + a
    return result

state = [cmath.exp(complex(0.0, -n*15.0*2.0*math.pi/resolution))/(math.exp(((n - resolution/2.0)/5.0)**2.0)) for n in range(resolution)]
state = normalize_state(state, 0.0)

def simulate(state, dt):
    next_state = [0 for n in range(resolution)]
    for x in range(resolution):
        second_derivative = get_second_derivative(state, x)
        next_state[x] = state[x] + complex(0, -1)*second_derivative*dt
    next_norm = abs(next_state[2]) + 1.0*abs(next_state[1])
    next_phase = cmath.phase(next_state[1]) - 2.0*cmath.phase(next_state[2])
    #next_state[0] = next_norm*cmath.exp(complex(0.0, next_phase))
    return next_state

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
    window.fill((0, 0, 0))
    render(state)
    pygame.display.update()
    dt = clock.tick(60)
    captured = total_captured
    for i in range(ticks_per_frame):
        state = simulate(state, time_step*dt)
        state = normalize_state(state, captured)
    total_captured += capture_rate*ticks_per_frame*float(dt)/1000.0*abs(state[0])**2
    print(total_captured)

pygame.quit()

