import time  # Making sure tings are based on time not loops
from tkinter import *


class infoManager:
    tk = windowAlive = canvas = healthbar = ammobar = None
    waveText = pointsText = ammoText = infoDisp = infoDisp2 = currTextId = None

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
        self.canvas = Canvas(self.tk, width=200, height=200)
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
        self.infoDisp = self.canvas.create_text(100, 170, text='yeet', font=('Helvetica', 10), tag="infoTxt")
        self.infoDisp2 = self.canvas.create_text(100, 190, text='yeet', font=('Helvetica', 10), tag="infoTxt")
        self.tk.update_idletasks()
        self.tk.geometry('200x160')
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

    def displayInfo(self, toDisp, toDisp2=None):
        if self.windowAlive:
            if toDisp2 is not None:
                self.tk.geometry('200x200')
                self.canvas.itemconfigure(self.infoDisp2, text=toDisp2, state="normal")
            else:
                self.tk.geometry('200x180')
            self.canvas.itemconfigure(self.infoDisp, text=toDisp, state="normal")
            if self.currTextId is not None:
                self.tk.after_cancel(self.currTextId)
            self.tk.update_idletasks()
            self.currTextId = self.tk.after(5000, self.hideInfo)

    def hideInfo(self):
        self.tk.geometry('200x160')
        self.currTextId = None

    def gameOver(self):
        self.canvas.delete("infoTxt")
        self.canvas.destroy()
        self.tk.destroy()
