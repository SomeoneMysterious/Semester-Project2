from tkinter import *
import time
import random
import sys
import math
from tkinter import colorchooser
pygameInstalled = True
try:
    from pygame import mixer
except ModuleNotFoundError as er:
    print("Pygame not installed, required for audio, game will not use any audio.")
    pygameInstalled = False

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
    gamePaused = False
    points = 0
    dispMenuHidden = False

    def __init__(self):
        tk.title("Protect The Base!")
        self.canvas = Canvas(tk, width=x, height=y)
        tk.resizable(width=False, height=False)
        self.canvas.pack()
        tk.geometry("+-7+0")
        self.clickChecked = True
        self.clickX = self.clickY = self.volumeToSet = 0
        self.menubar = self.shopMenu = self.dispMenu = self.gameMenu = 0
        if pygameInstalled:
            mixer.init()
        self.enemyCtrl = EnemyCtrl(self)
        self.tower = Tower(self)
        self.bindKeypressesAndMenu()
        self.titleScreen()

    def bindKeypressesAndMenu(self):
        self.menubar = Menu(tk)
        self.gameMenu = Menu(tk, tearoff=0)
        if pygameInstalled:
            self.gameMenu.add_command(label="Set Volume %", command=self.changeVolume)
        # self.gameMenu.add_command(label="Resize Max Sized Window")  # Will be moved to it's own file
        self.gameMenu.add_command(label="Pause/Unpause Game", command=self.pauseGame)
        # This comment is is memory of an attempt at a restart. I don't think I'll try that again.
        self.gameMenu.add_command(label="Quit", command=self.quit)
        self.dispMenu = Menu(tk, tearoff=0)
        self.dispMenu.add_command(label="Set Background Color", command=self.setBackgroundColor)
        self.dispMenu.add_command(label="Toggle Enemy Leg Motion", command=self.enemyCtrl.toggleLegMotion)
        self.shopMenu = Menu(tk, tearoff=0)
        self.shopMenu.add_command(label="Clear All Enemies (30 Points)", command=self.enemyCtrl.killAllEnemies)
        self.menubar.add_cascade(label="Game", menu=self.gameMenu)
        self.menubar.add_cascade(label="View", menu=self.dispMenu)
        self.menubar.add_cascade(label="Shop", menu=self.shopMenu)
        tk.config(menu=self.menubar)
        tk.bind("<Button 1>", self.mouseClick)
        tk.bind("<Escape>", self.stopGame)
        tk.bind("q", self.enemyCtrl.killAllEnemies)
        tk.bind('p', self.pauseGame)
        tk.bind('e', lambda clickLoc=None: print('How dare you press the "e" key!'))

    def titleScreen(self):
        self.canvas.create_text(midx, midy - 200, text='Protect the base!', font=('Helvetica', 35), tag="titleText")
        self.canvas.create_text(midx, midy - 140, text='Click anywhere to continue.', font=('Helvetica', 20), tag="titleText")
        if pygameInstalled:
            mixer.music.load("Sounds/Background1.wav")
            mixer.music.play(-1)
        while self.clickChecked:
            try:
                tk.update()
            except TclError as e:
                print(e)
                print("You have closed the window!")
                self.quit()
        self.clickChecked = True
        if pygameInstalled:
            mixer.music.load("Sounds/Background2.wav")
            mixer.music.play(-1)
        self.gameRunning = True
        self.tower.startGame()
        self.enemyCtrl.startGame()
        self.canvas.delete("titleText")
        tk.update_idletasks()
        self.handleGame()

    def endScreen(self):
        global x, y
        self.tower.remove()
        self.enemyCtrl.killAllEnemies()
        if pygameInstalled:
            mixer.music.load("Sounds/Background1.wav")
            mixer.music.play(-1)
        t1 = self.canvas.create_text(midx, midy - 200, text='You Have Lost!', font=('Helvetica', 35))
        t2 = self.canvas.create_text(midx, midy - 140, text='You got to round %i.' % self.enemyCtrl.round, font=('Helvetica', 20))
        for self.health in range(0, self.ogHealth+2, 2):
            self.shrinkWindow()
            if x > 140 and self.dispMenuHidden:
                self.menubar = Menu(tk)
                self.menubar.add_cascade(label="Game", menu=self.gameMenu)
                self.menubar.add_cascade(label="View", menu=self.dispMenu)
                self.menubar.add_cascade(label="Shop", menu=self.shopMenu)
                tk.config(menu=self.menubar)
                self.dispMenuHidden = False
            self.canvas.coords(t1, (midx, midy - 200))
            self.canvas.coords(t2, (midx, midy - 140))
            tk.update()
        try:
            while True:
                tk.update()
        except TclError as e:
            print(e)
            print("You have closed the window!")
            self.quit()

    def handleGame(self):
        while self.gameRunning:
            try:
                while self.gamePaused:
                    tk.update()
                    time.sleep(.05)
                self.enemyCtrl.handleEnemies()
                if self.health != self.lastHealth:
                    self.lastHealth = self.health
                    self.shrinkWindow()
                    self.updateLocations()
                if self.health <= 0:
                    self.gameRunning = False
                    self.endScreen()
                tk.update()
            except TclError as e:
                print(e)
                print("You have closed the window!")
                self.gameRunning = False
                self.quit()

    def pauseGame(self, *args):
        if self.gamePaused:
            self.gamePaused = False
            self.enemyCtrl.unpauseEnemies()
        else:
            self.gamePaused = True

    def shrinkWindow(self):
        global x, y, midx, midy, offx, offy
        if self.gameRunning:
            if y > 100:
                y = ogY / self.ogHealth * self.health
            if x > 75:
                x = ogX / self.ogHealth * self.health
            if x <= 140 and not self.dispMenuHidden:
                self.menubar = Menu(tk)
                self.menubar.add_cascade(label="Game", menu=self.gameMenu)
                self.menubar.add_cascade(label="Shop", menu=self.shopMenu)
                tk.config(menu=self.menubar)
                self.dispMenuHidden = True
        else:
            y = ogY / self.ogHealth * self.health
            x = ogX / self.ogHealth * self.health
        midx = x / 2
        midy = y / 2
        offx = int(midox - midx) - 7
        offy = int(midoy - midy)
        self.canvas.config(width=x, height=y)
        if x > 115:
            tk.geometry('+' + str(offx) + '+' + str(offy))
        self.canvas.pack()

    def updateLocations(self):
        self.tower.moveTower()
        self.enemyCtrl.winShrinkMove()

    def setBackgroundColor(self):
        color = colorchooser.askcolor()
        print(color)
        if color[1] is None:
            self.canvas.configure(bg='SystemButtonFace')
        else:
            self.canvas.configure(bg=color[1])
        self.enemyCtrl.unpauseEnemies()

    def changeVolume(self):
        global w2
        self.volumeToSet = -1
        tk2 = Tk()
        canvas = Canvas(tk2, width=150, height=10)
        tk2.resizable(width=False, height=False)
        tk2.geometry('+' + str(int(midox)) + '+' + str(int(midoy)))
        canvas.pack()
        w2 = Scale(tk2, from_=0, to=100, orient=HORIZONTAL)
        w2.set(mixer.music.get_volume() * 100)
        w2.pack()
        Button(tk2, text='Set', command=self.setVolume).pack()
        while self.volumeToSet == -1:
            try:
                tk.update()
                tk2.update()
            except TclError as e:
                self.volumeToSet = -2
        try:
            tk2.destroy()
        except TclError as e:
            pass
        if self.volumeToSet != -2:
            self.volumeToSet /= 100
            mixer.music.set_volume(self.volumeToSet)
            mixer.Sound.set_volume(self.enemyCtrl.stepSound, self.volumeToSet)
            mixer.Sound.set_volume(self.enemyCtrl.shotSound, self.volumeToSet)
        self.enemyCtrl.unpauseEnemies()

    def setVolume(self):
        global w2
        self.volumeToSet = w2.get()

    def mouseClick(self, clickloc):
        if self.gameRunning:
            if not self.gamePaused:
                self.enemyCtrl.checkClickedLocation(clickloc.x, clickloc.y)
        else:
            self.clickChecked = False
            self.clickX = clickloc.x
            self.clickY = clickloc.y

    def stopGame(self, *args):
        if self.gameRunning:
            self.gameRunning = False
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

    def remove(self):
        self.game.canvas.delete(self.tower)

    def hideTower(self):
        self.game.canvas.itemconfigure(self.tower, state='hidden')

    def showTower(self):
        self.game.canvas.itemconfigure(self.tower, state='normal')


class EnemyCtrl:
    enemyIDs = []
    round = 0
    moveLegs = True

    def __init__(self, gamein):
        self.game = gamein
        if pygameInstalled:
            self.shotSound = mixer.Sound("Sounds/shot sound.wav")
            self.stepSound = mixer.Sound("Sounds/footstep.wav")

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

    def unpauseEnemies(self):
        for w in range(-1, len(self.enemyIDs) - 1):
            self.enemyIDs[w].unpause()

    def toggleLegMotion(self):
        self.moveLegs = not self.moveLegs
        for w in range(-1, len(self.enemyIDs) - 1):
            self.enemyIDs[w].toggleLegMotion()
        self.unpauseEnemies()

    def checkClickedLocation(self, clickX, clickY):
        toDelete = []
        if pygameInstalled:
            mixer.Sound.play(self.shotSound)
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
                if len(args) == 0:
                    self.unpauseEnemies()
                return
        for w in range(-1, len(self.enemyIDs) - 1):
            self.enemyIDs[0].killSelf()
            del self.enemyIDs[0]
        if self.game.gameRunning:
            if len(args) == 0:
                self.unpauseEnemies()
            self.startRound()

    def winShrinkMove(self):
        for w in range(-1, len(self.enemyIDs) - 1):
            self.enemyIDs[w].baseMove()


class Enemy:
    x = y = dispX = dispY = m = b = oldMove = lastMove = loopNum = 0
    disp = disp2 = disp3 = currDisp = spawnWall = lives = img1 = img2 = img3 = 2
    lastTime = timeForAnimate = timeToStop = time.time()

    def __init__(self, enemyCtrlIn, gameIn, level):
        self.enemyCtrl = enemyCtrlIn
        self.game = gameIn
        self.level = level
        self.speedPPS = (75 + 3 * (enemyCtrlIn.round + random.randint(-50, 50) / 10) / 1536 * ogX)  # PPS stands for Pixels Per Second
        self.moveLegs = enemyCtrlIn.moveLegs
        self.stopped = False
        self.setupImages(level)
        self.spawnSelf()

    def setupImages(self, level):
        if level == 2:
            self.lives = 2
            self.speedPPS -= 9
            self.img1 = PhotoImage(file='Images\\stick1L2.gif')
            self.img2 = PhotoImage(file='Images\\stick2L2.gif')
            self.img3 = PhotoImage(file='Images\\stick3L2.gif')
        else:
            self.lives = 1
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
        # Base Screen must be bigger than 100 for width and 30 for any or this will break (likely)
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
        self.timeToStop = time.time() + abs(self.x - midox) / self.speedPPS + .2  # .2 second buffer
        self.setupDisp()
        self.lastTime = time.time()

    def hideEnemy(self, toHide):
        self.game.canvas.itemconfigure(toHide, state='hidden')

    def showEnemy(self, toShow):
        self.game.canvas.itemconfigure(toShow, state='normal')

    def hitTargetPrep(self):
        self.stopped = True
        self.currDisp = 1
        self.swapCostume()
        self.lastTime = time.time()

    def swapCostume(self):
        self.currDisp += 1
        if self.currDisp == 2:
            self.hideEnemy(self.disp)
            self.hideEnemy(self.disp3)
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

    def toggleLegMotion(self):
        self.moveLegs = not self.moveLegs
        if self.moveLegs:
            self.timeForAnimate = time.time()
        else:
            self.currDisp = 1
            self.swapCostume()

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
                if self.moveLegs:
                    animateTime = time.time()
                    if animateTime - self.timeForAnimate > .15:
                        self.swapCostume()
                        self.timeForAnimate = animateTime
                self.lastTime = Time
                self.baseMove()
                if self.timeToStop < Time:
                    # The code for 1 & 2 does a good enough job, don't necessarily know how...
                    if self.spawnWall == 1:
                        self.y = midoy - 50
                        self.x = abs((-1 * self.y - self.b + ogY) / self.m) / 2 + 375
                    elif self.spawnWall == 2:
                        self.y = midoy + 50
                        self.x = abs((-1 * self.y - self.b + ogY) / self.m) / 2 + 375
                    elif self.spawnWall == 3:
                        self.x = midox - 43
                        self.y = abs(-1 * self.m * self.x + self.b - ogY)
                    else:
                        self.x = midox + 27
                        self.y = abs(-1 * self.m * self.x + self.b - ogY)
                    self.hitTargetPrep()
                elif self.oldMove == self.x + self.y and self.oldMove != self.lastMove:
                    self.hitTargetPrep()
            else:
                self.hitTargetPrep()
        else:
            Time = time.time()
            if self.lastTime + 1 <= Time:
                self.game.health -= math.floor(Time - self.lastTime)
                self.lastTime = Time

    def baseMove(self):
        self.dispX = self.x - offx
        self.dispY = self.y - offy
        self.game.canvas.coords(self.disp, (self.dispX, self.dispY))
        self.game.canvas.coords(self.disp2, (self.dispX, self.dispY))
        self.game.canvas.coords(self.disp3, (self.dispX, self.dispY))

    def killSelf(self):
        self.game.canvas.delete(self.disp, self.disp2, self.disp3)

    def unpause(self):
        Time = time.time()
        self.timeToStop += Time - self.lastTime
        self.lastTime = self.timeForAnimate = Time

    def checkClickedLocation(self, clickX, clickY):
        if abs(self.dispX - clickX) <= 8 and abs(self.dispY - clickY) <= 16:
            self.lives -= 1
            if self.lives == 1:
                self.killSelf()
                self.setupImages(1)
                self.setupDisp()
            elif self.lives <= 0:
                self.killSelf()
                return True
        return False


game = Game()
