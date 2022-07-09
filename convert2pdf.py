
from asyncio.windows_events import NULL
from mimetypes import init
from random import random


import sqlite3
from string import ascii_uppercase


import tkinter
from tkinter import filedialog, simpledialog
from tkinter import messagebox as mb

import os    

root = tkinter.Tk()
root.title('export to pdf')
root.geometry("1280x720")

destinationDirectory = " "

conn = sqlite3.connect("files.db")
c = conn.cursor()


c.execute("""CREATE TABLE IF NOT EXISTS files (
    path text,
    destination text,
    name text
       )""") 

def fileNameFromPath(file):
    return str(os.path.basename(file))

def addFileButtonHandler():
    global lb
    paths = filedialog.askopenfilenames(filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    for path in paths:
        filename = fileNameFromPath(path)
        lb.insert(0, filename)
        c.execute("insert into files (path, destination, name) values (?, ?, ?)",
            (path, destinationDirectory, filename))
def removeFileButtonHandler():
    selected = lb.curselection()
    if(selected):
        lb.delete(selected[0])
        removeFileButtonHandler()
        
def setPathButtonHandler():
    global destinationDirectory
    destinationDirectory = filedialog.askdirectory()
    textForLabel = "Destination:   " + destinationDirectory
    destinationLabel.configure(text=textForLabel)

def listBoxClickedHandler(Event):
    selected = lb.curselection() 
    if(len(selected)>1):
        mb.showwarning(title="multiple selection not allowed", message="Select only one file")
        return
    simpledialog.askstring('enter new name', 'enter new name')

def exportAsPDFButtonHandler():
    if destinationDirectory == " ":
        mb.showwarning(title="Destination is not set", message="Set the destination before you start the export")
        return
    if lb.size() == 0: 
        mb.showwarning(title="Nothing to export", message="There's nothing to do")
        return
    else:
        mb.showwarning(title="Nothing implemented yet", message="I don't know how to do that!")

lb = tkinter.Listbox(root, width=150, height=25, selectmode='extended' )
lb.grid(row=1, column=1, rowspan=4)
lb.bind('<Double-1>', listBoxClickedHandler)

addFileButton = tkinter.Button(root, width=18, text ='Add file',command=addFileButtonHandler)
addFileButton.grid(row=1,column=2) 

removeFileButton= tkinter.Button(root, width=18, text ='Remove file',command=removeFileButtonHandler)
removeFileButton.grid(row=2,column=2)

setPathButton= tkinter.Button(root,  width=18, text ='Set Destination',command=setPathButtonHandler)
setPathButton.grid(row=3,column=2)

exportAsPDFButton = tkinter.Button(root, width=18, text='Export Files as PDF', command=exportAsPDFButtonHandler)
exportAsPDFButton.grid(row=4,column=2)

destinationLabel = tkinter.Label(root, text="Destination: not set")
destinationLabel.grid(column=1, row=5)






root.mainloop()
conn.commit()
conn.close() 
