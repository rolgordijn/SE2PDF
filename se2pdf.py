from tkinter import ttk
from database import Database

import subprocess

import tkinter
from tkinter import Frame, Listbox, filedialog, simpledialog
from tkinter import messagebox as mb

import os
import time

from threading import Thread
from typing import List

root = tkinter.Tk()


class App:
    def __init__(self, path) -> None:
        self.db = Database(path)
        self.destinationDirectory = ""
        self.gui_items = []

    

   
    

"""init routines"""
def initApp(db: Database)->None:
        initListBox(db)

"""Method called on initialisation of the app
fills the listbox with the drawings"""
def initListBox(db: Database) -> None:
        db.executeQuery("SELECT * FROM files")
        results = db.getAllResults()
        if(results):
             removeFileButton['state']='normal'
             setPathButton['state'] = 'normal'
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
    return db.getOneResult()


def doesNewFileNameExist(db: Database, newFileName:str)->int:
        db.executeQuery(f"SELECT COUNT(1) FROM files WHERE name= '{newFileName}'")
        return (db.getOneResult())

def changeFileExtensionToPDF(filename: str) -> str:
    return  f'{filename.split(".")[0]}.pdf' 


def getFilesToAdd()->List:
   return filedialog.askopenfilenames(initialdir="C://LDM_WORK" , filetypes = (("Solid Edge 2D files","*.dft"),("all files","*.*")))
    
def addFileButtonHandler(lb: Listbox, db: Database, paths: List, app: App) -> None:
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
            db.executeQuery(f"insert into files (path, filename, destination, name) values ('{path}','{filename}','{app.destinationDirectory}','{newName}')")
            removeFileButton['state']='normal'
            setPathButton['state']='normal'


def removeFileButtonHandler(db: Database, lb: Listbox) -> None:
    selected = lb.curselection()
    if(selected):
        filename = getFileNameFromListBox(lb,selected[0])
        db.executeQuery(f"DELETE FROM files WHERE filename= '{filename}'")
        lb.delete(selected[0])
        removeFileButtonHandler(db,lb)
        lb.selection_set(selected[0])
    if(lb.size() == 0):
        removeFileButton['state']='disabled'
        setPathButton['state']='disabled'

            
def setPathButtonHandler(db: Database, app: App) -> None:
    app.destinationDirectory = filedialog.askdirectory()
    db.executeQuery(f"UPDATE files SET destination = '{app.destinationDirectory}'")

    if " " in  app.destinationDirectory:
        mb.showwarning(title="space not allowed", message="Export directory should not contain spaces")
        return 
    
    textForLabel = "Destination:   " + app.destinationDirectory
    destinationLabel.configure(text=textForLabel)
    exportAsPDFButton['state'] = 'normal' 
    openDestinationButton['state'] = 'normal'
    

def changeListBoxItem(lb: Listbox, index: int, selectedFile:str, newFileName: str):
    lb.delete(index)
    addFileToListBox(index, selectedFile, newFileName)


def listBoxClickedHandler(db,lb)-> None:
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

    db.updateFileName(newFileName, selectedFile)
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
    app = App("files.db")
    

    db = app.db
    db.init()

    root.title('export to pdf')


    east = Frame(root)
    east.grid(row=1,column=1)
    west = Frame(root)
    west.grid(row=1,column=2)

    south= Frame(root)
    south.grid(row=2,column=1, columnspan=2)

    lb = Listbox(east, width=100, height=25, selectmode='extended' )
    lb.pack()
 
    lb.bind('<Double-1>',  lambda e, db, lb: listBoxClickedHandler(db,lb))

    BUTTON_WIDTH = 35


    addFileButton = ttk.Button(west, width=BUTTON_WIDTH, text ='Add file',command= lambda: addFileButtonHandler(lb,db, getFilesToAdd(), app))
    addFileButton.pack()


    removeFileButton= ttk.Button(west, width=BUTTON_WIDTH, text ='Remove file',command= lambda: removeFileButtonHandler(db,lb), state='disabled')
    removeFileButton.pack()
  

    setPathButton= ttk.Button(west,  width=BUTTON_WIDTH, text ='Set filename',  state='disabled',  command= lambda e, db, lb: listBoxClickedHandler(db,lb))
    setPathButton.pack()
   
   
    setNameButton= ttk.Button(west,  width=BUTTON_WIDTH, text ='Set Destination (all files)',command= lambda: setPathButtonHandler(db))
    setNameButton.pack()


    exportAsPDFButton = ttk.Button(west, width=BUTTON_WIDTH, text='Export Files as PDF', state='disabled' ,command= lambda: exportAsPDFButtonHandler(db))
    exportAsPDFButton.pack()
  

    openDestinationButton = ttk.Button(west, width=BUTTON_WIDTH, text='Open folder', state='disabled' ,command= lambda: openDestinationButtonHandler(app.destinationDirectory))
    openDestinationButton.pack()


    destinationLabel = ttk.Label(south, text="Destination: not set")
    destinationLabel.pack()


    statusLabel = ttk.Label(south, text="")
    statusLabel.pack()

    

   
    initApp(db)

    root.mainloop()
    db.conn.close()


  



