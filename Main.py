import configparser
import math  # Ceil's of numbers
import os  # Checking existence of config
import random  # Randomises enemy attributes
import time  # Making sure tings are based on time not loops
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
        global tk  # Used to kill and recreate
        self.game = gameIn
        self.x = tk.winfo_screenwidth()
        self.y = tk.winfo_screenheight() - 56
        self.offx = -7
        self.offy = 0
        self.windowCustomised = False
        self.updateWinValues(1)  # Init the remaining vars
        self.config = configparser.ConfigParser()
        tk.bind("<Escape>", self.handleClose)
        tk.bind("<Button-3>", self.setCustomised)  # Right click to end customisation
        if os.path.exists("config.ini"):
            try:
                self.readConfig(3)  # Record window vars, skim to make sure others are there
                self.updateWinValues(1)
                self.windowCustomised = True
                return
            except (configparser.NoOptionError, configparser.NoSectionError) as e:
                print(e)
                print("There was an error while reading the file, making a new file")
                os.remove("config.ini")
        canvas = Canvas(tk, width=self.x, height=self.y)
        canvas.pack()
        tk.geometry("+-7+0")
        menubar = Menu(tk)
        menubar.add_cascade(label="Menubar will be here")
        tk.config(menu=menubar)
        self.customiseWindow()  # Runs user customisation
        self.updateWinValues(1)
        self.updateConfig()
        canvas.destroy()
        tk.destroy()
        tk = Tk()  # Makes a new TK for the game to use

    def readConfig(self, what):
        self.config.read("config.ini")
        self.x = self.config.getint("window", "X")
        self.y = self.config.getint("window", "Y")
        self.offx = self.config.getint("window", "offX")
        self.offy = self.config.getint("window", "offY")
        if what == 2:  # Ran after window and classes are made
            if pygameInstalled:
                mixer.music.set_volume(self.config.getint("settings", "musicVolume") / 100)
                self.game.setEffectsVolume(self.config.getint("settings", "effectsVolume") / 100)
            background = self.config.get("settings", "backgroundColor")
            if background == "Rainbow":
                self.game.currColor = "Rainbow"
            else:
                self.game.setBackgroundColor(background, True)  # True to prevent rewrite of config
            self.game.enemyCtrl.moveLegs = self.config.getboolean("settings", "moveLegs")
            self.game.stopBetweenRounds = self.config.getboolean("settings", "stopBetweenRounds")
            # Will add records in a later update
            self.config.get("records", "name")
            self.config.getint("records", "score")
            self.config.getint("records", "round")
        else:  # read values but don't set, put to make sure no errors
            self.config.getint("settings", "musicVolume")
            self.config.getint("settings", "effectsVolume")
            self.config.get("settings", "backgroundColor")
            self.config.getboolean("settings", "moveLegs")
            self.config.getboolean("settings", "stopBetweenRounds")
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

    def updateConfig(self):  # Called when making a config and when anything in the config is changed
        self.config = configparser.ConfigParser()
        self.config.add_section("window")
        self.config.set("window", "X", str(round(self.ogX)))
        self.config.set("window", "Y", str(round(self.ogY)))
        self.config.set("window", "offX", str(round(self.offox)))
        self.config.set("window", "offY", str(round(self.offoy)))
        self.config.add_section("settings")
        if pygameInstalled and os.path.exists("config.ini"):
            self.config.set("settings", "musicVolume", str(math.ceil(mixer.music.get_volume() * 100)))
            self.config.set("settings", "effectsVolume", str(math.ceil(mixer.Sound.get_volume(
                self.game.enemyCtrl.shotSound) * 100)))
        else:
            self.config.set("settings", "musicVolume", str(100))
            self.config.set("settings", "effectsVolume", str(100))
        if os.path.exists("config.ini"):  # If we are making a new config, this prevents errors
            self.config.set("settings", "backgroundColor", self.game.currColor)
            self.config.set("settings", "moveLegs", str(self.game.enemyCtrl.moveLegs))
            self.config.set("settings", "stopBetweenRounds", str(self.game.stopBetweenRounds))
        else:
            self.config.set("settings", "backgroundColor", "Default")
            self.config.set("settings", "moveLegs", "True")
            self.config.set("settings", "stopBetweenRounds", "False")
        self.config.add_section("records")
        self.config.set("records", "name", "N/A")
        self.config.set("records", "score", "0")
        self.config.set("records", "round", "1")
        with open("config.ini", "w") as file:
            self.config.write(file)

    def shrinkWindow(self):
        if self.game.gameRunning:
            if self.y > 100:  # Keeps window at playable size
                self.y = self.ogY / self.game.ogHealth * self.game.health
            if self.x > 75:  # Keeps window at playable size
                self.x = self.ogX / self.game.ogHealth * self.game.health
            # The following prevents a 2 lined menubar
            if self.x <= 140 and not self.game.dispMenuHidden:
                self.game.menubar = Menu(tk)
                self.game.menubar.add_cascade(label="Game", menu=self.game.gameMenu)
                self.game.menubar.add_cascade(label="View", menu=self.game.dispMenu)
                self.game.menubar.add_cascade(label="S.", menu=self.game.shopMenu)
                tk.config(menu=self.game.menubar)
                self.game.dispMenuHidden = True
        else:  # Allows end screen to expand
            self.y = self.ogY / self.game.ogHealth * self.game.health
            self.x = self.ogX / self.game.ogHealth * self.game.health
        self.updateWinValues(2)  # Adjust window vars to shrink
        self.game.canvas.config(width=self.x, height=self.y)
        if self.x > 115:  # Keeps canvas centered
            tk.geometry('+' + str(self.offx) + '+' + str(self.offy))
        self.game.canvas.pack()

    def customiseButton(self):  # Ran if asked to resize from menubar
        self.game.gamePaused = True
        self.windowCustomised = False
        tk2 = Tk()  # Need new tk-keep the game alive
        tk2.title("Resize Window")
        menubar = Menu(tk2)
        menubar.add_cascade(label="Menubar will be here")
        tk2.config(menu=menubar)
        tk2canvas = Canvas(tk2, width=self.ogX, height=self.ogY)
        tk2.resizable(width=True, height=True)
        tk2canvas.pack()
        tk2.geometry('+' + str(self.offox) + '+' + str(self.offoy))
        tk2.bind("<Button-3>", self.setCustomised)  # Right click to end customisation
        changed = self.customiseWindow(tk2)
        tk2canvas.destroy()
        tk2.destroy()
        if changed:
            self.updateWinValues(1)  # Re-inits default values
            self.shrinkWindow()  # Adjusts window to new size
            self.game.updateLocations()
            self.updateConfig()
        self.game.waitForResize = False
        self.game.pauseGame()  # Unpauses game

    def setCustomised(self, *args):  # Hooks up to rightclick to exit customise window
        self.windowCustomised = True

    def customiseWindow(self, tk2=None):
        if tk2 is not None:  # If called from window
            result = simpledialog.messagebox.askokcancel("Window Size",
                                                         "Configure the window to the size you like it then right click on the window. NOTE: If you just tried to resize and you are seeing this again, your window must be taller in order for the game to run.")
        else:
            result = simpledialog.messagebox.askokcancel("Window Size",
                                                         "It appears to be your first time running on this device. Configure the window to the size you like it then right click on the window. NOTE: If you just tried to resize and you are seeing this again, your window must be taller in order for the game to run.")
        if not result:
            return False  # Don't customise if not ok
        while not self.windowCustomised:
            try:
                tk.update()
                if tk2 is not None:
                    tk2.update()
            except TclError as e:
                print(e)
                print("You have closed the window!")
                self.handleClose()
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
        if self.y < 61:  # Makes sure the game can run in this size
            self.windowCustomised = False
            self.customiseWindow(tk2)
        return True

    def handleClose(self, *args):
        try:
            tk.destroy()
        except TclError as e:
            print(e)
        if pygameInstalled:
            mixer.quit()
        sys.exit(0)


class Game:
    # Init some vars
    health = 200
    ogHealth = health
    lastHealth = health
    gameRunning = gamePaused = dispMenuHidden = waitForResize = stopBetweenRounds = lastMidRound = False
    clickChecked = midRound = True
    clickX = clickY = volumeSet = rainbowTime = points = 0
    menubar = shopMenu = dispMenu = gameMenu = rainbowOn = 0
    bullets = 6
    clipSize = 6
    refillTimer = 1.5
    rainbowList = ['#ff0000', '#ff3700', '#ff6a00', '#ffa200', '#ffd500', '#f2ff00', '#bfff00', '#88ff00',
                   '#55ff00', '#1eff00', '#00ff15', '#00ff4d', '#00ff80', '#00ffb7', '#00ffea', '#00ddff',
                   '#00aaff', '#0073ff', '#0040ff', '#0009ff', '#2b00ff', '#6200ff', '#9500ff', '#cc00ff',
                   '#ff00ff']
    currColor = "Default"

    def __init__(self):
        if pygameInstalled:
            mixer.init()
        # Get sizes then setup window
        self.window = WinSize(self)
        tk.title("Protect The Base!")
        self.canvas = Canvas(tk, width=self.window.x, height=self.window.y)
        tk.resizable(width=False, height=False)  # Window can't be resized
        self.canvas.pack()
        tk.geometry('+' + str(self.window.offx) + '+' + str(self.window.offy))
        self.defBackground = self.canvas["background"]
        self.enemyCtrl = EnemyCtrl(self, self.window)
        self.tower = Tower(self, self.window)
        self.infoManager = None  # Will be made after title screen
        self.waveNoticeText = self.canvas.create_text(self.window.midx, self.window.midy / 2, text='Wave #1',
                                                      font=('Helvetica', 20))
        self.canvas.itemconfigure(self.waveNoticeText, state="hidden")
        self.bindKeypressesAndMenu()
        self.window.readConfig(2)  # read rest of config
        self.titleScreen()  # Runs the title screen

    def bindKeypressesAndMenu(self):
        self.menubar = Menu(tk)
        self.gameMenu = Menu(tk, tearoff=0)  # Tearoff keeps menus from being able to detach
        if pygameInstalled:
            self.gameMenu.add_command(label="Set Volume %", command=self.changeVolume)
        self.gameMenu.add_command(label="Resize Max Sized Window", command=self.queueResize)
        self.gameMenu.add_command(label="Pause/Unpause Game", command=self.pauseGame)
        self.gameMenu.add_command(label="Toggle stop between rounds", command=self.toggleBetweenRoundsPause)
        self.gameMenu.add_command(label="Restart", command=lambda: restart(self))
        self.gameMenu.add_command(label="Quit", command=self.quit)
        self.dispMenu = Menu(tk, tearoff=0)
        self.dispMenu.add_command(label="Set Background Color", command=self.setBackgroundColor)
        self.dispMenu.add_command(label="Set Background Rainbow", command=self.setBackgroundRainbow)
        self.dispMenu.add_command(label="Toggle Enemy Leg Motion", command=self.enemyCtrl.toggleLegMotion)
        self.dispMenu.add_command(label="Toggle Information Window", command=self.toggleInfoWin)
        self.shopMenu = Menu(tk, tearoff=0)
        self.shopMenu.add_command(label="Clear All Enemies (30 Points)", command=self.enemyCtrl.killAllEnemies)
        self.menubar.add_cascade(label="Game", menu=self.gameMenu)
        self.menubar.add_cascade(label="View", menu=self.dispMenu)
        self.menubar.add_cascade(label="Shop", menu=self.shopMenu)
        tk.config(menu=self.menubar)
        tk.bind("<Button 1>", self.mouseClick)  # Left click
        tk.bind("<Button 3>", self.startReload)  # Right click
        tk.bind("<space>", self.startRound)
        tk.bind("<Escape>", self.stopGame)
        # These next 2 will probably be changed later
        tk.bind("q", self.enemyCtrl.killAllEnemies)
        tk.bind('p', self.pauseGame)
        tk.bind('e', lambda clickLoc=None: print('How dare you press the "e" key!'))

    def titleScreen(self):
        # Should eventually make text based on window size
        self.canvas.create_text(self.window.midx, self.window.midy - 200, text='Protect the base!',
                                font=('Helvetica', 35), tag="titleText")
        self.canvas.create_text(self.window.midx, self.window.midy - 140, text='Click anywhere to continue.',
                                font=('Helvetica', 20), tag="titleText")
        if pygameInstalled:
            # Title screen music
            mixer.music.load("Sounds/Background1.wav")
            mixer.music.play(-1)  # -1 means until new one or stopped
        if self.currColor == "Rainbow":
            self.handleRainbow()
        while self.clickChecked:
            try:
                tk.update()
            except TclError as e:
                print(e)
                print("You have closed the window!")
                self.quit()
        self.clickChecked = True
        self.infoManager = infoManager(self, self.window, self.enemyCtrl)
        if pygameInstalled:
            # Game music
            mixer.music.load("Sounds/Background2.wav")
            mixer.music.play(-1)
        self.gameRunning = True
        self.tower.startGame()
        self.canvas.delete("titleText")
        tk.update_idletasks()
        self.handleGame()

    def endScreen(self):
        self.infoManager.gameOver()
        self.tower.remove()
        self.enemyCtrl.killAllEnemies()
        if pygameInstalled:
            # End screen/Title screen music
            mixer.music.load("Sounds/Background1.wav")
            mixer.music.play(-1)
        t1 = self.canvas.create_text(self.window.midx, self.window.midy - 200, text='You Have Lost!',
                                     font=('Helvetica', 35))
        t2 = self.canvas.create_text(self.window.midx, self.window.midy - 140,
                                     text='You got to round %i.' % self.enemyCtrl.round, font=('Helvetica', 20))
        # Expand window to full size
        for self.health in range(0, self.ogHealth + 2, 2):
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
        except TclError as e:
            print(e)
            print("You have closed the window!")
            self.quit()

    def handleGame(self):
        while self.gameRunning:
            try:
                while self.gamePaused:
                    tk.update()
                self.enemyCtrl.handleEnemies()
                self.infoManager.updateItems()
                # Check if request to resize
                if self.waitForResize and (not self.midRound):
                    self.window.customiseButton()
                # Check if round over and show click space to continue, or show new round text
                if self.midRound != self.lastMidRound:
                    if not (self.stopBetweenRounds or self.midRound):
                        self.midRound = True
                    self.lastMidRound = self.midRound
                    if self.midRound:
                        self.canvas.itemconfig(self.waveNoticeText, text="Round #{0}".format(self.enemyCtrl.round + 1),
                                               state="normal")
                        self.canvas.coords(self.waveNoticeText, (self.window.midx, self.window.midy / 2))
                        self.bullets = self.clipSize
                        self.canvas.after(2000, lambda: self.canvas.itemconfigure(self.waveNoticeText, state="hidden"))
                        self.tower.showTower()
                        self.enemyCtrl.startRound()
                    else:
                        self.tower.hideTower()
                        self.canvas.itemconfig(self.waveNoticeText, text="Press space to start next round.",
                                               state="normal")
                        self.canvas.coords(self.waveNoticeText, (self.window.midx, self.window.midy / 2))
                # Check if need to resize
                if self.health != self.lastHealth:
                    self.lastHealth = self.health
                    self.window.shrinkWindow()
                    self.updateLocations()
                # Check if dead
                if self.health <= 0:
                    self.gameRunning = False
                    self.endScreen()
                tk.update()  # Update everything
            except TclError as e:  # handle closed window
                print(e)
                print("You have closed the window!")
                self.gameRunning = False
                self.quit()

    def setBackgroundRainbow(self):  # Menu sets rainbow
        if self.currColor == "Rainbow":
            self.setBackgroundColor("Default")
        else:
            self.currColor = "Rainbow"
            self.handleRainbow()

    def handleRainbow(self):  # Checks and updates rainbow
        if self.currColor == "Rainbow":
            self.setBackgroundColor(self.rainbowList[self.rainbowOn])
            self.rainbowOn += 1
            self.rainbowOn %= 25
            self.canvas.after(1000, self.handleRainbow)

    def pauseGame(self, *args):  # Pause/Unpause
        if self.gamePaused:
            self.gamePaused = False
            self.enemyCtrl.unpauseEnemies()
        else:
            self.gamePaused = True

    def updateLocations(self):  # Done after window shrink to move things properly
        self.tower.moveTower()
        self.enemyCtrl.winShrinkMove()

    def queueResize(self):
        if self.gameRunning:
            self.waitForResize = True
        else:
            self.window.customiseButton()

    def toggleInfoWin(self, *args):
        if self.gameRunning:
            self.infoManager.toggleWin()
            if len(args) == 0:
                self.enemyCtrl.unpauseEnemies()

    def toggleBetweenRoundsPause(self):
        self.stopBetweenRounds = not self.stopBetweenRounds
        self.window.updateConfig()
        self.enemyCtrl.unpauseEnemies()

    def startReload(self, *args):
        self.refillTimer = time.time() + 1.5
        self.bullets = 0
        if self.gameRunning:
            self.infoManager.reloading = True

    def startRound(self, *args):
        self.midRound = True

    def setBackgroundColor(self, colorIn=None, readingConfig=False):
        if colorIn is None:  # Called from menu
            color = colorchooser.askcolor()
        else:  # Called in code
            if colorIn == "Default":
                color = ["eh", None]
            else:
                color = ["eh", colorIn]
        if color[1] is None:
            self.canvas.configure(bg=self.defBackground)
            self.currColor = "Default"
        else:
            self.canvas.configure(bg=color[1])
            if self.currColor != "Rainbow" or colorIn is None:
                self.currColor = color[1]
        if not readingConfig:
            self.window.updateConfig()
        self.enemyCtrl.unpauseEnemies()
        tk.update_idletasks()

    def changeVolume(self):
        self.volumeSet = -1
        tk2 = Tk()  # Make window for volume controls
        canvas = Canvas(tk2, width=150, height=45)
        tk2.resizable(width=False, height=False)
        tk2.geometry('+' + str(int(self.window.midox)) + '+' + str(int(self.window.midoy)))
        canvas.pack()
        # Make volume controls
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
        while self.volumeSet == -1:  # set by button press command
            try:
                tk.update()
                tk2.update()
                if lastTv != tv.get():  # Master controls both
                    lastTv = tv.get()
                    ev.set(lastTv)
                    mv.set(lastTv)
            except TclError:
                self.volumeSet = -2
        if self.volumeSet != -2:  # -2 is closed, /100 to make 0-1
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

    def quit(self, restarting=False):  # Handles being quit
        try:
            if self.gameRunning:
                self.infoManager.gameOver()
            self.gameRunning = False
            self.enemyCtrl.killAllEnemies()
            self.canvas.destroy()
            tk.destroy()
        except TclError as e:
            print(e)
        if pygameInstalled:
            mixer.quit()
        if not restarting:
            sys.exit()


class infoManager:
    tk = windowAlive = canvas = healthbar = ammobar = waveText = pointsText = ammoText = None

    def __init__(self, gameIn, windowIn, enemyCtrlIn):
        self.game = gameIn
        self.window = windowIn
        self.enemyCtrl = enemyCtrlIn
        self.reloading = False
        self.makeWindow()
        self.makeItems()

    def makeWindow(self):
        self.windowAlive = True
        self.tk = Tk()
        self.tk.title("Info Window")
        self.canvas = Canvas(self.tk, width=200, height=160)
        self.tk.resizable(width=False, height=False)
        self.canvas.pack()
        self.tk.geometry('+' + str(self.window.ogX - 200 + self.window.offox) + '+' + str(self.window.offoy))
        self.tk.attributes("-topmost", "true")

    def makeItems(self):
        self.canvas.create_text(100, 15, text='Health:', font=('Helvetica', 15), tag="infoTxt")
        self.healthbar = self.canvas.create_rectangle(12, 32, 188, 48, fill="red", tag="infoTxt")
        self.canvas.create_rectangle(10, 30, 190, 50, tag="infoTxt")  # Healthbar outline
        self.waveText = self.canvas.create_text(100, 65, text='Wave #: 1', font=('Helvetica', 15), tag="infoTxt")
        self.pointsText = self.canvas.create_text(100, 95, text='Points: 0', font=('Helvetica', 15), tag="infoTxt")
        self.ammobar = self.canvas.create_rectangle(12, 112, 188, 128, fill="yellow", tag="infoTxt")
        self.canvas.create_rectangle(10, 110, 190, 130, tag="infoTxt")  # Ammobar outline
        self.ammoText = self.canvas.create_text(100, 145, text='Ammo: 0/0', font=('Helvetica', 15), tag="infoTxt")
        self.tk.update_idletasks()

    def toggleWin(self):
        if self.windowAlive:
            self.gameOver()
        else:
            self.makeWindow()
            self.makeItems()

    def updateItems(self):
        if self.windowAlive:
            try:
                newLen = self.game.health / self.game.ogHealth * 176  # 176 is max length
                newLen += 12
                self.canvas.coords(self.healthbar, 12, 32, newLen, 48)
                self.canvas.itemconfigure(self.waveText, text="Wave #: {0}".format(str(self.enemyCtrl.round)))
                self.canvas.itemconfigure(self.pointsText, text="Points: {0}".format(str(self.game.points)))
                if self.reloading:
                    times = time.time()
                    passed = 1.5 - (self.game.refillTimer - times)
                    self.canvas.itemconfigure(self.ammoText,
                                              text="Ammo: Reloading...".format(self.game.bullets, self.game.clipSize))
                    if passed > 1.5:
                        passed = 1.5
                        self.reloading = False
                        self.game.bullets = self.game.clipSize
                    newLen = passed / 1.5 * 176
                else:
                    newLen = self.game.bullets / self.game.clipSize * 176  # 176 is max length
                    self.canvas.itemconfigure(self.ammoText,
                                              text="Ammo: {0}/{1}".format(self.game.bullets, self.game.clipSize))
                newLen = round(newLen)
                if newLen == 0:
                    self.canvas.itemconfigure(self.ammobar, state="hidden")
                else:
                    self.canvas.itemconfigure(self.ammobar, state="normal")
                    newLen += 12
                    self.canvas.coords(self.ammobar, 12, 112, newLen, 128)
                self.tk.update_idletasks()
            except TclError:
                self.windowAlive = False

    def gameOver(self):
        self.canvas.delete("infoTxt")
        self.canvas.destroy()
        self.tk.destroy()


class Tower:

    def __init__(self, gamein, windowIn):
        self.game = gamein
        self.window = windowIn
        self.towerImg = PhotoImage(file='Images/towerImg.gif')
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

    def __init__(self, gamein, windowIn):
        self.game = gamein
        self.window = windowIn
        if pygameInstalled:
            # Make sound effects
            self.shotSound = mixer.Sound("Sounds/shot sound.wav")
            self.stepSound = mixer.Sound("Sounds/footstep.wav")  # Not used yet

    def startGame(self):
        self.startRound()

    def startRound(self):
        self.round += 1
        if self.round >= 10:  # generate level 1 and 2 enemies
            level = random.choices([1, 2], weights=[90, 10], k=4 + self.round)
        else:  # generate level 1 enemies
            level = [1] * (4 + self.round)
        for w in range(0, 4 + self.round):  # Make each enemy
            self.enemyIDs.append(Enemy(self, self.game, self.window, level[w]))

    def handleEnemies(self):
        # find some way the enemies move sound can be played ONLY WHILE MOVING, and at a reasonable interval
        [enemy.moveSelf() for enemy in self.enemyIDs]

    def unpauseEnemies(self):  # ran after finish of pause, resets timers
        [enemy.unpause() for enemy in self.enemyIDs]

    def toggleLegMotion(self):
        self.moveLegs = not self.moveLegs
        [enemy.toggleLegMotion() for enemy in self.enemyIDs]
        self.window.updateConfig()
        self.unpauseEnemies()

    def checkClickedLocation(self, clickX, clickY):
        if self.game.bullets <= 0 or not self.game.midRound:
            return  # if no bullets, or not in a round, no shoot
        self.game.bullets -= 1
        toDelete = []
        if pygameInstalled:
            mixer.Sound.play(self.shotSound)
        for enemy in range(len(self.enemyIDs)):
            killed = self.enemyIDs[enemy].checkClickedLocation(clickX, clickY)
            if killed:
                toDelete.append(enemy)
                self.game.points += 1
        for enemy in sorted(toDelete, reverse=True):
            del self.enemyIDs[enemy]  # Kill all killed enemies
        if len(self.enemyIDs) == 0:  # If all enemies killed
            self.game.points += 2
            self.game.midRound = False

    def killAllEnemies(self, *args):
        if self.game.gameRunning:  # used that way end screen can kill enemies
            if self.game.points >= 30:
                self.game.points -= 30
            else:
                print("That item is too expensive.")
                if len(args) == 0:  # Called from menu
                    self.unpauseEnemies()
                return
        for w in range(len(self.enemyIDs)):
            self.enemyIDs[0].killSelf()
            del self.enemyIDs[0]
        if self.game.gameRunning:
            if len(args) == 0:
                self.unpauseEnemies()
            self.game.midRound = False

    def winShrinkMove(self):
        [enemy.baseMove() for enemy in self.enemyIDs]


class Enemy:
    # Init Vars
    x = y = dispX = dispY = m = b = oldMove = lastMove = loopNum = 0
    disp = disp2 = disp3 = currDisp = spawnWall = lives = img1 = img2 = img3 = 2
    lastTime = timeForAnimate = timeToStop = time.time()

    def __init__(self, enemyCtrlIn, gameIn, windowIn, level):
        self.enemyCtrl = enemyCtrlIn
        self.game = gameIn
        self.window = windowIn
        self.level = level
        # PPS stands for Pixels Per Second
        self.speedPPS = (75 + 3 * (enemyCtrlIn.round + random.randint(100,
                                                                      100) / 10) / 1536 * self.window.ogX)
        self.moveLegs = enemyCtrlIn.moveLegs
        self.stopped = False
        # Make images of enemy
        self.setupImages(level)
        # Put enemy on screen
        self.spawnSelf()

    def setupImages(self, level):
        if level == 2:
            self.lives = 2
            self.speedPPS -= 9
            self.img1 = PhotoImage(file='Images/stick1L2.gif')
            self.img2 = PhotoImage(file='Images/stick2L2.gif')
            self.img3 = PhotoImage(file='Images/stick3L2.gif')
        else:
            self.lives = 1
            self.img1 = PhotoImage(file='Images/stick1.gif')
            self.img2 = PhotoImage(file='Images/stick2.gif')
            self.img3 = PhotoImage(file='Images/stick3.gif')

    def setupDisp(self):
        # Make first display
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
                if abs(self.window.midox - self.x) > 10:  # Can't spawn in middle
                    break
            # Note to past self... taking a ceiling of a fraction likely wasn't helping...
            # Adjust speed to make it the same as the others
            self.speedPPS *= abs(self.window.midox - self.x) / (self.window.midox - 30)
            if self.speedPPS < self.enemyCtrl.round:  # don't allow it to be too slow
                self.speedPPS = self.enemyCtrl.round
        elif self.spawnWall == 2:  # Bottom
            self.y = self.window.ogY - 30
            while True:
                self.x = random.randint(30, self.window.ogX - 30)
                if abs(self.window.midox - self.x) > 10:  # Can't spawn in middle
                    break
            # Adjust speed to make it the same as the others
            self.speedPPS *= abs(self.window.midox - self.x) / (self.window.midox - 30)
            if self.speedPPS < self.enemyCtrl.round:  # don't allow it to be too slow
                self.speedPPS = self.enemyCtrl.round
        elif self.spawnWall == 3:  # Left
            self.x = 30
            self.y = random.randint(30, self.window.ogY - 30)
        else:  # Right
            self.x = self.window.ogX - 30
            self.y = random.randint(30, self.window.ogY - 30)
        # Make line vars to middle
        self.m = (self.window.midoy - self.y) / (self.window.midox - self.x)
        self.b = self.window.midoy + self.m * self.window.midox
        # Make sure enemy doesn't go past tower
        self.timeToStop = time.time() + abs(self.x - self.window.midox) / self.speedPPS + .2  # .2 second buffer
        self.setupDisp()  # add pictures
        self.lastTime = time.time()

    def hideEnemy(self, toHide):
        self.game.canvas.itemconfigure(toHide, state='hidden')

    def showEnemy(self, toShow):
        self.game.canvas.itemconfigure(toShow, state='normal')

    def hitTargetPrep(self):  # run when hit tower
        self.stopped = True
        self.currDisp = 1
        self.swapCostume()
        self.lastTime = time.time()

    def swapCostume(self):  # make legs move
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
            # Check if hit tower
            if abs(self.window.midoy - self.y) > 50 or abs(self.window.midox - self.x) > 30:
                Time = time.time()
                # Change based on time
                if self.x > self.window.midox:
                    self.x -= self.speedPPS * (Time - self.lastTime)
                else:
                    self.x += self.speedPPS * (Time - self.lastTime)
                # use the line function to get y
                self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
                if self.moveLegs:
                    # figure out leg movements
                    animateTime = time.time()
                    if animateTime - self.timeForAnimate > .15:
                        self.swapCostume()
                        self.timeForAnimate = animateTime
                self.lastTime = Time
                self.baseMove()
                if self.timeToStop < Time:
                    # Went past tower, goto tower by calculating the lines
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
                    # Somehow skipped over tower then back
                    self.hitTargetPrep()
            else:
                self.hitTargetPrep()
        else:
            # Handle attack
            Time = time.time()
            if self.lastTime + 1 <= Time:
                self.game.health -= math.floor(Time - self.lastTime)
                self.lastTime = Time

    def baseMove(self):
        # Converts from max window size to current, then displays
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
        # Check if clicked on
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


def restart(gameIn):
    global game, tk
    if gameIn.window.windowCustomised:
        gameIn.quit(True)
        tk = Tk()
        game = Game()


if __name__ == "__main__":
    game = Game()
