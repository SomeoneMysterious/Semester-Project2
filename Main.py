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
        self.canvas = Canvas(tk, width=500, height=100)
        tk.resizable(width=False, height=False)
        self.canvas.pack()
        tk.geometry("+-7+0")
        self.enemyCtrl = Enemys()
        self.tower = Tower(self)
        self.titleScreen()

    def titleScreen(self):
        tk.update()
        self.gameRunning = True
        self.handleGame()

    def handleGame(self):
        while self.gameRunning:
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
        if random.randint(1, 50) == 10:
            self.health -= 1

    def endScreen(self):
        tk.destroy()
        sys.exit()


class Tower:
    def __init__(self, game):
        self.game = game
        self.tower = self.game.canvas.create_rectangle(midx-25, midy-25, midx+25, midy+25, fill="green")
        tk.update()

    def moveTower(self):
        print(midx)
        self.game.canvas.coords(self.tower, (midx-25, midy-25, midx+25, midy+25))
        tk.update()


class Enemys:
    def __init__(self):
        pass

    def moveEnemies(self):
        pass

    def winShrinkMove(self):
        pass


game = Game()
print(game.canvas)
