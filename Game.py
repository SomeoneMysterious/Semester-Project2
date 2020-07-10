import random  # seed generation
import time  # Making sure tings are based on time not loops
from tkinter import *
from tkinter import colorchooser, simpledialog
import winSize
import infoWindow
import enemyCtrl

pygameInstalled = True
try:
    from pygame import mixer
except ModuleNotFoundError as er:
    print("Pygame not installed, required for audio, game will not use any audio.")
    pygameInstalled = False

class Game:
    # Init some vars
    health = 200
    ogHealth = lastHealth = health
    gameRunning = gamePaused = dispMenuHidden = waitForResize = stopBetweenRounds = lastMidRound = schoolFriendly = False
    clickChecked = midRound = shrinkWin = True
    clickX = clickY = volumeSet = rainbowTime = points = menubar = shopMenu = dispMenu = gameMenu = rainbowOn = 0
    bullets = clipSize = seedTxt = 6
    refillTimer = 1.5
    rainbowList = ['#ff0000', '#ff3700', '#ff6a00', '#ffa200', '#ffd500', '#f2ff00', '#bfff00', '#88ff00',
                   '#55ff00', '#1eff00', '#00ff15', '#00ff4d', '#00ff80', '#00ffb7', '#00ffea', '#00ddff',
                   '#00aaff', '#0073ff', '#0040ff', '#0009ff', '#2b00ff', '#6200ff', '#9500ff', '#cc00ff',
                   '#ff00ff']
    difficulties = []
    currColor = "Default"

    def __init__(self):
        self.tk = Tk()
        if pygameInstalled:
            mixer.init()
        self.difficulty = IntVar(self.tk, 2)
        # Get sizes then setup window
        self.window = winSize.WinSize(self)
        self.pygameInstalled = pygameInstalled
        self.tk.title("Protect The Base!")
        self.canvas = Canvas(self.tk, width=self.window.x, height=self.window.y)
        self.tk.resizable(width=False, height=False)  # Window can't be resized
        self.canvas.pack()
        self.tk.geometry('+' + str(self.window.offx) + '+' + str(self.window.offy))
        self.defBackground = self.canvas["background"]  # Sets defualt background for system compatibility
        self.enemyCtrl = enemyCtrl.EnemyCtrl(self, self.window)
        self.tower = Tower(self, self.window)
        self.infoManager = None  # Will be made after title screen
        self.waveNoticeText = self.canvas.create_text(self.window.midx, self.window.midy / 2, text='Wave #1',
                                                      font=('Helvetica', 20))
        self.canvas.itemconfigure(self.waveNoticeText, state="hidden")
        self.bindKeypressesAndMenu()
        self.window.readConfig(2)  # read rest of config
        self.seed = random.randrange(sys.maxsize)
        self.titleScreen()  # Runs the title screen

    def bindKeypressesAndMenu(self):
        self.menubar = Menu(self.tk)
        self.gameMenu = Menu(self.tk, tearoff=0)  # Tearoff keeps menus from being able to detach
        if pygameInstalled:
            self.gameMenu.add_command(label="Set Volume %", command=self.changeVolume)
        self.gameMenu.add_command(label="Resize Max Sized Window", command=self.queueResize)
        self.gameMenu.add_command(label="Pause/Unpause Game", command=self.pauseGame)
        self.gameMenu.add_command(label="Toggle stop between rounds", command=self.toggleBetweenRoundsPause)
        self.gameMenu.add_command(label="Restart", command=lambda: restart(self))
        self.gameMenu.add_command(label="Quit", command=self.quit)
        self.dispMenu = Menu(self.tk, tearoff=0)
        self.dispMenu.add_command(label="Set Background Color", command=self.setBackgroundColor)
        self.dispMenu.add_command(label="Set Background Rainbow", command=self.setBackgroundRainbow)
        self.dispMenu.add_command(label="Toggle Enemy Leg Motion", command=self.enemyCtrl.toggleLegMotion)
        self.dispMenu.add_command(label="Toggle Information Window", command=self.toggleInfoWin)
        self.shopMenu = Menu(self.tk)
        self.shopMenu.add_command(label="Clear All Enemies (30 Points)", command=self.enemyCtrl.killAllEnemies)
        self.shopMenu.add_command(label="Expand window (20s, 20 Points)", command=self.expandWindow)
        self.menubar.add_cascade(label="Game", menu=self.gameMenu)
        self.menubar.add_cascade(label="View", menu=self.dispMenu)
        self.menubar.add_cascade(label="Shop", menu=self.shopMenu)
        self.tk.config(menu=self.menubar)
        self.tk.bind("<Button 1>", self.mouseClick)  # Left click
        self.tk.bind("<Button 3>", self.startReload)  # Right click
        self.tk.bind("<space>", self.startRound)
        self.tk.bind("<Escape>", self.stopGame)
        # These next 2 will probably be changed later
        self.tk.bind("q", self.enemyCtrl.killAllEnemies)
        self.tk.bind('p', self.pauseGame)
        self.tk.bind('e', self.easterEgg)

    def titleScreen(self):
        # Should eventually make text based on window size
        self.canvas.create_text(self.window.midx, self.window.midy - 200, text='Protect the base!',
                                font=('Helvetica', 35), tag="titleItem")
        self.canvas.create_text(self.window.midx, self.window.midy - 140, text='Right click anywhere to continue.',
                                font=('Helvetica', 20), tag="titleItem")
        seedBtn = Button(self.tk, text="Set Game Seed", command=self.setSeed)
        seedBtn.pack()
        seedBtn.place(x=self.window.midx, y=self.window.midy - 110, anchor=CENTER)
        self.seedTxt = self.canvas.create_text(self.window.midx, self.window.midy - 85,
                                        text='Current Seed: ' + str(self.seed), font=('Helvetica', 15), tag="titleItem")
        self.canvas.create_text(self.window.midx, self.window.midy - 60, text='Difficulty:',
                                font=('Helvetica', 15), tag="titleItem")
        options = {"Easy": 1, "Medium": 2, "Hard": 3, "Impossible": 4}
        for (text, value) in options.items():
            self.difficulties.append(Radiobutton(self.tk, text=text, variable=self.difficulty, value=value))
            self.difficulties[value - 1].pack()
            self.difficulties[value - 1].place(x=self.window.midx - 40, y=self.window.midy - 70 + 20 * value)
        if pygameInstalled:
            # Title screen music
            mixer.music.load("Sounds/Background1.wav")
            mixer.music.play(-1)  # -1 means until new one or stopped
        if self.currColor == "Rainbow":
            self.handleRainbow()
        elif self.currColor != "Default":
            [item.config(bg=self.currColor) for item in self.difficulties]
        while self.clickChecked:
            try:
                self.tk.update()
            except TclError as e:
                print(e)
                print("You have closed the window!")
                self.quit()
        self.clickChecked = True
        self.infoManager = infoWindow.infoManager(self, self.window, self.enemyCtrl)
        if pygameInstalled:
            # Game music
            mixer.music.load("Sounds/Background2.wav")
            mixer.music.play(-1)
        self.canvas.delete("titleItem")
        [item.destroy() for item in self.difficulties]
        self.difficulties = []
        seedBtn.destroy()
        random.seed(self.seed)
        print("The seed for this game was: " + str(self.seed))
        self.gameRunning = True
        self.tower.startGame()
        self.tk.update_idletasks()
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
        for x in range(0, 101):
            self.window.shrinkWindow(x / 100)
            if self.window.x > 140 and self.dispMenuHidden:
                self.menubar = Menu(self.tk)
                self.menubar.add_cascade(label="Game", menu=self.gameMenu)
                self.menubar.add_cascade(label="View", menu=self.dispMenu)
                self.menubar.add_cascade(label="Shop", menu=self.shopMenu)
                self.tk.config(menu=self.menubar)
                self.dispMenuHidden = False
            self.canvas.coords(t1, (self.window.midx, self.window.midy - 200))
            self.canvas.coords(t2, (self.window.midx, self.window.midy - 140))
            self.tk.update()
        try:
            while True:
                self.tk.update()
        except TclError as e:
            print(e)
            print("You have closed the window!")
            self.quit()

    def handleGame(self):
        while self.gameRunning:
            try:
                while self.gamePaused:
                    self.tk.update()
                self.enemyCtrl.handleEnemies()
                self.enemyCtrl.handleBullets()
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
                        self.enemyCtrl.roundCleanup()
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
                    if self.shrinkWin:
                        self.window.shrinkWindow()
                        self.updateLocations()
                # Check if dead
                if self.health <= 0:
                    self.gameRunning = False
                    self.endScreen()
                self.tk.update()  # Update everything
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
            self.infoManager.displayInfo("Window will be resized after",  "this round is completed.")
        else:
            self.window.customiseButton()

    def setSeed(self):
        seed = simpledialog.askinteger("Pick Seed", "Please put in a seed to replicate the randomness in the game.")
        if seed is not None:
            self.seed = seed
            self.canvas.itemconfigure(self.seedTxt, text='Current Seed: ' + str(seed))

    def toggleInfoWin(self, *args):
        if self.gameRunning:
            self.infoManager.toggleWin()
            if len(args) == 0:
                self.enemyCtrl.unpauseEnemies()

    def toggleBetweenRoundsPause(self):
        self.stopBetweenRounds = not self.stopBetweenRounds
        self.window.updateConfig()
        self.enemyCtrl.unpauseEnemies()

    def easterEgg(self, *args):
        print('How DARE you press the "e" key!')
        if self.gameRunning:
            self.infoManager.displayInfo('How DARE you press the "e" key!')

    # Commence shop items
    def expandWindow(self, *args):
        if self.points < 20:
            print("That item is too expensive.")
            self.infoManager.displayInfo("That item is too expensive.")
            return
        self.points -= 20
        self.shrinkWin = False
        self.window.shrinkWindow(1)  # sets window to full size
        self.updateLocations()
        self.tk.after(20000, self.stopExpandWindow)  # Currently for 20 secs

    def stopExpandWindow(self):
        self.shrinkWin = True
        if self.gameRunning:
            self.window.shrinkWindow()
            self.updateLocations()

    def startReload(self, clickloc):
        if self.gameRunning:
            self.refillTimer = time.time() + 1.5
            self.bullets = 0
            self.infoManager.reloading = True
        else:
            self.clickChecked = False
            self.clickX = clickloc.x
            self.clickY = clickloc.y

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
            if len(self.difficulties) != 0:
                [item.config(bg=self.defBackground) for item in self.difficulties]
            self.currColor = "Default"
        else:
            self.canvas.configure(bg=color[1])
            if len(self.difficulties) != 0:
                [item.config(bg=color[1]) for item in self.difficulties]
            if self.currColor != "Rainbow" or colorIn is None:
                self.currColor = color[1]
        if not readingConfig:
            self.window.updateConfig()
        self.enemyCtrl.unpauseEnemies()
        self.tk.update_idletasks()

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
                self.tk.update()
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

    def stopGame(self, *args):
        if self.gameRunning:
            self.gameRunning = False
        self.tk.destroy()

    def quit(self, restarting=False):  # Handles being quit
        try:
            if self.gameRunning:
                self.infoManager.gameOver()
            self.gameRunning = False
            self.enemyCtrl.killAllEnemies()
            self.canvas.destroy()
            self.tk.destroy()
        except TclError as e:
            print(e)
        if pygameInstalled:
            mixer.quit()
        if not restarting:
            sys.exit()


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


def restart(gameIn):
    global game
    if gameIn.window.windowCustomised:
        gameIn.quit(True)
        gameIn.tk = Tk()
        game = Game()


if __name__ == "__main__":
    game = Game()
