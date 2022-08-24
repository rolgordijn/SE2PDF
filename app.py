from database import Database
class App:
    def __init__(self, database: Database) -> None:
        self.db = database
        self.destinationDirectory = ""
    
    def setDestinationDirectory(self, dir):
        self.destinationDirectory = dir.replace('/','\\')
        self.db.executeQuery(f"UPDATE files SET destination = '{self.destinationDirectory}'")