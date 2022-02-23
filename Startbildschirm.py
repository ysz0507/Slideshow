import json
import os
import pygame

class Button():
    def __init__(self, x = 10, y = 10, width = 100, height = 50, name="", font=120):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        if name != "":
            smallfont = pygame.font.SysFont('Corbel', font) 
            self.text = smallfont.render(name , True, (255, 255, 255)) 
        else:
            self.text = None

    def checkLocation(self, mouseX, mouseY):
        return self.x < mouseX < self.x + self.width and self.y < mouseY < self.y + self.height

    def drawSurface(self, screen, surface):
        if surface == None:
            return
        xOffset = (self.width - surface.get_width()) / 2
        yOffset = (self.height - surface.get_height()) / 2
        screen.blit(surface, (self.x + xOffset, self.y + yOffset))

    def drawRectangle(self, screen, color):
        pygame.draw.rect(screen, color, [self.x, self.y, self.width, self.height])

    def drawText(self, screen):
        self.drawSurface(screen, self.text)


class Startbildschirm():

    def __init__(self):
        with open("order.json", "r") as file:
            maps = list(json.load(file).keys())

        pygame.init()
        clock = pygame.time.Clock()

        dimension = (1000,650) 
        screen = pygame.display.set_mode(dimension)
        pygame.display.set_caption("Race")

        smallfont = pygame.font.SysFont('Corbel', 200) 
        text = smallfont.render('Race Game' , True, (255, 255, 255)) 

        play = Button(350, 300, 300, 200, "")
        links = Button(150, 270, 200, 220, "<", 500)
        rechts = Button(650, 270, 200, 220, ">", 500)

        hoverColor = (30, 129, 176)
        pressColor = (21,76,121)
        normalColor = (37, 150, 190)

        selected = 0
        displayed = -1

        running = True
        pressed = False
        firstTime = True
        
        while running: 
            screen.fill((157, 177, 187)) 
            screen.blit(text, ((dimension[0] - text.get_width())/2, (dimension[1] - text.get_height())/4))
            links.drawText(screen)
            rechts.drawText(screen)

            if selected != displayed:
                selected %= len(maps)
                displayed = selected
                largeMap = pygame.image.load(os.path.join(os.getcwd(), "pictures" , maps[selected])).convert()
                currentMap = pygame.transform.smoothscale(largeMap, (270, 170))

            mouse = pygame.mouse.get_pos() 
            
            if play.checkLocation(*mouse): 
                if pressed:
                    play.drawRectangle(screen, pressColor)
                    if firstTime:
                        firstTime = False
                        print("hallo")
                        continue
                else:
                    play.drawRectangle(screen, hoverColor)
            else:
                play.drawRectangle(screen, normalColor)
            play.drawText(screen)

            screen.blit(currentMap, (365, 315))

            if links.checkLocation(*mouse): 
                if pressed and firstTime:
                    firstTime = False
                    selected -= 1
            links.drawText(screen)

            if rechts.checkLocation(*mouse): 
                if pressed and firstTime:
                    firstTime = False
                    selected += 1
            rechts.drawText(screen)

            
            pygame.display.update() 

            for ev in pygame.event.get(): 
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                if ev.type == pygame.QUIT: 
                    running = False
                if ev.type == pygame.MOUSEBUTTONDOWN: 
                    pressed = True
                if ev.type == pygame.MOUSEBUTTONUP: 
                    pressed = False
                    firstTime = True
            
            
            clock.tick(40)

        pygame.quit() 

    


if __name__ == '__main__':
    start = Startbildschirm()