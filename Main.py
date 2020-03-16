from tkinter import *
import time
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
    def __init__(self):
        tk.title("Protect The Base!")
        self.canvas = Canvas(tk, width=500, height=100)
        tk.resizable(width=False, height=False)
        self.canvas.pack()
        tk.geometry("+-7+0")
        self.titleScreen()
    def titleScreen(self):
        self.tower = Tower(self)
        self.enemyCtrl = Enemys()
        tk.update()
        self.shrinkTest()
    def handleGame(self):
        pass
    def shrinkWindow(self):
        global x, y, midx, midy, offx, offy
        y = ogY/self.ogHealth*self.health
        x = ogX/self.ogHealth*self.health
        midx = x/2
        midy = y/2
        offx = int(midox-midx)-7
        offy = int(midoy-midy)
        self.canvas.config(width=x, height=y)
        if (x > 115):
            tk.geometry('+'+str(offx)+'+'+str(offy))
        self.canvas.pack()
        self.updateLocations()
        tk.update()
    def updateLocations(self):
        self.tower.moveTower()
    def shrinkTest(self):
        for self.health in range(self.health, -1, -1):
            self.shrinkWindow()
            time.sleep(.1)
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
    def moveEnemys(self):
        pass
    def winSrinkMove(self):
        pass

game = Game()
print(game.canvas)
