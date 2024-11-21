import pygame
import math
import cmath

screen_resolution = (640*2, 640*2)
resolution = 50

time_step = 0.00125
ticks_per_frame = 4
total_captured = 0.0
capture_rate = 1.0
pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode(screen_resolution)

state = [[cmath.exp(complex(0.0, -(x*0.581 + 2.21*y)*2.5*2.0*math.pi/resolution))/(math.exp(((x - resolution/2.0)/5.0)**2 + ((y - resolution/2.0)/5.0)**2)) for y in range(resolution)] for x in range(resolution)]

norm_squared = 0.0
for x in range(resolution):
    for y in range(resolution):
        norm_squared += state[x][y].real*state[x][y].real + state[x][y].imag*state[x][y].imag
norm = math.sqrt(norm_squared)

state_real = [[state[x][y].real/norm for y in range(resolution)] for x in range(resolution)]
state_imag = [[state[x][y].imag/norm for y in range(resolution)] for x in range(resolution)]

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

def render(state_real, state_imag):
    max_val = 0.0
    for n in range(resolution):
        for m in range(resolution):
            max_val = max(max_val, abs(complex(state_real[n][m], state_imag[n][m])))

    prev_x = 0
    for n in range(resolution):
        prev_y = 0
        for m in range(resolution):
            color = get_color(complex(state_real[n][m], state_imag[n][m]), max_val)
            x = int((n + 1.0)*screen_resolution[0]/resolution)
            y = int((m + 1.0)*screen_resolution[1]/resolution)
            pygame.draw.rect(window, color, (prev_x, prev_y, x - prev_x, y - prev_y))
            prev_y = y
        prev_x = x

def get_second_derivative(vector, x, y):
    if x == 0:
        x0 = 0.0
    else:
        x0 = vector[x - 1][y]
    x1 = vector[x][y]
    if x == resolution - 1:
        x2 = 0.0
    else:
        x2 = vector[x + 1][y]

    if y == 0:
        y0 = 0.0
    else:
        y0 = vector[x][y - 1]
    y1 = vector[x][y]
    if y == resolution - 1:
        y2 = 0.0
    else:
        y2 = vector[x][y + 1]

    return (x0 - 2.0*x1 + x2, y0 - 2.0*y1 + y2)

def get_total_prob(next_state_real, next_state_imag, state_imag):
    total = 0.0
    for x in range(resolution):
        for y in range(resolution):
            val = next_state_real[x][y]*next_state_real[x][y] + next_state_imag[x][y]*state_imag[x][y]
            total += val
    return total

def simulate(state_real, state_imag, dt):
    next_state_real = [[0 for y in range(resolution)] for x in range(resolution)]
    next_state_imag = [[0 for y in range(resolution)] for x in range(resolution)]

    for x in range(resolution):
        for y in range(resolution):
            second_derivative_imag = get_second_derivative(state_imag, x, y)
            next_state_real[x][y] = state_real[x][y] + second_derivative_imag[0]*dt + second_derivative_imag[1]*dt
    for x in range(resolution):
        for y in range(resolution):
            second_derivative_real = get_second_derivative(next_state_real, x, y)
            next_state_imag[x][y] = state_imag[x][y] - second_derivative_real[0]*dt - second_derivative_real[1]*dt
    total_prob = get_total_prob(next_state_real, next_state_imag, state_imag)
    norm = math.sqrt(total_prob)

    for x in range(resolution):
        for y in range(resolution):
            next_state_real[x][y] /= norm
            next_state_imag[x][y] /= norm
            pass

    return next_state_real, next_state_imag

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
    window.fill((0, 0, 0))
    render(state_real, state_imag)
    pygame.display.update()
    dt = clock.tick(60)
    captured = total_captured
    for i in range(ticks_per_frame):
        state_real, state_imag = simulate(state_real, state_imag, time_step*dt)

pygame.quit()

