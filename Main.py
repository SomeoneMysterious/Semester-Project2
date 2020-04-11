from tkinter import *
import time
import random
import sys
import math

tk = Tk()
x = tk.winfo_screenwidth()
y = tk.winfo_screenheight() - 63
print(x)
print(y)
ogX = x
ogY = y
midx = x / 2
midy = y / 2
midox = midx
midoy = midy
offx = -7
offy = 0


class Game:
    health = 200
    ogHealth = health
    lastHealth = health
    gameRunning = False
    points = 0

    def __init__(self):
        tk.title("Protect The Base!")
        self.canvas = Canvas(tk, width=x, height=y)
        tk.resizable(width=False, height=False)
        self.canvas.pack()
        tk.geometry("+-7+0")
        self.clickChecked = True
        self.clickX = 0
        self.clickY = 0
        self.enemyCtrl = EnemyCtrl(self)
        self.tower = Tower(self)
        self.bindKeypresses()
        self.titleScreen()

    def bindKeypresses(self):
        tk.bind("<Button 1>", self.mouseClick)
        tk.bind("<Escape>", self.stopGame)
        tk.bind("q", self.enemyCtrl.killAllEnemies)

    def titleScreen(self):
        self.canvas.create_text(midx, midy - 200, text='Protect the base!', font=('Helvetica', 35), tag="titleText")
        self.canvas.create_text(midx, midy - 140, text='Click anywhere to continue.', font=('Helvetica', 20), tag="titleText")
        while self.clickChecked:
            try:
                tk.update()
            except TclError as e:
                print(e)
                print("You have closed the window!")
                self.quit()
        self.clickChecked = True
        self.gameRunning = True
        self.tower.startGame()
        self.enemyCtrl.startGame()
        self.canvas.delete("titleText")
        tk.update()
        self.handleGame()

    def handleGame(self):
        while self.gameRunning:
            try:
                self.enemyCtrl.handleEnemies()
                if self.health != self.lastHealth:
                    self.lastHealth = self.health
                    self.shrinkWindow()
                if self.health <= 0:
                    self.gameRunning = False
                tk.update()
            except TclError as e:
                print(e)
                print("You have closed the window!")
                self.gameRunning = False
        self.quit()

    def shrinkWindow(self):
        global x, y, midx, midy, offx, offy
        if y > 100:
            y = ogY / self.ogHealth * self.health
        if x > 75:
            x = ogX / self.ogHealth * self.health
        midx = x / 2
        midy = y / 2
        offx = int(midox - midx) - 7
        offy = int(midoy - midy)
        self.canvas.config(width=x, height=y)
        if x > 115:
            tk.geometry('+' + str(offx) + '+' + str(offy))
        self.canvas.pack()
        self.updateLocations()

    def updateLocations(self):
        self.tower.moveTower()
        self.enemyCtrl.winShrinkMove()

    def mouseClick(self, clickloc):
        if self.gameRunning:
            self.enemyCtrl.checkClickedLocation(clickloc.x, clickloc.y)
        else:
            self.clickChecked = False
            self.clickX = clickloc.x
            self.clickY = clickloc.y

    def stopGame(self, clickLoc):
        if self.gameRunning:
            self.gameRunning = False
        else:
            tk.destroy()

    def quit(self):
        self.gameRunning = False
        try:
            tk.destroy()
        except TclError as e:
            print(e)
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
    round = 0

    def __init__(self, gamein):
        self.game = gamein

    def startGame(self):
        self.startRound()

    def startRound(self):
        self.round += 1
        if self.round >= 10:
            level = random.choices([1, 2], weights=[90, 10], k=4 + self.round)
        else:
            level = [1] * (4 + self.round)
        for w in range(0, 4 + self.round):
            self.enemyIDs.append(Enemy(self, self.game, level[w]))

    def handleEnemies(self):
        self.moveEnemies()

    def moveEnemies(self):
        for w in range(-1, len(self.enemyIDs) - 1):
            self.enemyIDs[w].moveSelf()

    def checkClickedLocation(self, clickX, clickY):
        toDelete = []
        for w in range(-1, len(self.enemyIDs) - 1):
            killed = self.enemyIDs[w].checkClickedLocation(clickX, clickY)
            if killed:
                toDelete.append(w)
                self.game.points += 1
        for i in sorted(toDelete, reverse=True):
            del self.enemyIDs[i]
        if len(self.enemyIDs) == 0:
            self.game.points += 2
            self.startRound()
        # print(self.game.points)

    def killAllEnemies(self, *args):
        if self.game.gameRunning:
            if self.game.points >= 30:
                self.game.points -= 30
            else:
                print("That item is too expensive.")
                return
        for w in range(-1, len(self.enemyIDs) - 1):
            self.enemyIDs[0].killSelf()
            del self.enemyIDs[0]
        if self.game.gameRunning:
            self.startRound()

    def winShrinkMove(self):
        for w in range(-1, len(self.enemyIDs) - 1):
            self.enemyIDs[w].baseMove()


class Enemy:
    def __init__(self, enemyCtrlIn, gameIn, level):
        self.enemyCtrl = enemyCtrlIn
        self.game = gameIn
        self.level = level
        self.speedPPS = (75 + 3 * (enemyCtrlIn.round + random.randint(-50, 50) / 10) / 1536 * ogX)  # PPS stands for Pixels Per Second
        self.x = self.y = self.dispX = self.dispY = self.m = self.b = self.oldMove = self.lastMove = self.loopNum = 0
        self.disp = self.disp2 = self.disp3 = self.currDisp = self.spawnWall = self.health = self.img1 = self.img2 = self.img3 = 2
        self.lastTime = self.timeForAnimate = time.time()
        self.stopped = False
        self.setupImages(level)
        self.spawnSelf()

    def setupImages(self, level):
        if level == 2:
            self.health = 2
            self.speedPPS -= 9
            self.img1 = PhotoImage(file='Images\\stick1L2.gif')
            self.img2 = PhotoImage(file='Images\\stick2L2.gif')
            self.img3 = PhotoImage(file='Images\\stick3L2.gif')
        else:
            self.health = 1
            self.img1 = PhotoImage(file='Images\\stick1.gif')
            self.img2 = PhotoImage(file='Images\\stick2.gif')
            self.img3 = PhotoImage(file='Images\\stick3.gif')

    def setupDisp(self):
        self.dispX = self.x - offx
        self.dispY = self.y - offy
        self.disp = self.game.canvas.create_image(self.dispX, self.dispY, image=self.img1)
        self.disp2 = self.game.canvas.create_image(self.dispX, self.dispY, image=self.img2)
        self.disp3 = self.game.canvas.create_image(self.dispX, self.dispY, image=self.img3)
        self.hideEnemy(self.disp)
        self.hideEnemy(self.disp3)

    def spawnSelf(self):
        # Screen must be bigger than 30 for both sides or this will break
        self.spawnWall = random.randint(1, 4)
        if self.spawnWall == 1:  # Top
            self.y = 30
            while True:
                self.x = random.randint(30, ogX - 30)
                if abs(midox - self.x) > 100:
                    break
            self.speedPPS *= math.ceil(abs(midx - self.x) / (midx - 30))
            if self.speedPPS < self.enemyCtrl.round:
                self.speedPPS = self.enemyCtrl.round
        elif self.spawnWall == 2:  # Bottom
            self.y = ogY - 30
            while True:
                self.x = random.randint(30, ogX - 30)
                if abs(midox - self.x) > 100:
                    break
            self.speedPPS *= math.ceil(abs(midx - self.x) / (midx - 30))
            if self.speedPPS < self.enemyCtrl.round:
                self.speedPPS = self.enemyCtrl.round
        elif self.spawnWall == 3:  # Left
            self.x = 30
            self.y = random.randint(30, ogY - 30)
        else:  # Right
            self.x = ogX - 30
            self.y = random.randint(30, ogY - 30)
        self.m = (midoy - self.y) / (midox - self.x)
        self.b = midoy + self.m * midox
        self.setupDisp()
        self.lastTime = time.time()

    def hideEnemy(self, toHide):
        self.game.canvas.itemconfigure(toHide, state='hidden')

    def showEnemy(self, toShow):
        self.game.canvas.itemconfigure(toShow, state='normal')

    def swapCostume(self):
        self.currDisp += 1
        if self.currDisp == 2:
            self.hideEnemy(self.disp)
            self.showEnemy(self.disp2)
        elif self.currDisp == 3:
            self.hideEnemy(self.disp2)
            self.showEnemy(self.disp3)
        elif self.currDisp == 4:
            self.hideEnemy(self.disp3)
            self.showEnemy(self.disp2)
        else:
            self.hideEnemy(self.disp2)
            self.showEnemy(self.disp)
            self.currDisp = 1

    def moveSelf(self):
        self.oldMove = self.lastMove
        self.lastMove = self.x + self.y
        if not self.stopped:
            if abs(midoy - self.y) > 50 or abs(midox - self.x - 8) > 35:
                Time = time.time()
                if self.x > midox:
                    self.x -= self.speedPPS * (Time - self.lastTime)
                else:
                    self.x += self.speedPPS * (Time - self.lastTime)
                self.y = abs(-1 * self.m * self.x + self.b - ogY)
                animateTime = time.time()
                if animateTime - self.timeForAnimate > .15:
                    self.swapCostume()
                    self.timeForAnimate = animateTime
                self.lastTime = animateTime
                self.baseMove()
                if self.oldMove == self.x + self.y and self.oldMove != self.lastMove:
                    self.stopped = True
                    self.currDisp = 1
                    self.swapCostume()
                    self.lastTime = time.time()
            else:
                self.stopped = True
                self.currDisp = 1
                self.swapCostume()
                self.lastTime = time.time()
        else:
            Time = time.time()
            if self.lastTime + 1 <= Time:
                self.game.health -= 1
                self.lastTime = Time

    def baseMove(self):
        self.dispX = self.x - offx
        self.dispY = self.y - offy
        self.game.canvas.coords(self.disp, (self.dispX, self.dispY))
        self.game.canvas.coords(self.disp2, (self.dispX, self.dispY))
        self.game.canvas.coords(self.disp3, (self.dispX, self.dispY))

    def killSelf(self):
        self.game.canvas.delete(self.disp, self.disp2, self.disp3)

    def checkClickedLocation(self, clickX, clickY):
        if abs(self.dispX - clickX) <= 8 and abs(self.dispY - clickY) <= 16:
            self.health -= 1
            if self.health == 1:
                self.killSelf()
                self.setupImages(1)
                self.setupDisp()
            elif self.health <= 0:
                self.killSelf()
                return True
        return False


game = Game()
