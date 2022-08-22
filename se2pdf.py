from operator import contains
import sqlite3

import subprocess

import tkinter
from tkinter import Frame, Listbox, filedialog, simpledialog
from tkinter import messagebox as mb

import os


import time

from threading import Thread
from typing import List

root = tkinter.Tk()

class Database: 
    def __init__(self, path):
        self.path = path

    def init(self):
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()

        self.c.execute("""CREATE TABLE IF NOT EXISTS files (
            path text,
            filename text,
            destination text,
            name text
            )""") 
        self.conn.commit()
    
    def executeQuery(self, query):
        print(query)
        self.c.execute(query)
        self.conn.commit()
    
    def getResults(self, amount) -> List: 
        return self.c.fetchmany(amount)
    
    def getAllResults(self) -> List:
        return self.c.fetchall()
    
    def getOneResult(self)-> List:
        return self.c.fetchone()[0]
    

"""init routines"""
def initApp(db: Database)->None:
        initListBox(db)

"""Method called on initialisation of the app
fills the listbox with the drawings"""
def initListBox(db: Database) -> None:
        db.executeQuery("SELECT * FROM files")
        results = db.getAllResults()
        for row in results: 
            addFileToListBox(0, row[1], row[3])

   


"""removes the path and returns only the filename"""
def fileNameFromPath(file:str) -> str:
    return str(os.path.basename(file))

def addFileToListBox(index :int, currentFileName: str, newFileName: str) -> None:
    textToDsiplay = f"{currentFileName} --> {newFileName}"
    lb.insert(index, textToDsiplay )

def getFileNameFromListBox(lb: Listbox, line: int) -> str:
     return  lb.get(line).split('-->')[0].strip()

def doesPathExist(db: Database, path:str)-> int:
    c = db.executeQuery(f"SELECT COUNT(1) FROM files WHERE path= '{path}'")
    ret = db.getOneResult()


def doesNewFileNameExist(db: Database, newFileName:str)->int:
        db.executeQuery(f"SELECT COUNT(1) FROM files WHERE name= '{newFileName}'")
        return (db.getOneResult())

def changeFileExtensionToPDF(filename: str) -> str:
    return  f'{filename.split(".")[0]}.pdf' 
    
def addFileButtonHandler(db: Database) -> None:
    global lb
    paths = filedialog.askopenfilenames(initialdir="C://LDM_WORK" , filetypes = (("Solid Edge 2D files","*.dft"),("all files","*.*")))
    for path in paths:
        print(f'add file: path is {path}')
        if doesPathExist(db, path): 
            mb.showwarning(title="duplicate file", message="file added to the queue")
            continue
        else:
            filename = fileNameFromPath(path)
            newName = changeFileExtensionToPDF(filename)

            if(doesNewFileNameExist(db, newName)):
                mb.showwarning(title="duplicate filename", message="file with same name already added to the queue")

            addFileToListBox(0, filename, newName)
            db.executeQuery(f"insert into files (path, filename, destination, name) values ('{path}','{filename}','{destinationDirectory}','{newName}')")


def removeFileButtonHandler(db: Database, lb: Listbox) -> None:
    selected = lb.curselection()
    if(selected):
        filename = getFileNameFromListBox(lb,selected[0])
        db.executeQuery(f"DELETE FROM files WHERE filename= '{filename}'")
        lb.delete(selected[0])
        removeFileButtonHandler(db,lb)
        lb.selection_set(selected[0])
            
def setPathButtonHandler(db: Database) -> None:
    global destinationDirectory
    destinationDirectory = filedialog.askdirectory()
    db.executeQuery(f"UPDATE files SET destination = '{destinationDirectory}'")

    if " " in destinationDirectory:
        mb.showwarning(title="space not allowed", message="Export directory should not contain spaces")
        return 
    
    textForLabel = "Destination:   " + destinationDirectory
    destinationLabel.configure(text=textForLabel)
    exportAsPDFButton['state'] = 'normal' 
    openDestinationButton['state'] = 'normal'


def updateFileName(db: Database, newFileName: str, selectedFile: str):
    db.executeQuery(f"UPDATE files SET name = '{newFileName}' WHERE filename = '{selectedFile}'")
    

def changeListBoxItem(lb: Listbox, index: int, selectedFile:str, newFileName: str):
    lb.delete(index)
    addFileToListBox(index, selectedFile, newFileName)


def listBoxClickedHandler(db)-> None:
    global c, conn
    selected = lb.curselection()
    if not len(selected): return
    if(len(selected)>1):
        mb.showwarning(title="multiple selection not allowed", message="Select only one file")
        return
    index = selected[0]
    selectedFile = getFileNameFromListBox(lb, index)
    newFileName = simpledialog.askstring('enter new name', 'enter new name')
    
    if newFileName is None:
        mb.showwarning(title='No input', message='no input detected, try again')
        return

    newFileName = changeFileExtensionToPDF(newFileName)

    if(doesNewFileNameExist(db,newFileName)):
        mb.showwarning(title="duplicate filename", message="file with same name already added to the queue")
        return

    updateFileName(db, newFileName, selectedFile)
    changeListBoxItem(lb, index, selectedFile, newFileName)
    
def getExportCommand(row):
    cmd = f'"C:/Program Files/Solid Edge ST9/Program/SolidEdgeTranslationServices.exe" -i={row[0]} -o={row[2]}/{row[3]} -t=pdf'
    cmd = cmd.replace('/','\\')
    return cmd

def exportSingleFile(cmd):
    return subprocess.Popen(cmd, shell=True)


def exportFiles(commands):
    exportQueue = []
    while commands or exportQueue:
        if len(exportQueue)<4 and commands:
            exportQueue.append(exportSingleFile(commands.pop()))
        exportQueue = [eq for eq  in exportQueue if eq.poll() is None] 
        statusLabelText = f"{len(commands)} files in the export Queue, currently {len(exportQueue)} files being exported"
        statusLabel.configure(text = statusLabelText)
        time.sleep((1))
    mb.showinfo(title="files exporterd", message="all files where exported to the selected folder")  
    statusLabel.configure(text = "")

def exportAsPDFButtonHandler(db):
    if destinationDirectory == " ":
        mb.showwarning(title="Destination is not set", message="Set the destination before you start the export")
        return
    if lb.size() == 0: 
        mb.showwarning(title="Nothing to export", message="There's nothing to do")
        return
    else:
        db.executeQuery("SELECT * FROM files")
        commands = [getExportCommand(row) for row in db.getAllResults()]
        Thread(target=exportFiles, args=(commands,)).start()

def openDestinationButtonHandler(destinationDirectory):
    FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
    print(destinationDirectory)
    subprocess.run([FILEBROWSER_PATH, destinationDirectory.replace('/','\\')])

if __name__ == '__main__':
    db = Database("files.db")
    db.init()
    
    root.title('export to pdf')


    lb = Listbox(root, width=100, height=25, selectmode='extended' )
    lb.grid(row=1, column=1, rowspan=6)
    lb.bind('<Double-1>', listBoxClickedHandler(db))

    addFileButton = tkinter.Button(root, width=18, text ='Add file',command= lambda: addFileButtonHandler(db))
    addFileButton.grid(row=1,column=2) 

    removeFileButton= tkinter.Button(root, width=18, text ='Remove file',command= lambda: removeFileButtonHandler(db,lb))
    removeFileButton.grid(row=2,column=2)

    setPathButton= tkinter.Button(root,  width=18, text ='Set filename',command= lambda: listBoxClickedHandler(db))
    setPathButton.grid(row=3,column=2)
   
    setNameButton= tkinter.Button(root,  width=18, text ='Set Destination (all files)',command= lambda: setPathButtonHandler(db))
    setNameButton.grid(row=4,column=2)

    exportAsPDFButton = tkinter.Button(root, width=18, text='Export Files as PDF', state='disabled' ,command= lambda: exportAsPDFButtonHandler(db))
    exportAsPDFButton.grid(row=5,column=2)

    openDestinationButton = tkinter.Button(root, width=18, text='Open folder', state='disabled' ,command= lambda: openDestinationButtonHandler(destinationDirectory))
    openDestinationButton.grid(row=6,column=2)

    destinationLabel = tkinter.Label(root, text="Destination: not set")
    destinationLabel.grid(column=1, row=7, columnspan=2)

    statusLabel = tkinter.Label(root, text="")
    statusLabel.grid(column=1, row=8, columnspan=2)

    destinationDirectory = " "

   
    initApp(db)

    root.mainloop()
    db.conn.close()



