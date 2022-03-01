
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
        fullscreen = False
        
        # initialize Pygame and GUI
        pygame.init()
        
        self.font = pygame.font.SysFont('arialnarrow', 20) 
        dimension = (1000,650) 
        if(not fullscreen):
            self.screen = pygame.display.set_mode(dimension)
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            infoObject = pygame.display.Info()
            dimension = (infoObject.current_w, infoObject.current_h)
        
        self.tmpScreen = pygame.Surface((dimension[0] + 200, dimension[1] + 200))
        self.tmpScreen.set_alpha(180)
        pygame.display.set_caption("Diashow - Editor")

        splitX = 0.3
        splitY = 0.6
        self.surSortiert = pygame.Surface((dimension[0] * splitX, dimension[1]))
        self.surAlle = pygame.Surface((dimension[0] * (1-splitX), dimension[1] * (1-splitY)))
        self.surPreview = pygame.Surface((dimension[0] * (1-splitX), dimension[1] * splitY))
        self.preview = Picture("", 0, 0, self.surPreview.get_width(), self.surPreview.get_height())

        # load data
        self.sorted = []
        try:
            with open("order.json", "r") as file:
                data = json.load(file)
                for name in list(data.get("order")):
                    self.sorted.append(Picture(name))
        except FileNotFoundError:
            data = {"order":[], "ignore":[]}
            print("No File imported")

        self.placePictures(self.sorted, self.surSortiert)

        self.otherImages = []
        obj = os.scandir("pictures")
        for entry in obj :
            if entry.is_file() and entry.name != ".DS_Store" and entry.name[-4:] in (".png", ".jpg", "jpeg", ".tif", ".gif"):
                if not entry.name in data.get("order")+data.get("ignore"):
                    self.otherImages.append(Picture(entry.name))
        self.placePictures(self.otherImages, self.surAlle, self.surSortiert.get_width(), self.surPreview.get_height())
        obj.close()

        self.deleted = data.get("ignore")
        
        for pic in self.sorted+self.otherImages:
            try:
                pic.date = Image.open("pictures/" + pic.url)._getexif().get(306)
                pic.number = int(pic.date.replace(":","").replace(" ", ""))
            except AttributeError:
                continue

    def mainloop(self):
        gray = (130, 130, 130)
        black = (0, 0, 0)
        clock = pygame.time.Clock()

        self.surSortiert.fill(gray)
        self.surAlle.fill(gray)
        self.surPreview.fill(black)

        hoverColor = gray

        scrollSize = 60
        running = True
        pressed = False
        firstTime = True
        toScroll = 0
        dragPos = [0, 0]
        insertMode = False
        deleteMode = False
        scrolled = 0

        while running: 

            # handling events
            mouse = pygame.mouse.get_pos() 
            for ev in pygame.event.get(): 

                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                    elif ev.key == pygame.K_f:
                        if mouse[0] > self.surSortiert.get_width():
                            self.placePictures(self.otherImages, self.surAlle, self.surSortiert.get_width(), self.surPreview.get_height())
                        else:
                            self.placePictures(self.sorted, self.surSortiert)
                            scrolled = 0
                    elif ev.key == pygame.K_i:
                        insertMode = True
                    elif ev.key == pygame.K_d:
                        deleteMode = True
                    elif ev.key == pygame.K_s:
                        self.save(self.sorted, self.deleted, self.surPreview)
                    elif ev.key == pygame.K_PLUS:
                        for pic in self.sorted+self.otherImages:
                            pic.width += 10
                            pic.height = int(pic.width / pic.ratio)
                            pic.refreshMap()
                            self.placePictures(self.sorted, self.surSortiert, shiftY = scrolled)
                    elif ev.key == pygame.K_MINUS:
                        for pic in self.sorted+self.otherImages:
                            pic.width -= 10
                            pic.height = int(pic.width / pic.ratio)
                            pic.refreshMap()
                            self.placePictures(self.sorted, self.surSortiert, shiftY = scrolled)
                    elif ev.key == pygame.K_RIGHT and self.preview.url != "" and drawPic in self.sorted[:-1]:
                        self.previewUrl(self.sorted[self.sorted.index(drawPic) + 1])
                        drawPic = self.sorted[self.sorted.index(drawPic) + 1]
                    elif ev.key == pygame.K_LEFT and self.preview.url != "" and drawPic in self.sorted[1:]:
                        self.previewUrl(self.sorted[self.sorted.index(drawPic) - 1])
                        drawPic = self.sorted[self.sorted.index(drawPic) - 1]

                        
                elif ev.type == pygame.KEYUP: 
                    if ev.key == pygame.K_i:
                        insertMode = False
                    elif ev.key == pygame.K_d:
                        deleteMode = False
                
                elif ev.type == pygame.QUIT: 
                    running = False

                elif ev.type == pygame.MOUSEBUTTONDOWN: 
                    # 4 and 5 -> Mousewheel up and down
                    if ev.button == 4:
                        toScroll -= 1
                    elif ev.button == 5:
                        toScroll += 1
                    else:
                        pressed = True
                elif ev.type == pygame.MOUSEBUTTONUP: 
                    pressed = False
                    firstTime = True
                    self.tmpScreen.fill((255, 255, 255, 0))
                    if dragPos != [0, 0]:
                        if mouse[0] < self.surSortiert.get_width():
                            for i, pic in enumerate(self.sorted):
                                if pic.checkLocation(mouse[0], mouse[1]):
                                    pos = i
                                    if drawPic in self.otherImages:
                                        self.otherImages.remove(drawPic)
                                    else:
                                        self.sorted.remove(drawPic)
                                    self.sorted.insert(pos, drawPic)
                                    self.placePictures(self.sorted, self.surSortiert, shiftY = scrolled)
                                    print("inserted:" + str(i))
                        else:
                            if mouse[1] > self.surPreview.get_height():
                                drawPic.x += dragPos[0]
                                drawPic.y += dragPos[1]
                                if drawPic in self.sorted:
                                    self.sorted.remove(drawPic)
                                    self.otherImages.append(drawPic)
                        dragPos[0] = 0
                        dragPos[1] = 0

            if toScroll != 0:
                if mouse[0] < self.surSortiert.get_width():
                    if scrolled - toScroll * scrollSize <= 0:
                        for pic in self.sorted:
                            pic.y -= toScroll * scrollSize
                        scrolled -= toScroll * scrollSize
                elif mouse[1] > self.surPreview.get_height():
                    for pic in self.otherImages:
                        pic.y -= toScroll * scrollSize
                toScroll = 0

            if pressed:
                for pic in self.sorted + self.otherImages:
                    if firstTime:
                        if pic.checkLocation(mouse[0], mouse[1]):
                            if not deleteMode:
                                firstTime = False
                                self.previewUrl(pic)

                                if pic.date != None:

                                    if pic in self.otherImages and insertMode:
                                        self.otherImages.remove(pic)

                                        pos = len(self.sorted)
                                        for i, old in enumerate(self.sorted):
                                            if old.date != None and old.number > pic.number:
                                                pos = i
                                                break
                                        self.sorted.insert(pos, pic)
                                        self.placePictures(self.sorted, self.surSortiert, shiftY = scrolled)
                                        
                                dragStart = mouse
                                drawPic = pic
                            else:
                                if pic in self.sorted:
                                    self.sorted.remove(pic)
                                else:
                                    self.otherImages.remove(pic)
                                self.deleted.append(pic.url)
                    elif not insertMode:
                        dragPos[0] = mouse[0] - dragStart[0]
                        dragPos[1] = mouse[1] - dragStart[1]
                        self.tmpScreen.fill((255, 255, 255, 0))
                        drawPic.draw(self.tmpScreen)

            # draw Changes
            self.screen.fill((0, 0, 0)) 
            self.screen.blit(self.surSortiert, (0, 0))
            self.screen.blit(self.surAlle, (self.surSortiert.get_width(), self.surPreview.get_height()))

            for pic in self.sorted:
                pic.drawRectangle(self.screen, hoverColor)
                pic.draw(self.screen)

            for pic in self.otherImages:
                pic.drawRectangle(self.screen, hoverColor)
                pic.draw(self.screen)

            self.screen.blit(self.surPreview, (self.surSortiert.get_width(), 0))
            self.screen.blit(self.tmpScreen, dragPos)

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

    def previewUrl(self, pic):
        self.preview.url = pic.url
        self.preview.refreshMap()
        self.surPreview.fill((0, 0, 0))
        self.preview.draw(self.surPreview)

        text = self.font.render(self.preview.url, False, (0, 0, 0))
        textRect = text.get_rect()
        textRect.midtop = (self.preview.x + self.preview.width/2, self.preview.y) 
        pygame.draw.rect(self.surPreview, (255, 255, 255), textRect)
        self.surPreview.blit(text, textRect)

        if pic.date != None:
            text = self.font.render(pic.date, False, (0, 0, 0))
            textRect = text.get_rect()
            textRect.midbottom = (self.preview.x + self.preview.width/2, self.preview.y + self.preview.height) 
            pygame.draw.rect(self.surPreview, (255, 255, 255), textRect)
            self.surPreview.blit(text, textRect)
    
    def save(self, sortiert, ignore, surface):
        newData = []
        for sample in sortiert:
            newData.append(sample.url)
        jsonData = json.dumps({"order":newData, "ignore":ignore}, indent = 4)

        f = open("order.json", "w")
        f.write(jsonData)
        f.close()
        try:
            with open("order.json", "r") as file:
                data = ["Es wurde gespeichert: "] + file.readlines()
                pygame.draw.rect(surface, (255, 255, 255), surface.get_rect())
                pos = [3, 3]
                for line in data:
                    text = self.font.render(line.replace("\n", ""), False, (0, 0, 0))
                    surface.blit(text, pos)
                    pos[1] += text.get_height()
        except FileNotFoundError:
            print("Fehler beim Speichervorgang")
            print(jsonData)


if __name__ == '__main__':
    start = Startbildschirm()
    start.mainloop()