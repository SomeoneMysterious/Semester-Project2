import math  # Ceil's of numbers
import random  # Randomises enemy attributes
import time  # Making sure tings are based on time not loops
from tkinter import *


class Enemy:
    # Init Vars
    x = y = dispX = dispY = m = b = oldMove = lastMove = loopNum = 0
    disp = disp2 = disp3 = currDisp = spawnWall = lives = img1 = img2 = img3 = 2
    lastTime = timeForAnimate = timeToStop = time.time()
    dead = False

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
        self.landX = 30
        self.landY = 50
        # Make images of enemy
        self.setupImages(level)
        # Put enemy on screen
        self.spawnSelf()

    def setupImages(self, level):
        if level == 1:
            self.lives = 1
            self.img1 = PhotoImage(file='Images/stick1.gif')
            self.img2 = PhotoImage(file='Images/stick2.gif')
            self.img3 = PhotoImage(file='Images/stick3.gif')
        elif level == 2:
            self.lives = 2
            self.speedPPS -= 9
            self.img1 = PhotoImage(file='Images/stick1L2.gif')
            self.img2 = PhotoImage(file='Images/stick2L2.gif')
            self.img3 = PhotoImage(file='Images/stick3L2.gif')
        else:
            self.lives = 1
            self.landX = 125
            self.landY = 125
            if self.game.schoolFriendly:
                self.img1 = PhotoImage(file='Images/stick1L3.gif')
                self.img2 = PhotoImage(file='Images/stick2L3.gif')
                self.img3 = PhotoImage(file='Images/stick3L3.gif')
            else:
                self.img1 = PhotoImage(file='Images/stick1L3S1.gif')
                self.img2 = PhotoImage(file='Images/stick2L3S1.gif')
                self.img3 = PhotoImage(file='Images/stick3L3S1.gif')

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
        if self.level == 3 and self.x > self.window.midox and not self.game.schoolFriendly:
            # Flips the gun to face the tower
            self.img1 = PhotoImage(file='Images/stick1L3S2.gif')
            self.img2 = PhotoImage(file='Images/stick2L3S2.gif')
            self.img3 = PhotoImage(file='Images/stick3L3S2.gif')
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
            if abs(self.window.midoy - self.y) > self.landY or abs(self.window.midox - self.x) > self.landX:
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
                        self.y = self.window.midoy - self.landY
                        self.x = abs((-1 * self.y - self.b + self.window.ogY) / self.m)
                        if self.window.midox - self.x < -self.landX:
                            self.x = self.window.midox - self.landX
                            self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
                        elif self.window.midox - self.x > self.landX:
                            self.x = self.window.midox + self.landX
                            self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
                    elif self.spawnWall == 2:
                        self.y = self.window.midoy + self.landY
                        self.x = abs((-1 * self.y - self.b + self.window.ogY) / self.m)
                        if self.window.midox - self.x < -self.landX:
                            self.x = self.window.midox - self.landX
                            self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
                        elif self.window.midox - self.x > self.landX:
                            self.x = self.window.midox + self.landX
                            self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
                    elif self.spawnWall == 3:
                        self.x = self.window.midox - self.landX
                        self.y = abs(-1 * self.m * self.x + self.b - self.window.ogY)
                    else:
                        self.x = self.window.midox + self.landX
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
            if self.level == 3:
                if self.lastTime + .8 <= Time:
                    self.enemyCtrl.makeBullet("tower", self.x, self.y)
                    self.lastTime = Time
            else:
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
        self.dead = True

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
                self.dead = False
                self.setupImages(1)
                self.setupDisp()
            elif self.lives <= 0:
                self.killSelf()
                return True
        return False
