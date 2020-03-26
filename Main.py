from tkinter import *
import time
import random
import sys
tk = Tk()
x = tk.winfo_screenwidth()
y = tk.winfo_screenheight()-63
print(x)
ogX = x
ogY = y
midx = x/2
midy = y/2
midox = midx
midoy = midy
offx = -7
offy = 0


class Game:
    health = 200
    ogHealth = health
    lastHealth = health
    gameRunning = False

    def __init__(self):
        tk.title("Protect The Base!")
        self.canvas = Canvas(tk, width=x, height=y)
        tk.resizable(width=False, height=False)
        self.canvas.pack()
        tk.geometry("+-7+0")
        self.clickChecked = True
        self.clickX = 0
        self.clickY = 0
        tk.bind("<Button 1>", self.mouseClick)
        self.enemyCtrl = EnemyCtrl(self)
        self.tower = Tower(self)
        self.titleScreen()

    def titleScreen(self):
        self.canvas.create_text(midx, midy-200, text='Protect the base!', font=('Helvetica', 35), tag="titleText")
        self.canvas.create_text(midx, midy-140, text='Click anywhere to continue.', font=('Helvetica', 20), tag="titleText")
        while self.clickChecked:
            tk.update()
        self.clickChecked = True
        self.gameRunning = True
        self.tower.startGame()
        self.enemyCtrl.startGame()
        self.canvas.delete("titleText")
        tk.update()
        self.handleGame()

    def handleGame(self):
        while self.gameRunning:
            self.enemyCtrl.handleEnemies()
            if self.health != self.lastHealth:
                self.lastHealth = self.health
                self.shrinkWindow()
            if self.health <= 0:
                self.gameRunning = False
            tk.update()
        self.endScreen()

    def shrinkWindow(self):
        global x, y, midx, midy, offx, offy
        y = ogY/self.ogHealth*self.health
        x = ogX/self.ogHealth*self.health
        midx = x/2
        midy = y/2
        offx = int(midox-midx)-7
        offy = int(midoy-midy)
        self.canvas.config(width=x, height=y)
        if x > 115:
            tk.geometry('+'+str(offx)+'+'+str(offy))
        self.canvas.pack()
        self.updateLocations()

    def updateLocations(self):
        self.tower.moveTower()
        self.enemyCtrl.winShrinkMove()

    def shrinkTest(self):
        if random.randint(1, 100) == 10:
            self.health -= 1

    def mouseClick(self, clickloc):
        print(clickloc)
        if self.gameRunning:
            self.enemyCtrl.checkClickedLocation(clickloc.x, clickloc.y)
        else:
            self.clickChecked = False
            self.clickX = clickloc.x
            self.clickY = clickloc.y

    def endScreen(self):
        tk.destroy()
        sys.exit()


class Tower:

    def __init__(self, gamein):
        self.game = gamein
        self.towerImg = PhotoImage(file='Images\\towerImg.gif')
        self.tower = self.game.canvas.create_image(midx, midy, image=self.towerImg)
        self.hideTower()

    def moveTower(self):
        self.game.canvas.coords(self.tower, (midx, midy))

    def startGame(self):
        self.showTower()

    def hideTower(self):
        self.game.canvas.itemconfigure(self.tower, state='hidden')

    def showTower(self):
        self.game.canvas.itemconfigure(self.tower, state='normal')


class EnemyCtrl:
    enemyIDs = []
    round = 1

    def __init__(self, gamein):
        self.game = gamein

    def startGame(self):
        self.startRound()

    def startRound(self):
        self.round += 1
        for w in range(0, 4+self.round):
            self.enemyIDs.append(Enemy(self, self.game, self.round))

    def handleEnemies(self):
        self.moveEnemies()

    def moveEnemies(self):
        for w in range(-1, len(self.enemyIDs)-1):
            self.enemyIDs[w].moveSelf()

    def checkClickedLocation(self, clickX, clickY):
        toDelete = []
        for w in range(-1, len(self.enemyIDs)-1):
            killed = self.enemyIDs[w].checkClickedLocation(clickX, clickY)
            if killed:
                toDelete.append(w)
        for i in sorted(toDelete, reverse=True):
            del self.enemyIDs[i]
        if len(self.enemyIDs) == 0:
            self.startRound()

    def winShrinkMove(self):
        for w in range(-1, len(self.enemyIDs)-1):
            self.enemyIDs[w].baseMove()


class Enemy:
    def __init__(self, enemyCtrlIn, gameIn, level):
        self.enemyCtrl = enemyCtrlIn
        self.game = gameIn
        self.level = level
        self.speedPPS = 75 + (3 * enemyCtrlIn.round)  # PPS stands for Pixels Per Second
        self.img1 = PhotoImage(file='Images\\stick2.gif')
        self.x = self.y = self.dispX = self.dispY = self.disp = self.spawnWall = self.m = self.b = self.oldMove = self.lastMove = 0
        self.lastTime = time.time()
        self.stopped = False
        self.spawnSelf()

    def spawnSelf(self):
        # Screen must be bigger than 30 for both sides or this will break
        self.spawnWall = random.randint(1, 4)
        if self.spawnWall == 1:  # Top
            self.y = 30
            while True:
                self.x = random.randint(30, ogX-30)
                if abs(midox-self.x) > 10:
                    break
            self.speedPPS -= abs(abs(midx - self.x) / 20 - 38.4)
            print(self.speedPPS, self.x, self.y)
        elif self.spawnWall == 2:  # Bottom
            self.y = ogY-30
            while True:
                self.x = random.randint(30, ogX-30)
                if abs(midox-self.x) > 10:
                    break
            self.speedPPS -= abs(abs(midx - self.x) / 20 - 38.4)
            print(self.speedPPS, self.x, self.y)
        elif self.spawnWall == 3:  # Left
            self.x = 30
            self.y = random.randint(30, ogY-30)
        else:  # Right
            self.x = ogX-30
            self.y = random.randint(30, ogY-30)
        self.m = (midoy-self.y)/(midox-self.x)
        self.b = midoy+self.m*midox
        self.dispX = self.x-offx
        self.dispY = self.y-offy
        self.disp = self.game.canvas.create_image(self.dispX, self.dispY, image=self.img1)
        self.lastTime = time.time()

    def moveSelf(self):
        self.oldMove = self.lastMove
        self.lastMove = self.x+self.y
        if not self.stopped:
            if abs(midoy-self.y) > 55 or abs(midox-self.x-6) > 40:
                Time = time.time()
                if self.x > midox:
                    self.x -= self.speedPPS*(Time-self.lastTime)
                else:
                    self.x += self.speedPPS*(Time-self.lastTime)
                self.y = abs(-1*self.m*self.x+self.b-ogY)
                self.lastTime = Time
                self.baseMove()
                if self.oldMove == self.x+self.y and self.oldMove != self.lastMove:
                    self.stopped = True
                    self.lastTime = time.time()
            else:
                self.stopped = True
                self.lastTime = time.time()
        else:
            Time = time.time()
            if self.lastTime+1 <= Time:
                self.game.health -= 1
                self.lastTime = Time

    def baseMove(self):
        self.dispX = self.x - offx
        self.dispY = self.y - offy
        self.game.canvas.coords(self.disp, (self.dispX, self.dispY))

    def checkClickedLocation(self, clickX, clickY):
        if abs(self.dispX-clickX) <= 8 and abs(self.dispY-clickY) <= 16:
            self.game.canvas.delete(self.disp)
            return True
        else:
            return False


game = Game()
print(game.canvas)
