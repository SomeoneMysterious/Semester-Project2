from tkinter import *
import time
tk = Tk()
tk.title("Protect The Base!")
x = tk.winfo_screenwidth()
y = tk.winfo_screenheight()
ratio = x/y
print(ratio)
print(str(x)+"-"+str(y))
ogX = x
ogY = y
midox = x/2
midoy = y/2
canvas = Canvas(tk, width=x, height=y)
tk.resizable(width=False, height=False)
#tk.geometry(str(x)+'x'+str(y))
canvas.pack()
line = canvas.create_line(0, 0, x, y)
tk.update()
time.sleep(5)
#y = y-2
for y in range(y, 250, -1):
    midx = x/2
    midy = y/2
    offx = int(midox-midx)
    offy = int(midoy-midy)
    canvas.config(width=x, height=y)
    tk.geometry('+'+str(offx)+'+'+str(offy))
    canvas.coords(line, (-offx, -offy, ogX, ogY))
    canvas.pack()
    tk.update()
    x = x-ratio
    time.sleep(.05)
time.sleep(5)
print(str(x)+'-'+str(y))
canvas.config(width=ogX, height=ogY)
tk.geometry("+0+0")
tk.update()
time.sleep(10)
