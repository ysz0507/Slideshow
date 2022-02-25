import json
import pygame
import os
from PIL import Image

class Picture():
    def __init__(self, url, x = 10, y = 10, width = 200, height = 140, date = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ratio = width/height
        self.url = url
        self.date = date
        if url != "":
            self.refreshMap(url)

    def refreshMap(self, url):
        self.url = url
        dimension = (self.width, self.height)
        largeMap = pygame.image.load(os.path.join(os.getcwd(), "pictures" , self.url)).convert()
        imgRatio = largeMap.get_width() / largeMap.get_height()
        if imgRatio < self.ratio:
            self.img = pygame.transform.smoothscale(largeMap, (int(imgRatio*dimension[1]), dimension[1]))
            self.imgPos = (int((dimension[0] - self.img.get_width())/2), 0)
        elif imgRatio > self.ratio:
            self.img = pygame.transform.smoothscale(largeMap, (dimension[0], int(dimension[0]/imgRatio)))
            self.imgPos = (0, int((dimension[1] - self.img.get_height())/2))
        else:
            self.img = pygame.transform.smoothscale(largeMap, dimension)
            self.imgPos = (0, 0)


    def checkLocation(self, mouseX, mouseY):
        return self.x < mouseX < self.x + self.width and self.y < mouseY < self.y + self.height

    def drawRectangle(self, screen, color):
        if self.date != None:
            pygame.draw.rect(screen, (255, 72, 0), [self.x - 5, self.y - 5, self.width + 6, self.height + 6])
        pygame.draw.rect(screen, color, [self.x, self.y, self.width, self.height])

    def draw(self, screen):
        screen.blit(self.img, (self.imgPos[0] + self.x, self.imgPos[1] + self.y))


class Startbildschirm():

    def __init__(self):
        fullscreen = True
        
        pygame.init()
        clock = pygame.time.Clock()
        font = pygame.font.SysFont('arialnarrow', 20) 

        dimension = (1000,650) 
        if(not fullscreen):
            screen = pygame.display.set_mode(dimension)
        else:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            infoObject = pygame.display.Info()
            dimension = (infoObject.current_w, infoObject.current_h)
        
        tmpScreen = pygame.Surface((dimension[0] + 200, dimension[1] + 200))
        tmpScreen.set_alpha(180)
        
        pygame.display.set_caption("Diashow - Editor")

        splitX = 0.3
        splitY = 0.6
        surSortiert = pygame.Surface((dimension[0] * splitX, dimension[1]))
        surAlle = pygame.Surface((dimension[0] * (1-splitX), dimension[1] * (1-splitY)))
        surPreview = pygame.Surface((dimension[0] * (1-splitX), dimension[1] * splitY))
        preview = Picture("", 0, 0, surPreview.get_width(), surPreview.get_height())

        sorted = []
        with open("order.json", "r") as file:
            data = json.load(file)
            for name in list(data.keys()):
                sorted.append(Picture(name))

        self.placePictures(sorted, surSortiert)

        otherImages = []

        obj = os.scandir("pictures")
        for entry in obj :
            if entry.is_file() and entry.name != ".DS_Store":
                if not entry.name in list(data.keys()):
                    otherImages.append(Picture(entry.name))
        self.placePictures(otherImages, surAlle, surSortiert.get_width(), surPreview.get_height())
        obj.close()
        
        for pic in sorted+otherImages:
            try:
                pic.date = Image.open("pictures/" + pic.url)._getexif().get(306)
            except AttributeError:
                print(pic.url)
            

        #image = Image.open("pictures/A221E0C4-5D6E-4E7A-AD7C-036E0EF6C9F2.jpg")
        image = Image.open("pictures/haha.jpg")
        EXIF_data = image._getexif()
        print(EXIF_data.get(306))

        surSortiert.fill((100, 0, 0))
        surAlle.fill((0, 100, 0))
        surPreview.fill((0, 0, 100))


        hoverColor = (130, 130, 130, 100)

        running = True
        pressed = False
        firstTime = True
        scrollSize = 30
        toScroll = 0
        dragPos = [0, 0]
        while running: 

            mouse = pygame.mouse.get_pos() 

            for ev in pygame.event.get(): 
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                    if ev.key == pygame.K_f:
                        if mouse[0] > surSortiert.get_width():
                            self.placePictures(otherImages, surAlle, surSortiert.get_width(), surPreview.get_height())
                        else:
                            self.placePictures(sorted, surSortiert)
                elif ev.type == pygame.QUIT: 
                    running = False
                elif ev.type == pygame.MOUSEBUTTONDOWN: 
                    if ev.button == 4:
                        toScroll -= 1
                    elif ev.button == 5:
                        toScroll += 1
                    else:
                        pressed = True
                elif ev.type == pygame.MOUSEBUTTONUP: 
                    pressed = False
                    firstTime = True
                    tmpScreen.fill((255, 255, 255, 0))
                    if dragPos != [0, 0]:
                        if mouse[0] < surSortiert.get_width():
                            for i, pic in enumerate(sorted):
                                if pic.checkLocation(mouse[0], mouse[1]):
                                    pos = i
                                    if drawPic in otherImages:
                                        otherImages.remove(drawPic)
                                    else:
                                        sorted.remove(drawPic)
                                    sorted.insert(pos, drawPic)
                                    self.placePictures(sorted, surSortiert)
                        else:
                            if mouse[1] > surPreview.get_height():
                                drawPic.x += dragPos[0]
                                drawPic.y += dragPos[1]
                                if drawPic in sorted:
                                    sorted.remove(drawPic)
                                    otherImages.append(drawPic)
                        dragPos[0] = 0
                        dragPos[1] = 0

            if toScroll != 0:
                if mouse[0] < surSortiert.get_width():
                    for pic in sorted:
                        pic.y -= toScroll * scrollSize
                elif mouse[1] > surPreview.get_height():
                    for pic in otherImages:
                        pic.y -= toScroll * scrollSize
                toScroll = 0

            if pressed:
                for pic in sorted + otherImages:
                    if firstTime:
                        if pic.checkLocation(mouse[0], mouse[1]):
                            firstTime = False
                            preview.refreshMap(pic.url)
                            surPreview.fill((0, 0, 0))
                            preview.draw(surPreview)

                            text = font.render(preview.url, False, (0, 0, 0))
                            textRect = text.get_rect()
                            textRect.midtop = (preview.x + preview.width/2, preview.y) 
                            pygame.draw.rect(surPreview, (255, 255, 255), textRect)
                            surPreview.blit(text, textRect)
                            print(pic.date)
                            if pic.date != None:
                                text = font.render(pic.date, False, (0, 0, 0))
                                textRect = text.get_rect()
                                textRect.midbottom = (preview.x + preview.width/2, preview.y + preview.height) 
                                pygame.draw.rect(surPreview, (255, 255, 255), textRect)
                                surPreview.blit(text, textRect)
                            
                            dragStart = mouse
                            drawPic = pic
                    else:
                        dragPos[0] = mouse[0] - dragStart[0]
                        dragPos[1] = mouse[1] - dragStart[1]
                        tmpScreen.fill((255, 255, 255, 0))
                        drawPic.draw(tmpScreen)

            screen.fill((0, 0, 0)) 


            screen.blit(surSortiert, (0, 0))
            screen.blit(surAlle, (surSortiert.get_width(), surPreview.get_height()))

            for pic in sorted:
                pic.drawRectangle(screen, hoverColor)
                pic.draw(screen)

            for pic in otherImages:
                pic.drawRectangle(screen, hoverColor)
                pic.draw(screen)

            screen.blit(surPreview, (surSortiert.get_width(), 0))
            screen.blit(tmpScreen, dragPos)

            pygame.display.update()             
            clock.tick(40)

        pygame.quit()
    
    def placePictures(self, pictures, surface, shiftX = 0, shiftY = 0, padding = 10):
        extreme = [padding, padding]
        i = 0
        while i < len(pictures):
            if extreme[0] + pictures[i].width < surface.get_width():
                pictures[i].x = extreme[0] + shiftX
                pictures[i].y = extreme[1] + shiftY
                extreme[0] += padding + pictures[i].width
                i += 1
            else:
                extreme[0] = padding
                extreme[1] += pictures[i].height + padding            

            


if __name__ == '__main__':
    start = Startbildschirm()