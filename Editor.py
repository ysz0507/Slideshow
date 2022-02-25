
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
            self.refreshMap()

    def refreshMap(self):
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
            pygame.draw.rect(screen, (255, 255, 255), [self.x - 5, self.y - 5, self.width + 6, self.height + 6])
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
        try:
            with open("order.json", "r") as file:
                data = json.load(file)
                for name in list(data.keys()):
                    sorted.append(Picture(name))
        except FileNotFoundError:
            data = {}
            print("No File imported")

        self.placePictures(sorted, surSortiert)

        otherImages = []

        obj = os.scandir("pictures")
        for entry in obj :
            if entry.is_file() and entry.name != ".DS_Store" and entry.name[-4:] in (".png", ".jpg", ".tif", ".gif"):
                if not entry.name in list(data.keys()):
                    otherImages.append(Picture(entry.name))
        self.placePictures(otherImages, surAlle, surSortiert.get_width(), surPreview.get_height())
        obj.close()
        
        for pic in sorted+otherImages:
            try:
                pic.date = Image.open("pictures/" + pic.url)._getexif().get(306)
                pic.number = int(pic.date.replace(":","").replace(" ", ""))
            except AttributeError:
                continue

        gray = (130, 130, 130)
        black = (0, 0, 0)

        surSortiert.fill(gray)
        surAlle.fill(gray)
        surPreview.fill(black)

        hoverColor = gray

        running = True
        pressed = False
        firstTime = True
        scrollSize = 30
        toScroll = 0
        dragPos = [0, 0]
        insertMode = False
        scrolled = 0
        while running: 

            mouse = pygame.mouse.get_pos() 

            for ev in pygame.event.get(): 
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                    elif ev.key == pygame.K_f:
                        if mouse[0] > surSortiert.get_width():
                            self.placePictures(otherImages, surAlle, surSortiert.get_width(), surPreview.get_height())
                        else:
                            self.placePictures(sorted, surSortiert)
                            scrolled = 0
                    elif ev.key == pygame.K_i:
                        insertMode = True
                    elif ev.key == pygame.K_s:
                        self.save(sorted, surPreview, font)
                    elif ev.key == pygame.K_PLUS:
                        for pic in sorted+otherImages:
                            pic.width += 10
                            pic.height = int(pic.width / pic.ratio)
                            pic.refreshMap()
                            self.placePictures(sorted, surSortiert, shiftY = scrolled)
                    elif ev.key == pygame.K_MINUS:
                        for pic in sorted+otherImages:
                            pic.width -= 10
                            pic.height = int(pic.width / pic.ratio)
                            pic.refreshMap()
                            self.placePictures(sorted, surSortiert, shiftY = scrolled)
                        
                elif ev.type == pygame.KEYUP: 
                    if ev.key == pygame.K_i:
                        insertMode = False
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
                                    self.placePictures(sorted, surSortiert, shiftY = scrolled)
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
                    if scrolled - toScroll * scrollSize <= 0:
                        for pic in sorted:
                            pic.y -= toScroll * scrollSize
                        scrolled -= toScroll * scrollSize
                elif mouse[1] > surPreview.get_height():
                    for pic in otherImages:
                        pic.y -= toScroll * scrollSize
                toScroll = 0

            if pressed:
                for pic in sorted + otherImages:
                    if firstTime:
                        if pic.checkLocation(mouse[0], mouse[1]):
                            firstTime = False
                            preview.url = pic.url
                            preview.refreshMap()
                            surPreview.fill((0, 0, 0))
                            preview.draw(surPreview)

                            text = font.render(preview.url, False, (0, 0, 0))
                            textRect = text.get_rect()
                            textRect.midtop = (preview.x + preview.width/2, preview.y) 
                            pygame.draw.rect(surPreview, (255, 255, 255), textRect)
                            surPreview.blit(text, textRect)

                            if pic.date != None:
                                text = font.render(pic.date, False, (0, 0, 0))
                                textRect = text.get_rect()
                                textRect.midbottom = (preview.x + preview.width/2, preview.y + preview.height) 
                                pygame.draw.rect(surPreview, (255, 255, 255), textRect)
                                surPreview.blit(text, textRect)

                                if pic in otherImages and insertMode:
                                    otherImages.remove(pic)

                                    pos = len(sorted)
                                    for i, old in enumerate(sorted):
                                        if old.date != None and old.number > pic.number:
                                            pos = i
                                            break
                                    sorted.insert(pos, pic)
                                    self.placePictures(sorted, surSortiert, shiftY = scrolled)
                                    
                            dragStart = mouse
                            drawPic = pic
                    elif not insertMode:
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
    
    def placePictures(self, pictures, surface, shiftX = 0, shiftY = 0, padding = 14):
        if len(pictures) == 0:
            return
        extreme = [0, padding]
        picsPerRow = int((surface.get_width() + padding) / (pictures[0].width + padding))
        shiftX += int((surface.get_width() - (picsPerRow * pictures[0].width + (picsPerRow - 1) * padding)) * 0.5)
        i = 0
        while i < len(pictures):
            if extreme[0] + pictures[i].width < surface.get_width():
                pictures[i].x = extreme[0] + shiftX
                pictures[i].y = extreme[1] + shiftY
                extreme[0] += padding + pictures[i].width
                i += 1
            else:
                extreme[0] = 0
                extreme[1] += pictures[i].height + padding    

    def save(self, data, surface, font):
        newData = {}
        for sample in data:
            newData[sample.url] = str(sample.date)
        jsonData = json.dumps(newData, indent = 4)

        f = open("order.json", "w")
        f.write(jsonData)
        f.close()
        try:
            with open("order.json", "r") as file:
                data = ["Es wurde gespeichert: "] + file.readlines()
                pygame.draw.rect(surface, (255, 255, 255), surface.get_rect())
                pos = [3, 3]
                for line in data:
                    text = font.render(line.replace("\n", ""), False, (0, 0, 0))
                    surface.blit(text, pos)
                    pos[1] += text.get_height()
        except FileNotFoundError:
            print("Fehler beim Speichervorgang")
            print(jsonData)





if __name__ == '__main__':
    start = Startbildschirm()