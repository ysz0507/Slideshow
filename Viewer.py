import json
import os
import pygame
import time

class Button():
    def __init__(self, x = 10, y = 10, width = 100, height = 50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def checkLocation(self, mouseX, mouseY):
        return self.x < mouseX < self.x + self.width and self.y < mouseY < self.y + self.height

    def drawRectangle(self, screen, color):
        pygame.draw.rect(screen, color, [self.x, self.y, self.width, self.height])


class Startbildschirm():

    def __init__(self):
        fullscreen = True
        automatisch = True
        intervall = 5
        animationSpeed = 23
        acceleration = 0.5

        with open("order.json", "r") as file:
            maps = list(json.load(file).get("order"))
        
        pygame.init()
        pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
        clock = pygame.time.Clock()

        dimension = (1000,650) 
        if(not fullscreen):
            screen = pygame.display.set_mode(dimension)
        else:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            infoObject = pygame.display.Info()
            dimension = (infoObject.current_w, infoObject.current_h)
        screenRatio = dimension[0] / dimension[1]
        tmpScreen = pygame.Surface(dimension)
        tmpScreen.set_alpha(125)
        
        pygame.display.set_caption("Diashow")

        split = 0.3
        links = Button(0, 0, dimension[0] * split, dimension[1])
        rechts = Button(dimension[0] * split, 0, dimension[0] * (1-split), dimension[1])

        hoverColor = (130, 130, 130, 100)
        links.drawRectangle(tmpScreen, hoverColor)

        selected = 0
        displayed = -1

        running = True
        pressed = False
        firstTime = True
        
        imgPos = (0, 0)

        last = int(time.time())
        surAnimation = pygame.Surface((dimension[0] * 2, dimension[1]))
        currentMap = pygame.Surface(dimension)

        while running: 
            for ev in pygame.event.get(): 
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                    if ev.key == pygame.K_LEFT:
                        selected -= 1
                    if ev.key == pygame.K_RIGHT:
                        selected += 1
                if ev.type == pygame.QUIT: 
                    running = False
                if ev.type == pygame.MOUSEBUTTONDOWN: 
                    pressed = True
                if ev.type == pygame.MOUSEBUTTONUP: 
                    pressed = False
                    firstTime = True
                
            if automatisch and int(time.time()) - last > intervall:
                selected += 1
                last = int(time.time())

            if selected != displayed:
                selected %= len(maps) + 1
                displayed = selected
                animation = screen.get_width()
                surAnimation.fill((0, 0, 0))
                surAnimation.blit(currentMap, imgPos)

                if(selected != len(maps)):
                    largeMap = pygame.image.load(os.path.join(os.getcwd(), "pictures" , maps[selected])).convert()
                    imgRatio = largeMap.get_width() / largeMap.get_height()
                    if imgRatio < screenRatio:
                        currentMap = pygame.transform.smoothscale(largeMap, (int(imgRatio*dimension[1]), dimension[1]))
                        imgPos = (int((dimension[0] - currentMap.get_width())/2), 0)
                    elif imgRatio > screenRatio:
                        currentMap = pygame.transform.smoothscale(largeMap, (dimension[0], int(dimension[0]/imgRatio)))
                        imgPos = (0, int((dimension[1] - currentMap.get_height())/2))
                    else:
                        currentMap = pygame.transform.smoothscale(largeMap, dimension)
                        imgPos = (0, 0)
                    
                else:
                    currentMap.fill((0, 0, 0))
                    imgPos = (0, 0)
                surAnimation.blit(currentMap, (imgPos[0] + animation, imgPos[1]))
                speed = animationSpeed
            
            if animation >= animationSpeed:
                #speed = 1 - abs(animation-screen.get_width()*0.5) / (screen.get_width()*0.5)
                #speed *= 4
                #speed = speed**2
                animation -= animationSpeed
            elif animation != 0:
                animation = 0
            
            screen.fill((0, 0, 0))
            screen.blit(surAnimation.subsurface(screen.get_width() - animation, 0, screen.get_width(), screen.get_height()), (0, 0))

            mouse = pygame.mouse.get_pos() 

            if links.checkLocation(*mouse): 
                if pressed:
                    if firstTime:
                        firstTime = False
                        selected -= 1
                else:
                    screen.blit(tmpScreen, (0, 0))

            if rechts.checkLocation(*mouse): 
                if pressed:
                    if firstTime:
                        firstTime = False
                        selected += 1

            
            pygame.display.update() 
            clock.tick(40)

        pygame.quit() 

    


if __name__ == '__main__':
    start = Startbildschirm()