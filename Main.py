import configparser
import math
import os
import random
import time
from tkinter import *
from tkinter import colorchooser, simpledialog

pygameInstalled = True
try:
    from pygame import mixer
except ModuleNotFoundError as er:
    print("Pygame not installed, required for audio, game will not use any audio.")
    pygameInstalled = False

tk = Tk()


class WinSize:
    ogX = ogY = midx = midy = midox = midoy = offox = offoy = 0  # Init Vars

    def __init__(self, gameIn):
        global tk
        self.game = gameIn
        self.x = tk.winfo_screenwidth()
        self.y = tk.winfo_screenheight() - 56
        self.offx = -7
        self.offy = 0
        self.windowCustomised = False
        self.updateWinValues(1)  # Init the remaining vars
        self.config = configparser.ConfigParser()
        tk.bind("<Escape>", self.game.quit)
        tk.bind("<Button-3>", self.setCustomised)
        if os.path.exists("config.ini"):
            try:
                self.readConfig(1)
                self.updateWinValues(1)
                return
            except configparser.Error:
                print("There was an error while reading the file, making a new file")
                os.remove("config.ini")
        canvas = Canvas(tk, width=self.x, height=self.y)
        canvas.pack()
        tk.geometry("+-7+0")
        menubar = Menu(tk)
        menubar.add_cascade(label="Menubar will be here")
        tk.config(menu=menubar)
        self.customiseWindow()
        self.updateWinValues(1)
        self.updateConfig()
        canvas.destroy()
        tk.destroy()
        tk = Tk()

    def readConfig(self, what):
        self.config.read("config.ini")
        self.x = self.config.getint("window", "X")
        self.y = self.config.getint("window", "Y")
        self.offx = self.config.getint("window", "offX")
        self.offy = self.config.getint("window", "offY")
        if what == 2:
            if pygameInstalled:
                mixer.music.set_volume(self.config.getint("settings", "musicVolume") / 100)
                self.game.setEffectsVolume(self.config.getint("settings", "effectsVolume") / 100)
            background = self.config.get("settings", "backgroundColor")
            if background == "Rainbow":
                self.game.currColor = "Rainbow"
            else:
                self.game.setBackgroundColor(background)
            self.game.enemyCtrl.moveLegs = self.config.getboolean("settings", "moveLegs")
            # Will add records in a later update
            self.config.get("records", "name")
            self.config.getint("records", "score")
            self.config.getint("records", "round")

    def updateWinValues(self, setting):
        self.midx = self.x / 2
        self.midy = self.y / 2
        if setting == 1:  # Setup setting
            self.ogX = self.x
            self.ogY = self.y
            self.midox = self.midx
            self.midoy = self.midy
            self.offox = self.offx
            self.offoy = self.offy
        elif setting == 2:  # Window shrink setting
            self.offx = int(self.midox - self.midx) + self.offox
            self.offy = int(self.midoy - self.midy) + self.offoy

    def updateConfig(self):
        self.config = configparser.ConfigParser()
        self.config.add_section("window")
        self.config.set("window", "X", str(round(self.ogX)))
        self.config.set("window", "Y", str(round(self.ogY)))
        self.config.set("window", "offX", str(round(self.offox)))
        self.config.set("window", "offY", str(round(self.offoy)))
        self.config.add_section("settings")
        if pygameInstalled and os.path.exists("config.ini"):
            self.config.set("settings", "musicVolume", str(math.ceil(mixer.music.get_volume() * 100)))
            self.config.set("settings", "effectsVolume", str(math.ceil(mixer.Sound.get_volume(self.game.enemyCtrl.shotSound) * 100)))
        else:
            self.config.set("settings", "musicVolume", str(100))
            self.config.set("settings", "effectsVolume", str(100))
        if os.path.exists("config.ini"):
            self.config.set("settings", "backgroundColor", self.game.currColor)
            self.config.set("settings", "moveLegs", str(self.game.enemyCtrl.moveLegs))
        else:
            self.config.set("settings", "backgroundColor", "Default")
            self.config.set("settings", "moveLegs", "True")
        self.config.add_section("records")
        self.config.set("records", "name", "N/A")
        self.config.set("records", "score", str(0))
        self.config.set("records", "round", str(1))
        with open("config.ini", "w") as file:
            self.config.write(file)

    def shrinkWindow(self):
        if self.game.gameRunning:
            if self.y > 100:
                self.y = self.ogY / self.game.ogHealth * self.game.health
            if self.x > 75:
                self.x = self.ogX / self.game.ogHealth * self.game.health
            if self.x <= 140 and not self.game.dispMenuHidden:
                self.game.menubar = Menu(tk)
                self.game.menubar.add_cascade(label="Game", menu=self.game.gameMenu)
                self.game.menubar.add_cascade(label="Shop", menu=self.game.shopMenu)
                tk.config(menu=self.game.menubar)
                self.game.dispMenuHidden = True
        else:
            self.y = self.ogY / self.game.ogHealth * self.game.health
            self.x = self.ogX / self.game.ogHealth * self.game.health
        self.updateWinValues(2)
        self.game.canvas.config(width=self.x, height=self.y)
        if self.x > 115:
            tk.geometry('+' + str(self.offx) + '+' + str(self.offy))
        self.game.canvas.pack()

    def customiseButton(self):
        self.game.gamePaused = True
        self.windowCustomised = False
        tk2 = Tk()
        tk2.title("Resize Window")
        menubar = Menu(tk2)
        menubar.add_cascade(label="Menubar will be here")
        tk2.config(menu=menubar)
        tk2canvas = Canvas(tk2, width=self.x, height=self.y)
        tk2.resizable(width=True, height=True)
        tk2canvas.pack()
        tk2.geometry('+' + str(self.offx) + '+' + str(self.offy))
        tk2.bind("<Button-3>", self.setCustomised)
        self.customiseWindow(tk2)
        tk2canvas.destroy()
        tk2.destroy()
        self.updateWinValues(1)
        self.shrinkWindow()
        self.game.updateLocations()
        self.updateConfig()
        self.game.waitForResize = False
        self.game.pauseGame()

    def setCustomised(self, *args):
        self.windowCustomised = True

    def customiseWindow(self, tk2=None):
        if tk2 is not None:
            result = simpledialog.messagebox.askokcancel("Window Size", "Configure the window to the size you like it then right click on the window. NOTE: If you just tried to resize and you are seeing this again, your window must be taller in order for the game to run.")
        else:
            result = simpledialog.messagebox.askokcancel("Window Size", "It appears to be your first time running on this device. Configure the window to the size you like it then right click on the window. NOTE: If you just tried to resize and you are seeing this again, your window must be taller in order for the game to run.")
        if not result:
            return
        while not self.windowCustomised:
            try:
                tk.update()
                if tk2 is not None:
                    tk2.update()
                    if self.game.currColor == "Rainbow":
                        self.game.handleRainbow()
            except TclError as e:
                print(e)
                print("You have closed the window!")
                self.game.quit()
        if tk2 is not None:
            winfo = tk2.geometry()
        else:
            winfo = tk.geometry()
        winfo = winfo.replace("x", "+")
        winfo = winfo.split("+")
        self.x = int(winfo[0])
        self.y = int(winfo[1])
        self.offx = int(winfo[2])
        self.offy = int(winfo[3])
        if self.y < 61:
            self.windowCustomised = False
            self.customiseWindow(tk2)


class Game:
    health = 200
    ogHealth = health
    lastHealth = health
    gameRunning = False
    gamePaused = False
    points = 0
    dispMenuHidden = False
    waitForResize = False

    def __init__(self):
        if pygameInstalled:
            mixer.init()
        self.window = WinSize(self)
        tk.title("Protect The Base!")
        self.canvas = Canvas(tk, width=self.window.x, height=self.window.y)
        tk.resizable(width=False, height=False)
        self.canvas.pack()
        tk.geometry('+' + str(self.window.offx) + '+' + str(self.window.offy))
        self.clickChecked = True
        self.clickX = self.clickY = self.volumeSet = self.rainbowTime = 0
        self.menubar = self.shopMenu = self.dispMenu = self.gameMenu = self.rainbowOn = 0
        self.rainbowList = ['#ff0000', '#ff3700', '#ff6a00', '#ffa200', '#ffd500', '#f2ff00', '#bfff00', '#88ff00', '#55ff00', '#1eff00', '#00ff15', '#00ff4d', '#00ff80', '#00ffb7', '#00ffea', '#00ddff', '#00aaff', '#0073ff', '#0040ff', '#0009ff', '#2b00ff', '#6200ff', '#9500ff', '#cc00ff', '#ff00ff']
        self.currColor = "Default"
        self.enemyCtrl = EnemyCtrl(self, self.window)
        self.tower = Tower(self, self.window)
        self.bindKeypressesAndMenu()
        self.window.readConfig(2)  # read rest of config
        self.titleScreen()

    def bindKeypressesAndMenu(self):
        self.menubar = Menu(tk)
        self.gameMenu = Menu(tk, tearoff=0)
        if pygameInstalled:
            self.gameMenu.add_command(label="Set Volume %", command=self.changeVolume)
        self.gameMenu.add_command(label="Resize Max Sized Window", command=self.queueResize)
        self.gameMenu.add_command(label="Pause/Unpause Game", command=self.pauseGame)
        # This comment is is memory of an attempt at a restart. I may try that again, it depends.
        self.gameMenu.add_command(label="Quit", command=self.quit)
        self.dispMenu = Menu(tk, tearoff=0)
        self.dispMenu.add_command(label="Set Background Color", command=self.setBackgroundColor)
        self.dispMenu.add_command(label="Set Background Rainbow", command=self.setBackgroundRainbow)
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
        self.canvas.create_text(self.window.midx, self.window.midy - 200, text='Protect the base!', font=('Helvetica', 35), tag="titleText")
        self.canvas.create_text(self.window.midx, self.window.midy - 140, text='Click anywhere to continue.', font=('Helvetica', 20), tag="titleText")
        if pygameInstalled:
            mixer.music.load("Sounds/Background1.wav")
            mixer.music.play(-1)
        while self.clickChecked:
            try:
                tk.update()
                if self.currColor == "Rainbow":
                    self.handleRainbow()
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
        self.tower.remove()
        self.enemyCtrl.killAllEnemies()
        if pygameInstalled:
            mixer.music.load("Sounds/Background1.wav")
            mixer.music.play(-1)
        t1 = self.canvas.create_text(self.window.midx, self.window.midy - 200, text='You Have Lost!', font=('Helvetica', 35))
        t2 = self.canvas.create_text(self.window.midx, self.window.midy - 140, text='You got to round %i.' % self.enemyCtrl.round, font=('Helvetica', 20))
        for self.health in range(0, self.ogHealth+2, 2):
            self.window.shrinkWindow()
            if self.window.x > 140 and self.dispMenuHidden:
                self.menubar = Menu(tk)
                self.menubar.add_cascade(label="Game", menu=self.gameMenu)
                self.menubar.add_cascade(label="View", menu=self.dispMenu)
                self.menubar.add_cascade(label="Shop", menu=self.shopMenu)
                tk.config(menu=self.menubar)
                self.dispMenuHidden = False
            self.canvas.coords(t1, (self.window.midx, self.window.midy - 200))
            self.canvas.coords(t2, (self.window.midx, self.window.midy - 140))
            tk.update()
        try:
            while True:
                tk.update()
                if self.currColor == "Rainbow":
                    self.handleRainbow()
        except TclError as e:
            print(e)
            print("You have closed the window!")
            self.quit()

    def handleGame(self):
        while self.gameRunning:
            try:
                while self.gamePaused:
                    tk.update()
                    if self.currColor == "Rainbow":
                        self.handleRainbow()
                self.enemyCtrl.handleEnemies()
                if self.health != self.lastHealth:
                    self.lastHealth = self.health
                    self.window.shrinkWindow()
                    self.updateLocations()
                if self.health <= 0:
                    self.gameRunning = False
                    self.endScreen()
                tk.update()
                if self.currColor == "Rainbow":
                    self.handleRainbow()
            except TclError as e:
                print(e)
                print("You have closed the window!")
                self.gameRunning = False
                self.quit()

    def setBackgroundRainbow(self):
        if self.currColor == "Rainbow":
            self.setBackgroundColor("Default")
        else:
            self.currColor = "Rainbow"

    def handleRainbow(self):
        times = time.time()
        if self.rainbowTime <= times:
            self.setBackgroundColor(self.rainbowList[self.rainbowOn])
            self.rainbowOn += 1
            self.rainbowTime = times + 1.012417  # don't question this number, it fixes a weird bug
            self.rainbowOn %= 25

    def pauseGame(self, *args):
        if self.gamePaused:
            self.gamePaused = False
            self.enemyCtrl.unpauseEnemies()
        else:
            self.gamePaused = True

    def updateLocations(self):
        self.tower.moveTower()
        self.enemyCtrl.winShrinkMove()

    def queueResize(self):
        if self.gameRunning:
            self.waitForResize = True
        else:
            self.window.customiseButton()

    def setBackgroundColor(self, colorIn=None):
        if colorIn is None:
            color = colorchooser.askcolor()
        else:
            if colorIn == "Default":
                color = ["eh", None]
            else:
                color = ["eh", colorIn]
        if color[1] is None:
            self.canvas.configure(bg='SystemButtonFace')
            self.currColor = "Default"
        else:
            self.canvas.configure(bg=color[1])
            if self.currColor != "Rainbow" or colorIn is None:
                self.currColor = color[1]
        self.window.updateConfig()
        self.enemyCtrl.unpauseEnemies()

    def changeVolume(self):
        self.volumeSet = -1
        tk2 = Tk()
        canvas = Canvas(tk2, width=150, height=45)
        tk2.resizable(width=False, height=False)
        tk2.geometry('+' + str(int(self.window.midox)) + '+' + str(int(self.window.midoy)))
        canvas.pack()
        mv = Scale(tk2, from_=0, to=100, orient=HORIZONTAL, label="Music Volume %")
        mv.set(mixer.music.get_volume() * 100)
        mv.pack()
        ev = Scale(tk2, from_=0, to=100, orient=HORIZONTAL, label="Effects Volume %")
        ev.set(mixer.Sound.get_volume(self.enemyCtrl.shotSound) * 100)
        ev.pack()
        tv = Scale(tk2, from_=0, to=100, orient=HORIZONTAL, label="Master Volume %")
        tv.set(mixer.music.get_volume() * 100)
        tv.pack()
        Button(tk2, text='Set', command=self.setVolume).pack()
        lastTv = tv.get()
        while self.volumeSet == -1:
            try:
                tk.update()
                tk2.update()
                if self.currColor == "Rainbow":
                    self.handleRainbow()
                if lastTv != tv.get():
                    lastTv = tv.get()
                    ev.set(lastTv)
                    mv.set(lastTv)
                time.sleep(.05)
            except TclError:
                self.volumeSet = -2
        if self.volumeSet != -2:
            mixer.music.set_volume(mv.get() / 100)
            self.setEffectsVolume(ev.get() / 100)
            self.window.updateConfig()
        try:
            tk2.destroy()
        except TclError:
            pass
        self.enemyCtrl.unpauseEnemies()

    def setVolume(self):
        self.volumeSet = 0

    def setEffectsVolume(self, volume):  # volume must be a float from 0 to 1 inclusive
        mixer.Sound.set_volume(self.enemyCtrl.stepSound, volume)
        mixer.Sound.set_volume(self.enemyCtrl.shotSound, volume)

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
            self.canvas.destroy()
            tk.destroy()
        except TclError as e:
            print(e)
        sys.exit()


class Tower:

    def __init__(self, gamein, windowin):
        self.game = gamein
        self.window = windowin
        self.towerImg = PhotoImage(file='Images\\towerImg.gif')
        self.tower = self.game.canvas.create_image(self.window.midx, self.window.midy, image=self.towerImg)
        self.hideTower()

    def moveTower(self):
        self.game.canvas.coords(self.tower, (self.window.midx, self.window.midy))

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

    def __init__(self, gamein, windowin):
        self.game = gamein
        self.window = windowin
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
            self.enemyIDs.append(Enemy(self, self.game, self.window, level[w]))

    def handleEnemies(self):
        self.moveEnemies()

    def moveEnemies(self):
        # find some way the enemies move sound can be played ONLY WHILE MOVING, and at a reasonable interval
        for w in range(-1, len(self.enemyIDs) - 1):
            self.enemyIDs[w].moveSelf()

    def unpauseEnemies(self):
        for w in range(-1, len(self.enemyIDs) - 1):
            self.enemyIDs[w].unpause()

    def toggleLegMotion(self):
        self.moveLegs = not self.moveLegs
        for w in range(-1, len(self.enemyIDs) - 1):
            self.enemyIDs[w].toggleLegMotion()
        self.window.updateConfig()
        self.unpauseEnemies()

    def checkClickedLocation(self, clickX, clickY):
        # add limit of number of bullets in future update
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
            if self.game.waitForResize:
                self.window.customiseButton()
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
            if self.game.waitForResize:
                self.window.customiseButton()
            self.startRound()

    def winShrinkMove(self):
        for w in range(-1, len(self.enemyIDs) - 1):
            self.enemyIDs[w].baseMove()


class Enemy:
    x = y = dispX = dispY = m = b = oldMove = lastMove = loopNum = 0
    disp = disp2 = disp3 = currDisp = spawnWall = lives = img1 = img2 = img3 = 2
    lastTime = timeForAnimate = timeToStop = time.time()

    def __init__(self, enemyCtrlIn, gameIn, windowIn, level):
        self.enemyCtrl = enemyCtrlIn
        self.game = gameIn
        self.window = windowIn
        self.level = level
        self.speedPPS = (75 + 3 * (enemyCtrlIn.round + random.randint(0, 0) / 10) / 1536 * self.window.ogX)  # PPS stands for Pixels Per Second
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
        self.dispX = self.x - self.window.offx
        self.dispY = self.y - self.window.offy
        self.disp = self.game.canvas.create_image(self.dispX, self.dispY, image=self.img1)
        self.disp2 = self.game.canvas.create_image(self.dispX, self.dispY, image=self.img2)
        self.disp3 = self.game.canvas.create_image(self.dispX, self.dispY, image=self.img3)
        self.hideEnemy(self.disp)
        self.hideEnemy(self.disp3)

    def spawnSelf(self):
        # Base Screen must be bigger than 30 for any direction or this will break
        self.spawnWall = random.randint(1, 4)
        if self.spawnWall == 1:  # Top
            self.y = 30
            while True:
                self.x = random.randint(30, self.window.ogX - 30)
                if abs(self.window.midox - self.x) > 10:
                    break
            # Note to past self... taking a ceiling of a fraction likely wasn't helping...
            self.speedPPS *= abs(self.window.midox - self.x) / (self.window.midox - 30)
            if self.speedPPS < self.enemyCtrl.round:
                self.speedPPS = self.enemyCtrl.round
        elif self.spawnWall == 2:  # Bottom
            self.y = self.window.ogY - 30
            while True:
                self.x = random.randint(30, self.window.ogX - 30)
                if abs(self.window.midox - self.x) > 10:
                    break
            self.speedPPS *= abs(self.window.midox - self.x) / (self.window.midox - 30)
            if self.speedPPS < self.enemyCtrl.round:
                self.speedPPS = self.enemyCtrl.round
        elif self.spawnWall == 3:  # Left
            self.x = 30
            self.y = random.randint(30, self.window.ogY - 30)
        else:  # Right
            self.x = self.window.ogX - 30
            self.y = random.randint(30, self.window.ogY - 30)
        self.m = (self.window.midoy - self.y) / (self.window.midox - self.x)
        self.b = self.window.midoy + self.m * self.window.midox
        self.timeToStop = time.time() + abs(self.x - self.window.midox) / self.speedPPS + .2  # .2 second buffer
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
            if abs(self.window.midoy - self.y) > 50 or abs(self.window.midox - self.x) > 30:
                Time = time.time()
                if self.x > self.window.midox:
                    self.x -= self.speedPPS * (Time - self.lastTime)
                else:
                    self.x += self.speedPPS * (Time - self.lastTime)
                self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
                if self.moveLegs:
                    animateTime = time.time()
                    if animateTime - self.timeForAnimate > .15:
                        self.swapCostume()
                        self.timeForAnimate = animateTime
                self.lastTime = Time
                self.baseMove()
                if self.timeToStop < Time:
                    if self.spawnWall == 1:
                        self.y = self.window.midoy - 50
                        self.x = abs((-1 * self.y - self.b + self.window.ogY) / self.m)
                        if self.window.midox - self.x < -27:
                            self.x = self.window.midox - 27
                            self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
                        elif self.window.midox - self.x > 27:
                            self.x = self.window.midox + 27
                            self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
                    elif self.spawnWall == 2:
                        self.y = self.window.midoy + 50
                        self.x = abs((-1 * self.y - self.b + self.window.ogY) / self.m)
                        if self.window.midox - self.x < -27:
                            self.x = self.window.midox - 27
                            self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
                        elif self.window.midox - self.x > 27:
                            self.x = self.window.midox + 27
                            self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
                    elif self.spawnWall == 3:
                        self.x = self.window.midox - 27
                        self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
                    else:
                        self.x = self.window.midox + 27
                        self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
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
        self.dispX = self.x - self.window.offx + self.window.offox
        self.dispY = self.y - self.window.offy + self.window.offoy
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
