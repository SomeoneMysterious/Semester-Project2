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
midx = x/2
midy = y/2
midox = midx
midoy = midy
canvas = Canvas(tk, width=x, height=y)
tk.resizable(width=False, height=False)
canvas.pack()
tk.geometry("+-7+0")
line = canvas.create_line(0, 0, x, y)
tower = canvas.create_rectangle(midx-25, midy-25, midx+25, midy+25, fill="green")
tk.update()
lives = 400
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
    if (x > 115):
        tk.geometry('+'+str(offx)+'+'+str(offy))
    canvas.coords(line, (-offx, -offy, ogX, ogY))
    canvas.coords(tower, (midx-25, midy-25, midx+25, midy+25))
    canvas.pack()
    tk.update()
time.sleep(5)
print(str(x)+'-'+str(y))
canvas.config(width=ogX, height=ogY)
tk.geometry("+-7+0")
tk.update()
