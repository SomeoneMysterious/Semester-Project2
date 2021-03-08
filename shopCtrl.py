from tkinter import *


class ShopCtrl(object):
    __shops = {}
    __actions = {}
    __increment = {}
    __running = {}
    COMPLETED_CHECK = 4

    def __init__(self, gameIn, info_manager_in):
        self.game = gameIn
        self.infoManager = info_manager_in
        self.shopMenu = Menu(self.game.tk)

    def make_shop(self, name, cost, action, increment_cost_by=1, keypress=None, running=False):
        self.__shops[name] = cost
        self.__actions[name] = action
        self.__increment[name] = increment_cost_by
        self.__running[name] = running
        dispText = name + " (" + str(cost) + " Points)"
        self.shopMenu.add_command(label=dispText, command=action)
        if keypress is not None:
            self.game.tk.bind(keypress, action)

    def handle_costs(self, name, argsLen):
        """Handles other situations then the cost. Returns 0 if the game hasn't started, 1 if the shop can't be found,
        2 if the shop is still running, 3 if the user doesn't have enough currency, and 4 if it succeeds."""
        if not self.game.gameRunning:
            # Game hasn't started yet
            print("You haven't started the game yet.")
            self.cleanup(argsLen)
            return 0
        cost = self.__shops.get(name)
        rounded_cost = round(cost)
        if cost is None:
            print("WARNING: Shop name", name, "cannot be found. Please make sure it is set up correctly. \n"
                  "It's actions will not be done, and there will be no cost.")
            self.infoManager.displayInfo("404 - Shop not found.")
            self.cleanup(argsLen)
            return 1
        running = self.__running[name]
        if running:
            if isinstance(running, str):  # If it is a list it can be run multiple times
                print("Shop", name, "is still running, and it can't run multiple times. None will be created,"
                                    " and there will be no cost.")
                self.cleanup(argsLen)
                return 2
        if self.game.points >= rounded_cost:
            self.game.points -= rounded_cost
        else:
            print("That item is too expensive.")
            self.game.infoManager.displayInfo("That item is too expensive.")
            self.cleanup(argsLen)
            return 3
        increment_by = self.__increment[name]
        cost *= increment_by
        self.__shops[name] = cost
        return self.COMPLETED_CHECK

    def cleanup(self, argsLen):
        """Cleanups everything after a shop has been activated."""
        if argsLen == 0:  # Called from menu
            self.game.enemyCtrl.unpauseEnemies()

    def kill_all_enemies(self, *args):
        """ Shop item that kills all of the enemies"""
        argslen = len(args)
        done = self.handle_costs("Clear All Enemies", argslen)
        if done == self.COMPLETED_CHECK:
            self.game.enemyCtrl.killAllEnemies()
            self.cleanup(argslen)

    def expandWindow(self, *args):
        argslen = len(args)
        done = self.handle_costs("Expand Window-20s", argslen)
        if done == self.COMPLETED_CHECK:
            self.game.shrinkWin = False
            self.game.window.shrinkWindow(1)  # sets window to full size
            self.game.updateLocations()
            after_key = self.game.tk.after(20000, self.stopExpandWindow)  # Currently for 20 secs
            self.__running["Expand Window-20s"] = after_key
            self.cleanup(argslen)

    def stopExpandWindow(self):
        self.game.shrinkWin = True
        if self.game.gameRunning:
            self.game.window.shrinkWindow()
            self.game.updateLocations()
        self.__running["Expand Window-20s"] = False

    def expand_clip(self, *args):
        argslen = len(args)
        done = self.handle_costs("Expand Clip Size (+1)", argslen)
        if done == self.COMPLETED_CHECK:
            if self.game.clipSize == self.game.bullets:  # If clip is full, keep clip full
                self.game.bullets += 1
            self.game.clipSize += 1
            self.game.infoManager.updateItems()
            self.cleanup(argslen)


