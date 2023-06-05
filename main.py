from config import *
from backend.tools import *
from xlsxdb.xlsxdb import Controller
from backend.extract import *
from frontend.view import View

    
# точка входа 
def main():
    db = Controller(NAME_DB_VALUES)
    front = View(db)
    front.launch()


main()


