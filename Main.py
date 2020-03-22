from tkinter import *
import time
import random
import sys
tk = Tk()
x = tk.winfo_screenwidth()
y = tk.winfo_screenheight()-63
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
        time.sleep(2)
        self.handleGame()

    def handleGame(self):
        while self.gameRunning:
            self.enemyCtrl.handleEnemies()
            if self.health != self.lastHealth:
                self.lastHealth = self.health
                self.shrinkWindow()
            if self.health <= 0:
                self.gameRunning = False
            self.shrinkTest()
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
        tk.update()

    def updateLocations(self):
        self.tower.moveTower()
        self.enemyCtrl.winShrinkMove()

    def shrinkTest(self):
        if random.randint(1, 100) == 10:
            self.health -= 1

    def mouseClick(self, clickloc):
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
        tk.update()

    def moveTower(self):
        self.game.canvas.coords(self.tower, (midx, midy))
        tk.update()

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
        self.enemyIDs.append(Enemy(self, self.game, 1))

    def handleEnemies(self):
        self.moveEnemies()

    def moveEnemies(self):
        pass

    def winShrinkMove(self):
        self.enemyIDs[0].winShrinkMove()
        tk.update()


class Enemy:
    def __init__(self, enemyCtrlIn, gameIn, level):
        self.enemyCtrl = enemyCtrlIn
        self.game = gameIn
        self.level = level
        self.speed = 10+(0.5*enemyCtrlIn.round)
        self.img1 = PhotoImage(file='Images\\stick2.gif')
        self.x = self.y = self.dispX = self.dispY = self.disp = 0
        self.spawnSelf()

    def spawnSelf(self):
        # Screen must be bigger than 30 for both sides or this will break
        wall = random.randint(1, 4)
        if wall == 1:  # Top
            self.y = 30
            self.x = random.randint(30, ogX-30)
        elif wall == 2:  # Bottom
            self.y = ogY-30
            self.x = random.randint(30, ogX-30)
        elif wall == 3:  # Left
            self.x = 30
            self.y = random.randint(30, ogY-30)
        else:  # Right
            self.x = ogX-30
            self.y = random.randint(30, ogY-30)
        self.dispX = self.x-offx
        self.dispY = self.y-offy
        self.disp = self.game.canvas.create_image(self.dispX, self.dispY, image=self.img1)

    def winShrinkMove(self):
        self.dispX = self.x - offx
        self.dispY = self.y - offy
        self.game.canvas.coords(self.disp, (self.dispX, self.dispY))


game = Game()
print(game.canvas)
