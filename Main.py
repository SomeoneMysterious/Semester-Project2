from tkinter import *
import time
tk = Tk()
tk.title("Protect The Base!")
x = tk.winfo_screenwidth()
y = tk.winfo_screenheight()-63
ratio = x/y
print(ratio)
print(str(x)+"-"+str(y))
ogX = x
ogY = y
midox = x/2
midoy = y/2
canvas = Canvas(tk, width=x, height=y)
tk.resizable(width=False, height=False)
canvas.pack()
tk.geometry("+-7+0")
line = canvas.create_line(0, 0, x, y)
tk.update()
lives = 50
ogLives = lives
time.sleep(5)
#y = y-2
for lives in range(lives, -1, -1):
    y = ogY/ogLives*lives
    x = ogX/ogLives*lives
    midx = x/2
    midy = y/2
    offx = int(midox-midx)-7
    offy = int(midoy-midy)
    canvas.config(width=x, height=y)
    tk.geometry('+'+str(offx)+'+'+str(offy))
    canvas.coords(line, (-offx, -offy, ogX, ogY))
    canvas.pack()
    tk.update()
    time.sleep(.2)
time.sleep(5)
print(str(x)+'-'+str(y))
canvas.config(width=ogX, height=ogY)
tk.geometry("+0+0")
tk.update()
