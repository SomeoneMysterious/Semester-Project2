import configparser
import math  # Ceil's of numbers
import os  # Checking existence of config
from tkinter import *
from tkinter import simpledialog

pygameInstalled = True
try:
    from pygame import mixer
except ModuleNotFoundError as er:
    print("Pygame not installed, required for audio, game will not use any audio.")
    pygameInstalled = False


class WinSize:
    ogX = ogY = midx = midy = midox = midoy = offox = offoy = 0  # Init Vars

    def __init__(self, gameIn):
        self.game = gameIn
        self.x = self.game.tk.winfo_screenwidth()
        self.y = self.game.tk.winfo_screenheight() - 56
        self.offx = -7
        self.offy = 0
        self.windowCustomised = False
        self.updateWinValues(1)  # Init the remaining vars
        self.config = configparser.ConfigParser()
        self.game.tk.bind("<Escape>", self.handleClose)
        self.game.tk.bind("<Button-3>", self.setCustomised)  # Right click to end customisation
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
        canvas = Canvas(self.game.tk, width=self.x, height=self.y)
        canvas.pack()
        self.game.tk.geometry("+-7+0")
        menubar = Menu(self.game.tk)
        menubar.add_cascade(label="Menubar will be here")
        self.game.tk.config(menu=menubar)
        self.customiseWindow()  # Runs user customisation
        self.updateWinValues(1)
        self.updateConfig()
        canvas.destroy()
        self.game.tk.destroy()
        self.game.tk = Tk()  # Makes a new TK for the game to use

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
            self.game.difficulty.set(self.config.getint("settings", "difficulty"))
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
            self.config.getint("settings", "difficulty")
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

    def updateConfig(self):  # Called when making a config and when we aren't sure what might have changed
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
        if os.path.exists("config.ini"):  # If we aren't making a new config
            self.config.set("settings", "backgroundColor", self.game.currColor)
            self.config.set("settings", "moveLegs", str(self.game.enemyCtrl.moveLegs))
            self.config.set("settings", "stopBetweenRounds", str(self.game.stopBetweenRounds))
            self.config.set("settings", "difficulty", str(self.game.difficulty.get()))
        else:  # If the config is new, prevent reading non-set values
            self.config.set("settings", "backgroundColor", "Default")
            self.config.set("settings", "moveLegs", "True")
            self.config.set("settings", "stopBetweenRounds", "False")
            self.config.set("settings", "difficulty", "2")
        self.config.add_section("records")
        self.config.set("records", "name", "N/A")
        self.config.set("records", "score", "0")
        self.config.set("records", "round", "1")
        with open("config.ini", "w") as file:
            self.config.write(file)

    def editConfig(self, section, item, value):
        self.config[section][item] = str(value)
        with open("config.ini", "w") as file:
            self.config.write(file)

    def shrinkWindow(self, setPercent=None):
        if setPercent is None:
            if self.y > 100:  # Keeps window at playable size
                self.y = self.ogY / self.game.ogHealth * self.game.health
            if self.x > 75:  # Keeps window at playable size
                self.x = self.ogX / self.game.ogHealth * self.game.health
            # The following prevents a 2 lined menubar
            if self.x <= 140 and not self.game.dispMenuHidden:
                self.game.rename_menubar("S.")
                self.game.dispMenuHidden = True
        else:  # Allows end screen to expand
            self.y = self.ogY * setPercent
            self.x = self.ogX * setPercent
        self.updateWinValues(2)  # Adjust window vars to shrink
        self.game.canvas.config(width=self.x, height=self.y)
        self.game.tk.geometry('+' + str(self.offx) + '+' + str(self.offy))
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
                                                         "Configure the window to the size you like it then right click"
                                                         " on the window. NOTE: If you just tried to resize and you are"
                                                         " seeing this again, your window must be taller in order for"
                                                         " the game to run.")
        else:
            result = simpledialog.messagebox.askokcancel("Window Size",
                                                         "It appears to be your first time running on this device. "
                                                         "Configure the window to the size you like it then right click"
                                                         " on the window. NOTE: If you just tried to resize and you are"
                                                         " seeing this again, your window must be taller in order for"
                                                         " the game to run.")
        if not result:
            return False  # Don't customise if not ok
        while not self.windowCustomised:
            try:  # Handle any window closes
                self.game.tk.update()
                if tk2 is not None:
                    tk2.update()
            except TclError as e:
                print(e)
                print("You have closed the window!")
                self.handleClose()
        if tk2 is not None:
            winfo = tk2.geometry()
        else:
            winfo = self.game.tk.geometry()
        winfo = winfo.replace("x", "+")
        winfo = winfo.split("+")
        self.x = int(winfo[0])
        self.y = int(winfo[1])
        self.offx = int(winfo[2])
        self.offy = int(winfo[3])
        if self.y < 61 or self.x < 61:  # Makes sure the game can run in this size
            self.windowCustomised = False
            self.customiseWindow(tk2)
        return True

    def handleClose(self, *args):
        try:
            self.game.tk.destroy()
        except TclError as e:
            print(e)
        if pygameInstalled:
            mixer.quit()
        sys.exit(0)
