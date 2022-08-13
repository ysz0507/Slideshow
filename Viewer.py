import json
import os
import pygame
import time

from Editor import Startbildschirm

class Button():
    def __init__(self, x = 10, y = 10, width = 100, height = 50, name = "", center=False):
        self.width = width
        self.height = height
        self.y = y
        if not center:
            self.x = x
        else:
            self.x = x - width/2
        if name != "":
            self.name = name

    def checkLocation(self, mouseX, mouseY):
        return self.x < mouseX < self.x + self.width and self.y < mouseY < self.y + self.height

    def drawRectangle(self, screen, color):
        pygame.draw.rect(screen, color, [self.x, self.y, self.width, self.height])

    def drawText(self, screen, font):
        text = font.render(self.name, False, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (self.x + self.width/2, self.y + self.height/2) 
        screen.blit(text, textRect)


class Viewer():

    def __init__(self, duration = 5):
        fullscreen = True
        automatisch = not (duration == 0)
        intervall = duration
        dock = 10
        acceleration = 1

        with open("order.json", "r") as file:
            maps = list(json.load(file).get("order"))
        
        pygame.init()
        pygame.mouse.set_visible(False)
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
        
        pygame.display.set_caption("Slideshow")

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
                surAnimation.blit(currentMap, (imgPos[0] + int(animation), imgPos[1]))
                speed = 0.1
            
            if speed > 0 and animation > dock:
                if(animation >= screen.get_width() * 0.5):
                    speed += acceleration
                elif(animation < screen.get_width() * 0.5):
                    speed -= acceleration
                
                animation -= speed
            elif animation != 0:
                animation = 0.0
                speed = 0.0
            
            screen.fill((0, 0, 0))
            screen.blit(surAnimation.subsurface(screen.get_width() - int(animation), 0, screen.get_width(), screen.get_height()), (0, 0))

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


class Startmenu:
    def __init__(self):
        pygame.init()

        self.GRAY = (156, 156, 156)
        clock = pygame.time.Clock()

        self.dimension = (1000,650) 
        self.screen = pygame.display.set_mode(self.dimension)
        self.screen.fill((255, 255, 255))
        font = pygame.font.SysFont('arialnarrow', 40) 
        pygame.display.set_caption("Slideshow")

        self.surText = pygame.Surface(self.dimension)
        duration = 8
        self.reloadTextSurface(font, str(duration))

        NORMAL_COLOR = (220, 220, 220)
        HOVER_COLOR = (190, 190, 190)
        PRESSED_COLOR = (100, 100, 100)

        running = True
        pressed = False
        while running:
            mouse = pygame.mouse.get_pos()
            for ev in pygame.event.get(): 
                if ev.type == pygame.QUIT: 
                    running = False
                elif ev.type == pygame.MOUSEBUTTONUP: 
                    pressed = False
                    for button in self.buttons:
                        if button.checkLocation(mouse[0], mouse[1]):
                            if button.name == "How to use":
                                self.loadInstructions(font)
                            elif button.name == "Next":
                                self.surText.fill(self.GRAY)
                                large = pygame.image.load(os.path.join(os.getcwd(), "example.png")).convert()
                                self.surText.blit(pygame.transform.smoothscale(large, self.dimension), (0, 0))
                                button.name = "Back"
                            elif button.name == "Back":
                                self.reloadTextSurface(font, str(duration))
                            elif button.name == "Edit / Create":
                                start = Startbildschirm()
                                start.mainloop()
                                self.screen = pygame.display.set_mode(self.dimension)
                                pygame.display.set_caption("Slideshow")
                            elif button.name == "Start Slideshow":
                                Viewer(duration)
                                self.screen = pygame.display.set_mode(self.dimension)
                                pygame.mouse.set_visible(True)
                            else:
                                print(button.name)
                elif ev.type == pygame.MOUSEBUTTONDOWN: 
                    pressed = True
                elif ev.type == pygame.KEYDOWN: 
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                    elif ev.key in (pygame.K_PLUS, pygame.K_UP, pygame.K_RIGHT):
                        duration += 1
                        duration %= 45 
                        self.reloadTextSurface(font, str(duration))
                    elif ev.key in (pygame.K_MINUS, pygame.K_DOWN, pygame.K_LEFT):
                        duration -= 1 
                        duration %= 45
                        self.reloadTextSurface(font, str(duration))

            self.screen.blit(self.surText, (0, 0))

            for button in self.buttons:
                if not button.checkLocation(mouse[0], mouse[1]):
                    button.drawRectangle(self.screen, NORMAL_COLOR)
                else:
                    if pressed:
                        button.drawRectangle(self.screen, PRESSED_COLOR)
                    else:
                        button.drawRectangle(self.screen, HOVER_COLOR)

                button.drawText(self.screen, font)


            pygame.display.update()
            clock.tick(40)

        pygame.quit()

    def writeText(self, textList, font, y=4):
        dy = 0
        i = 0
        textList.append("end")
        while i < len(textList) - 1:
            sur = font.render(textList[i], False, (0, 0, 0))
            textRect = sur.get_rect()
            textRect.midtop = (self.screen.get_width()/2, y + dy) 
            self.surText.blit(sur, textRect)
            dy += sur.get_height()
            i += 1
        return dy

    def reloadTextSurface(self, font, duration):
        self.surText.fill(self.GRAY)
        self.buttons = []

        if(duration == "0"):
            duration = "infinite"
        
        dy = 50
        dy += self.writeText(["Before you start: Read the controls and instructions carefully!"], font, dy) + 10
        self.buttons.append(Button(name = "How to use", x=self.dimension[0]/2, y = dy, width= 200, height=80, center=True))
        dy += 80 + 20
        dy += self.writeText(["Than create and edit your slideshow with this button:", "(Tip: Do not forget to save with s)"], font, dy) + 10
        self.buttons.append(Button(name = "Edit / Create", x=self.dimension[0]/2, y = dy, width= 200, height=80, center=True))
        dy += 80 + 20
        dy += self.writeText(["Finally start your slideshow with " + duration + " seconds per image", "(Change amount of seconds with + or - on your keyboard)"], font, dy) + 10
        self.buttons.append(Button(name = "Start Slideshow", x=self.dimension[0]/2, y=dy, width= 300, height=80, center=True))

    def loadInstructions(self, font):
        self.surText.fill(self.GRAY)
        self.buttons = []

        control = []
        control.append("Use arrows for navigation")
        control.append("Drag image to sort manually")
        dy = 30
        dy += self.writeText(control, font, dy) + 40

        control = []
        control.append("F - Format and jump to start")
        control.append("S - Save current order")
        control.append("- and + for de-/increasing size of image")
        dy += self.writeText(control, font, dy) + 40

        control = []
        control.append("Hold key to change mode of your click:")
        control.append("D - Delete the clicked image")
        control.append("I - Insert into the ordered images, if the shooting date is available")
        dy += self.writeText(control, font, dy) + 40

        self.buttons.append(Button(name = "Next", x=self.dimension[0]/2, y=dy, width= 300, height=80, center=True))
        

if __name__ == '__main__':
    Startmenu()