import pygame
import sys

pygame.init()

box_width, box_height = 1280, 720 
black = (0, 0, 0)   
aqua = (0, 255, 255)         
fps = 120                 

screen = pygame.display.set_mode((box_width, box_height))

particle_pos = [640, 360] 
particle_vel = [1, 1]      
gravity = 9.8

RADIUS = 10


clock = pygame.time.Clock()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    particle_pos[0] = particle_vel[0] + particle_pos[0] + gravity
    particle_pos[1] = particle_vel[1] + particle_pos[1] + gravity

    if particle_pos[0] - RADIUS <= 0 or particle_pos[0] + RADIUS >= box_width:
        particle_vel[0] =- particle_vel[0]  
    
    if particle_pos[1] - RADIUS <= 0 or particle_pos[1] + RADIUS >= box_height:
        particle_vel[1] =- particle_vel[1]  

    screen.fill(black)

    pygame.draw.circle(screen, aqua, particle_pos, RADIUS)
    pygame.display.flip()

    clock.tick(fps)
