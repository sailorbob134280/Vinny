import PySide2
import wine_bottle
from db_man import DatabaseManager
from main_window import *

class MainInterface(QtWidgets.QMainWindow, Ui_Vinny):
    def __init__(self):
        super().__init__()
        self.setupUi(Vinny)

        self.InventorySearch.clicked.connect(self.quick_search)

    def refresh_tables(self):
        db_grab = DatabaseManager()
        inv_rows = db_grab.db_fetch('SELECT * FROM userinventory ORDER BY wine_id', rows='all')

    # Iterate through each of the entries in the inventory For each
    # entry, look it up in the winedata table and add create one 
    # long list which the relevant data. This is a little slower,
    # but more memory efficient. Write that to the extended page. 
        for i in range(len(inv_rows)):
            write_row = list(db_grab.db_fetch('SELECT * FROM winedata WHERE wine_id=?', (inv_rows[i][0],)))
            write_row.extend(inv_rows[i][2:])
            print(write_row)


    @QtCore.Slot()
    def quick_search(self):
        # if self.ui.InventoryWineID.text() == '' and self.ui.InventoryLocation.text() == '':
        #     print('none')
        # elif self.ui.InventoryWineID.text() != '' and self.ui.InventoryLocation.text() != '':
        #     print('WineID: ' + self.ui.InventoryWineID.text())
        #     print('Location: ' + self.ui.InventoryLocation.text())
        # elif self.ui.InventoryWineID.text() != '':
        #     print('WineID: ' + self.ui.InventoryWineID.text())
        # elif self.ui.InventoryLocation.text() != '':
        #     print('Location: ' + self.ui.InventoryLocation.text())
        self.refresh_tables()
    
    # @QtCore.Slot()
    # def check_out(self):
    #     pass

    # @QtCore.Slot()
    # def add_copy(self):
    #     pass
    
    # @QtCore.Slot()
    # def edit_bottle(self):
    #     pass
    
    # @QtCore.Slot()
    # def move_bottle(self):
    #     pass
    
    # @QtCore.Slot()
    # def deep_search(self):
    #     pass
    
    # @QtCore.Slot()
    # def update_bottle(self):
    #     pass
    
    # @QtCore.Slot()
    # def add_to_cellar(self):
    #     pass
    
    # @QtCore.Slot()
    # def generate_barcode(self):
    #     pass
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Vinny = QtWidgets.QMainWindow()
    ui = MainInterface()
    Vinny.show()
    sys.exit(app.exec_())