
import sqlite3


import tkinter
from tkinter import Listbox, filedialog, simpledialog
from tkinter import messagebox as mb

import os
from typing import List    

root = tkinter.Tk()
root.title('export to pdf')
#root.geometry("1280x720")

destinationDirectory = " "

conn = None
c = None

def initListBox() -> None:
    global c, conn
    c.execute("SELECT * FROM files")
    addFilesToListBox([i[0] for i in c.fetchall()])
    conn.commit()

def initDataBase(db:str) -> None:
    global c, conn
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS files (
        path text,
        filename text,
        destination text,
        name text
        )""") 
    conn.commit()

def initApp(db:str)->None:
    initDataBase(db)
    initListBox()

def fileNameFromPath(file:str) -> str:
    return str(os.path.basename(file))

def addFilesToListBox(paths: List) -> None:
    global lb
    for path in paths:
         filename = fileNameFromPath(path)
         lb.insert(0, filename)


def doesPathExist(path:str)-> int:
    c.execute("SELECT COUNT(1) FROM files WHERE path= ?", (path,))
    return (c.fetchone()[0])
    conn.commit()
    

def addFileButtonHandler() -> None:
    global lb
    paths = filedialog.askopenfilenames(filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    for path in paths:
        if doesPathExist(path): 
            mb.showwarning(title="duplicate file", message="file added to the queue")
            continue
        else:
            filename = fileNameFromPath(path)
            lb.insert(0, filename)
            c.execute("insert into files (path, filename, destination, name) values (?, ?, ?, ?)",
                (path, filename, destinationDirectory, filename))
            conn.commit()

def getFileNameFromListBox(line) -> str:
    return lb.get(line)


def removeFileButtonHandler() -> None:
    selected = lb.curselection()
    if(selected):
        filename = getFileNameFromListBox(selected[0])
        c.execute("DELETE FROM files WHERE filename= ?", (filename,))
        lb.delete(selected[0])
        removeFileButtonHandler()
        conn.commit()
        
def setPathButtonHandler() -> None:
    global destinationDirectory
    destinationDirectory = filedialog.askdirectory()
    c.execute("UPDATE files SET destination = ?", (destinationDirectory,))
    conn.commit()
    textForLabel = "Destination:   " + destinationDirectory
    destinationLabel.configure(text=textForLabel)

def listBoxClickedHandler(Event):
    global c, conn
    selected = lb.curselection()
    if(len(selected)>1):
        mb.showwarning(title="multiple selection not allowed", message="Select only one file")
        return
    index = selected[0]
    selectedFile = getFileNameFromListBox(index)
    newFileName = simpledialog.askstring('enter new name', 'enter new name')
    c.execute("UPDATE files SET name = ? WHERE filename = ?", (newFileName,selectedFile,))
    conn.commit()
    lb.delete(index)
    lb.insert(index, f"{selectedFile} % {newFileName}")

def exportAsPDFButtonHandler():
    if destinationDirectory == " ":
        mb.showwarning(title="Destination is not set", message="Set the destination before you start the export")
        return
    if lb.size() == 0: 
        mb.showwarning(title="Nothing to export", message="There's nothing to do")
        return
    else:
        mb.showwarning(title="Nothing implemented yet", message="I don't know how to do that!")

lb = tkinter.Listbox(root, width=40, height=25, selectmode='extended' )
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

initApp("files.db")









root.mainloop()
conn.commit()
conn.close() 
