import sqlite3
from typing import List

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