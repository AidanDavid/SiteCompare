from tkinter import *
from tkinter import ttk

class GUI:
    def __init__(self):
        pass

    def mainScreen(self):
        root = Tk()
        root.geometry("1000x600")

        ttk.Label(root, text="Site Comparator").place(x=500, y=200)
        ttk.Button(root, text="Start", command=root.destroy).place(x=400, y=300)
        ttk.Button(root, text="Quit", command=root.destroy).place(x=600, y=300)

        root.mainloop()

gui = GUI()
gui.mainScreen()
