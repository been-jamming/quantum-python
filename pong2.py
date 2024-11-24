import pygame
import math
import cmath

resolution_x = 80
resolution_y = 50
screen_resolution = (resolution_x*14, resolution_y*14)

time_step = 0.0025
ticks_per_frame = 2
pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode(screen_resolution)
barrier_end = 20

state = [[cmath.exp(complex(0.0, (x*4.21 + 2.21*y)*2.5*2.0*math.pi)/50.0)/(math.exp(((x - resolution_x/2.0)/5.0)**2 + ((y - resolution_y/2.0)/5.0)**2)) for y in range(resolution_y)] for x in range(resolution_x)]

norm_squared = 0.0
for x in range(resolution_x):
    for y in range(resolution_y):
        norm_squared += state[x][y].real*state[x][y].real + state[x][y].imag*state[x][y].imag
norm = math.sqrt(norm_squared)

state_real = [[state[x][y].real/norm for y in range(resolution_y)] for x in range(resolution_x)]
state_imag = [[state[x][y].imag/norm for y in range(resolution_y)] for x in range(resolution_x)]

def get_potential(x, y, state_real, state_imag):
    return 0.0

def get_barrier_momentum(y, state_real, state_imag):
    z0 = complex(state_real[barrier_end - 1][y], state_imag[barrier_end - 1][y])
    z1 = complex(state_real[barrier_end][y], state_imag[barrier_end][y])
    z2 = complex(state_real[barrier_end + 1][y], state_imag[barrier_end + 1][y])
    
    #w0 = complex(state_real[barrier_end - 3][y], state_imag[barrier_end - 3][y])
    #w1 = complex(state_real[barrier_end - 2][y], state_imag[barrier_end - 2][y])
    #w2 = complex(state_real[barrier_end - 1][y], state_imag[barrier_end - 1][y])

    momentum0 = (complex(0, -1)*(z2 - z0).conjugate()*z1).real
    #momentum1 = (complex(0, -1)*(w2 - w0).conjugate()*w1).real

    #return momentum0 + momentum1
    return momentum0

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
    for n in range(resolution_x):
        for m in range(resolution_y):
            max_val = max(max_val, abs(complex(state_real[n][m], state_imag[n][m])))

    prev_x = 0
    for n in range(resolution_x):
        prev_y = 0
        for m in range(resolution_y):
            color = get_color(complex(state_real[n][m], state_imag[n][m]), max_val)
            x = int((n + 1.0)*screen_resolution[0]/resolution_x)
            y = int((m + 1.0)*screen_resolution[1]/resolution_y)
            pygame.draw.rect(window, color, (prev_x, prev_y, x - prev_x, y - prev_y))
            prev_y = y
        prev_x = x

def get_second_derivative(vector, x, y, state_real, state_imag):
    if x == barrier_end:
        momentum = get_barrier_momentum(y, state_real, state_imag)
        if momentum > 0:
            x0 = 0.0
        else:
            x0 = vector[x - 1][y]
    elif x == 0:
        x0 = 0.0
    else:
        x0 = vector[x - 1][y]
    x1 = vector[x][y]
    if x == barrier_end - 1:
        momentum = get_barrier_momentum(y, state_real, state_imag)
        if momentum > 0:
            x2 = 0.0
        else:
            x2 = vector[x + 1][y]
    elif x == resolution_x - 1:
        x2 = 0.0
    else:
        x2 = vector[x + 1][y]

    if y == 0:
        y0 = 0.0
    else:
        y0 = vector[x][y - 1]
    y1 = vector[x][y]
    if y == resolution_y - 1:
        y2 = 0.0
    else:
        y2 = vector[x][y + 1]

    return (x0 - 2.0*x1 + x2, y0 - 2.0*y1 + y2)

def get_total_prob(next_state_real, next_state_imag, state_imag):
    total = 0.0
    for x in range(resolution_x):
        for y in range(resolution_y):
            val = next_state_real[x][y]*next_state_real[x][y] + next_state_imag[x][y]*state_imag[x][y]
            total += val
    return total

def simulate(state_real, state_imag, dt):
    next_state_real = [[0 for y in range(resolution_y)] for x in range(resolution_x)]
    next_state_imag = [[0 for y in range(resolution_y)] for x in range(resolution_x)]

    for x in range(resolution_x):
        for y in range(resolution_y):
            potential = get_potential(x, y, state_real, state_imag)
            second_derivative_imag = get_second_derivative(state_imag, x, y, state_real, state_imag)
            next_state_real[x][y] = state_real[x][y] + second_derivative_imag[0]*dt + second_derivative_imag[1]*dt + potential*state_imag[x][y]*dt
    for x in range(resolution_x):
        for y in range(resolution_y):
            potential = get_potential(x, y, state_real, state_imag)
            second_derivative_real = get_second_derivative(next_state_real, x, y, state_real, state_imag)
            next_state_imag[x][y] = state_imag[x][y] - second_derivative_real[0]*dt - second_derivative_real[1]*dt - potential*next_state_real[x][y]*dt
    total_prob = get_total_prob(next_state_real, next_state_imag, state_imag)
    norm = math.sqrt(total_prob)

    for x in range(resolution_x):
        for y in range(resolution_y):
            next_state_real[x][y] /= norm
            next_state_imag[x][y] /= norm

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
    for i in range(ticks_per_frame):
        state_real, state_imag = simulate(state_real, state_imag, time_step*dt)

pygame.quit()

