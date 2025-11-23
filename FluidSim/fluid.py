import pygame
import sys

pygame.init()

#topleft is 0,0
box_width, box_height = 1280, 720 
black = (0, 0, 0)   
aqua = (0, 255, 255)         
fps = 120                 

screen = pygame.display.set_mode((box_width, box_height))

xpos = 640
ypos = 360
xvel = -4
yvel = 5

gravity = 0.5
dampingRate = 0.9

radius = 10

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    yvel += gravity

    xpos += xvel 
    ypos += yvel 

    if ypos + radius >= box_height: #floor
        ypos = box_height - radius
        yvel = -yvel * dampingRate
    
    if ypos - radius <= 0: #roof
        ypos = radius
        yvel = -yvel * dampingRate
    if xpos + radius >= box_width: #right wall
        xpos = box_width - radius
        xvel = -xvel * dampingRate

    if xpos - radius <= 0: #left wall
        xpos = radius
        xvel = -xvel * dampingRate

    screen.fill(black)

    pygame.draw.circle(screen, aqua, (int(xpos), int(ypos)), radius)
    pygame.display.flip()

    clock.tick(fps)
