# importing everything from tkinter
from tkinter import *
# importing ttk for styling widgets from tkinter
from tkinter import ttk
# importing filedialog from tkinter
from tkinter import filedialog as fd
# importing os module
import os

# creating a class called PDFViewer
class PDFViewer:
    # initializing the __init__ / special method
    def __init__(self, master):
        pass

# creating the root window using Tk() class
root = Tk()
# instantiating/creating object app for class PDFViewer
app = PDFViewer(root)
# calling the mainloop to run the app infinitely until user closes it
root.mainloop()
