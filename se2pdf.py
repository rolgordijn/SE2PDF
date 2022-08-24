from tkinter import ttk
from turtle import width


from app import App
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

"""Method called on initialisation of the app
fills the listbox with the drawings"""
def initListBox(db: Database) -> None:
        db.executeQuery("SELECT * FROM files")
        results = db.getAllResults()
        if(results):
             removeFileButton['state']='normal'
             setNewFileNameButton['state'] = 'normal'
        for row in results: 
            addFileToListBox(0, row[1], row[3])

"""removes the path and returns only the filename"""
def fileNameFromPath(file:str) -> str:
    return str(os.path.basename(file))

def addFileToListBox(index :int, currentFileName: str, newFileName: str) -> None:
    textToDsiplay = f"{currentFileName} --> {newFileName}"
    lb.insert(index, textToDsiplay )

def getFileNameFromListBox(line: str) -> str:
     return  line.split('-->')[0].strip()

def changeFileExtensionToPDF(filename: str) -> str:
    return  f'{filename.split(".")[0]}.pdf' 


def getFilesToAdd()->List:
   return filedialog.askopenfilenames(initialdir="C://LDM_WORK" , filetypes = (("Solid Edge 2D files","*.dft"),("all files","*.*")))
    
def addFileButtonHandler(lb: Listbox, db: Database, paths: List, app: App) -> None:
    for path in paths:
        print(f'add file: path is {path}')
        if db.doesPathExist(path): 
            mb.showwarning(title="duplicate file", message="file added to the queue")
            continue
        else:
            filename = fileNameFromPath(path)
            newName = changeFileExtensionToPDF(filename)

            if(db.doesNewFileNameExist(newName)):
                mb.showwarning(title="duplicate filename", message="file with same name already added to the queue")

            addFileToListBox(0, filename, newName)
            db.executeQuery(f"insert into files (path, filename, destination, name) values ('{path}','{filename}','{app.destinationDirectory}','{newName}')")
            removeFileButton['state']='normal'
            setNewFileNameButton['state']='normal'


def removeFileButtonHandler(db: Database, lb: Listbox) -> None:
    selected = lb.curselection()
    if(selected):
        filename = getFileNameFromListBox(lb.get(selected[0]))
        db.executeQuery(f"DELETE FROM files WHERE filename= '{filename}'")
        lb.delete(selected[0])
        removeFileButtonHandler(db,lb)
        lb.selection_set(selected[0])
    if(lb.size() == 0):
        removeFileButton['state']='disabled'
        setNewFileNameButton['state']='disabled'

            
def setDestinationPathButtonHandler(a: App) -> None:
    destination = filedialog.askdirectory()

    #if " " in  destination:
    #        mb.showwarning(title="space not allowed", message="Export directory should not contain spaces")
    #        return 
    
    print(type(destination))
    a.setDestinationDirectory(destination)

    textForLabel = "Destination:   " + app.destinationDirectory
    destinationLabel.configure(text=textForLabel)
    exportAsPDFButton['state'] = 'normal' 
    openDestinationButton['state'] = 'normal'
    

def changeListBoxItem(lb: Listbox, index: int, selectedFile:str, newFileName: str):
    lb.delete(index)
    addFileToListBox(index, selectedFile, newFileName)


def listBoxClickedHandler(event, db : Database,lb: Listbox)-> None:
    selected = lb.curselection()
    if not len(selected): return
    if(len(selected)>1):
        mb.showwarning(title="multiple selection not allowed", message="Select only one file")
        return
    index = selected[0]
    selectedFile = getFileNameFromListBox(lb.get(index))
    newFileName = simpledialog.askstring(title='enter new name', initialvalue=selectedFile.split('.')[0], prompt="Type the new filename", width="200")
    
    if newFileName is None:
        mb.showwarning(title='No input', message='no input detected, try again', )
        return

    newFileName = changeFileExtensionToPDF(newFileName)

    if(db.doesNewFileNameExist(newFileName)):
        mb.showwarning(title="duplicate filename", message="file with same name already added to the queue")
        return

    db.updateFileName(newFileName, selectedFile)
    changeListBoxItem(lb, index, selectedFile, newFileName)
    
def getExportCommand(row: List):
    cmd = f'"C:/Program Files/Solid Edge ST9/Program/SolidEdgeTranslationServices.exe" -i="{row[0]}" -o="{row[2]}/{row[3]}" -t=pdf'
    cmd = cmd.replace('/','\\')
    print(f"the command is: {cmd}")
    return cmd

def exportSingleFile(cmd :str):
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

def exportAsPDFButtonHandler(db :Database):
    if lb.size() == 0: 
        mb.showwarning(title="Nothing to export", message="There's nothing to do")
        return
    else:
        db.executeQuery("SELECT * FROM files")
        commands = [getExportCommand(row) for row in db.getAllResults()]
        Thread(target=exportFiles, args=(commands,)).start()

def openDestinationButtonHandler(destinationDirectory: str):
    FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
    print(destinationDirectory)
    subprocess.run([FILEBROWSER_PATH, destinationDirectory])




if __name__ == '__main__':
    app = App(Database("files.db"))

    app.db.init()

    root.title('export to pdf')


    east = Frame(root)
    east.grid(row=1,column=1)
    west = Frame(root)
    west.grid(row=1,column=2)

    south= Frame(root)
    south.grid(row=2,column=1, columnspan=2)

    lb = Listbox(east, width=100, height=25, selectmode='extended' )
    lb.pack()
 
    lb.bind('<Double-1>',  lambda e, db=app.db, lb=lb: listBoxClickedHandler(e, db,lb))

    BUTTON_WIDTH = 35


    addFileButton = ttk.Button(west, width=BUTTON_WIDTH, text ='Add file',command= lambda: addFileButtonHandler(lb,app.db, getFilesToAdd(), app))
    addFileButton.pack()


    removeFileButton= ttk.Button(west, width=BUTTON_WIDTH, text ='Remove file',command= lambda: removeFileButtonHandler(app.db,lb), state='disabled')
    removeFileButton.pack()
  

    setNewFileNameButton= ttk.Button(west,  width=BUTTON_WIDTH, text ='Set filename',  state='disabled',  command= lambda e=None, db=app.db, lb=lb: listBoxClickedHandler(None, db,lb))
    setNewFileNameButton.pack()
   
   
    setDestinationPathButton= ttk.Button(west,  width=BUTTON_WIDTH, text ='Set Destination (all files)',command= lambda: setDestinationPathButtonHandler(app))
    setDestinationPathButton.pack()


    exportAsPDFButton = ttk.Button(west, width=BUTTON_WIDTH, text='Export Files as PDF', state='disabled' ,command= lambda: exportAsPDFButtonHandler(app.db))
    exportAsPDFButton.pack()
  

    openDestinationButton = ttk.Button(west, width=BUTTON_WIDTH, text='Open folder', state='disabled' ,command= lambda: openDestinationButtonHandler(app.destinationDirectory))
    openDestinationButton.pack()


    destinationLabel = ttk.Label(south, text="Destination: not set")
    destinationLabel.pack()


    statusLabel = ttk.Label(south, text="")
    statusLabel.pack()

    

   
    initListBox(app.db)

    root.mainloop()
    app.db.conn.close()


  



