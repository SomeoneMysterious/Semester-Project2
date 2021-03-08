import random  # Randomises enemy attributes
import bullet
import enemy
import infoWindow

pygameInstalled = True
try:
    from pygame import mixer
except ModuleNotFoundError as er:
    print("Pygame not installed, required for audio, game will not use any audio.")
    pygameInstalled = False


class EnemyCtrl:
    enemyIDs = []
    bulletIDs = []
    toCleanup = []
    round = 0
    moveLegs = True

    def __init__(self, gamein, windowin):
        self.game = gamein
        self.window = windowin
        if pygameInstalled:
            # Make sound effects
            self.shotSound = mixer.Sound("Sounds/shot sound.wav")
            self.stepSound = mixer.Sound("Sounds/footstep.wav")  # Not used yet

    def startRound(self):
        self.round += 1
        if self.round > 9:  # generate all 1, 2, and 3
            percent = (self.round - 4) * 2 * (self.game.difficulty.get() / 2)
            if percent > 50:  # Makes maximum percents at 25% for 1, 50% for 2, and 25% for 3, at round 30+.
                percent = 50
            level = random.choices([1, 2, 3], weights=[100 - percent * 1.5, percent, percent / 2], k=4 + self.round)
        elif self.round > 4:  # generate level 1 and 2 enemies
            percent = (self.round - 4) * 2 * (self.game.difficulty.get() / 2)
            level = random.choices([1, 2], weights=[100 - percent, percent], k=4 + self.round)
        else:  # generate level 1 enemies
            level = [1] * (4 + self.round)
        for w in range(0, 4 + self.round):  # Make each enemy
            enemyID = enemy.Enemy(self, self.game, self.window, level[w])
            self.enemyIDs.append(enemyID)
            self.toCleanup.append(enemyID)

    def roundCleanup(self):
        for i, o in enumerate(self.toCleanup):
            item = self.toCleanup[i]
            del item
        self.toCleanup = []

    def handleEnemies(self):
        # find some way the enemies move sound can be played ONLY WHILE MOVING, and at a reasonable interval
        [enemy.moveSelf() for enemy in self.enemyIDs]

    def handleBullets(self):
        [bulle.moveSelf() for bulle in self.bulletIDs]

    def makeBullet(self, target, inX, inY):
        bulle = bullet.Bullet(self.game, self.window, self, target, inX, inY)
        self.bulletIDs.append(bulle)
        self.toCleanup.append(bulle)

    def unpauseEnemies(self):  # ran after finish of pause, resets timers
        [enemy.unpause() for enemy in self.enemyIDs]

    def toggleLegMotion(self):
        self.moveLegs = not self.moveLegs
        [enemy.toggleLegMotion() for enemy in self.enemyIDs]
        self.window.editConfig("settings", "moveLegs", self.moveLegs)
        self.unpauseEnemies()

    def checkClickedLocation(self, clickX, clickY):
        if self.game.bullets <= 0 or not self.game.midRound:
            return  # if no bullets, or not in a round, no shoot
        self.game.bullets -= 1
        toDelete = []
        if pygameInstalled and not self.game.schoolFriendly:
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
        [enemy.killSelf() for enemy in self.enemyIDs]
        self.enemyIDs = []
        if self.game.gameRunning:
            self.game.midRound = False

    def winShrinkMove(self):
        [enemy.baseMove() for enemy in self.enemyIDs]
        [bullet.baseMove() for bullet in self.bulletIDs]
