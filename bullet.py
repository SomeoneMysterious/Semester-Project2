import time  # Making sure tings are based on time not loops
from tkinter import *


class Bullet:
    m = b = 0

    def __init__(self, gameIn, windowIn, enemyCtrlIn, target, startXIn, startYIn):
        self.game = gameIn
        self.window = windowIn
        self.enemyCtrl = enemyCtrlIn
        self.target = target
        self.startX = startXIn
        self.startY = startYIn
        self.x = startXIn
        self.y = startYIn
        self.speedPPS = 300 + self.game.enemyCtrl.round * 10 / 1536 * self.window.ogX
        try:
            self.img = PhotoImage(file="Images/bullet.gif")
        except RuntimeError:
            pass
        self.dispX = self.x - self.window.offx + self.window.offox
        self.dispY = self.y - self.window.offy + self.window.offoy
        self.disp = self.game.canvas.create_image(self.dispX, self.dispY, image=self.img)
        self.lastTime = time.time()

    def __del__(self):
        try:
            self.killSelf()
        except (ValueError, TclError):
            pass

    def moveSelf(self):
        self.speedPPS = 300 + self.game.enemyCtrl.round * 10 / 1536 * self.window.ogX
        if self.target == "tower":
            targX = self.window.midox
            targY = self.window.midoy
        else:
            if self.target.dead:
                self.killSelf()
            targX = self.target.x
            targY = self.target.y
        self.m = (targY - self.y) / (targX - self.x)
        self.b = targY + self.m * targX
        self.speedPPS *= abs(targX - self.x) / (abs(targX - self.x) + abs(targY - self.y))
        Time = time.time()
        change1 = self.x > targX
        # Change based on time
        if change1:
            self.x -= self.speedPPS * (Time - self.lastTime)
        else:
            self.x += self.speedPPS * (Time - self.lastTime)
        # use the line function to get y
        self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
        self.lastTime = Time
        self.baseMove()
        if change1 != (self.x > targX):  # Went past target/hit target
            if self.target == "tower":
                self.game.health -= 1
            else:
                self.target.checkClickedLocation(self.target.dispX, self.target.dispY)  # Deal damage to enemy
            self.killSelf()

    def killSelf(self):
        self.game.canvas.delete(self.disp)
        del (self.enemyCtrl.bulletIDs[self.enemyCtrl.bulletIDs.index(self)])

    def baseMove(self):
        # Converts from max window size to current, then displays
        self.dispX = self.x - self.window.offx + self.window.offox
        self.dispY = self.y - self.window.offy + self.window.offoy
        self.game.canvas.coords(self.disp, (self.dispX, self.dispY))
