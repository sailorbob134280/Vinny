import PySide2
from PySide2.QtWidgets import QInputDialog, QLineEdit
from wine_bottle import *
from db_man import DatabaseManager
from main_window import *

class MainInterface(QtWidgets.QMainWindow, Ui_Vinny):
    def __init__(self):
        super().__init__()
        self.setupUi(Vinny)

        self.InventorySearch.clicked.connect(self.quick_search)
        self.InventoryCheckOut.clicked.connect(self.check_out)

        self.AddBottleAdd.clicked.connect(self.add_to_cellar)

        self.inv_table_pop(None, None)

    def translate_col_names(self, input_list):
        # Translates code names to pretty names and back. It does this
        # using a dict with both directions in it, since all entries are
        # unique. Hacky? Yes. Does it work? Also yes. Does it really take
        # up that much space? Nope. 
        #
        # Takes a list, outputs another list.
        translate_dict = {'wine_id':'Wine ID',
                          'upc':'UPC',
                          'winery':'Winery',
                          'region':'AVA',
                          'name':'Blend Name',
                          'varietal':'Varietal',
                          'vintage':'Vintage',
                          'wtype':'Type',
                          'msrp':'MSRP',
                          'value':'Value',
                          'comments':'Comments',
                          'bottle_size':'Bottle Size',
                          'location':'Location',
                          'date_in':'Date In',
                          'date_out':'Date Out',
                          'Wine ID':'wine_id',
                          'UPC':'upc',
                          'Winery':'winery',
                          'AVA':'region',
                          'Blend Name':'name',
                          'Varietal':'varietal',
                          'Vintage':'vintage',
                          'Type':'wtype',
                          'MSRP':'msrp',
                          'Value':'value',
                          'Comments':'comments',
                          'Bottle Size':'bottle_size',
                          'Location':'location',
                          'Date In':'date_in',
                          'Date Out':'date_out'}

        output_list = []
        for name in input_list:
            output_list.append(translate_dict[name])
        return output_list

    def inv_table_pop(self, wine_id, location):
        db_table_setup = DatabaseManager()
        col_names = db_table_setup.db_getcolnames('winedata')
        col_names.extend(db_table_setup.db_getcolnames('userinventory')[1:])
        self.InventoryTable.setColumnCount(len(col_names))
        col_labels = self.translate_col_names(col_names)
        self.InventoryTable.setHorizontalHeaderLabels(col_labels)
        sort_term = self.translate_col_names([self.InventorySortBy.currentText()])[0]
        
        if wine_id == None and location == None:
            arg = 'SELECT * FROM winedata JOIN userinventory USING (wine_id) WHERE '
            arg += 'date_out IS NULL ORDER BY ' + sort_term
            if self.InventorySortAsc.isChecked():
                arg += ' ASC'
            else:
                arg += ' DESC'
            inv_rows = list(db_table_setup.db_fetch(arg, rows='all'))
        else:
            if wine_id == None:
                wine_info = None
            else:
                wine_info = {'wine_id':wine_id}
            if location == None:
                bottle_info = {'location':None}
            else:
                bottle_info = {'location':location}
                
            find_bottles = Bottle(wine_info=wine_info, bottle_info=bottle_info)
            bottles = find_bottles.search_bottle()
            print(bottles)
            inv_rows = []
            for i, bottle in enumerate(bottles):
                inv_rows.append(list(find_bottles.wine_info.values()))
                inv_rows[i].extend(bottle[1:])
            print(inv_rows)

        self.InventoryTable.setRowCount(0)
        for row_num, row in enumerate(inv_rows):
            self.InventoryTable.insertRow(row_num)
            for col_num, col_entry in enumerate(row):
                self.InventoryTable.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(str(col_entry)))

    @QtCore.Slot()
    def quick_search(self):
        wine_id = None
        location = None
        if self.InventoryWineID.text() != '':
            wine_id = self.InventoryWineID.text()
        if self.InventoryLocation.text() != '':
            location = self.InventoryLocation.text()
        self.inv_table_pop(wine_id, location)
    
    @QtCore.Slot()
    def check_out(self):
        selection_row = self.InventoryTable.currentRow()
        bottle_info = {'wine_id':self.InventoryTable.item(selection_row, 0).text()}
        bottle_checkout = Bottle(wine_info=None, bottle_info=bottle_info)
        bottle_checkout.check_out()
        self.quick_search()

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
    
    @QtCore.Slot()
    def add_to_cellar(self):
        wine_info = {"upc":self.AddBottleUPC.text(),
                     "winery":self.AddBottleWinery.text(),
                     "region":self.AddBottleAVA.text(),
                     "name":self.AddBottleBlendName.text(),
                     "varietal":self.AddBottleVarietal.text(),
                     "wtype":self.AddBottleType.currentText(),
                     "vintage":self.AddBottleVintage.text(),
                     "msrp":self.AddBottleMSRP.text(),
                     "value":self.AddBottleCurrentValue.text(),
                     "comments":self.AddBottleComments.toPlainText()}

        bottle_info = {"bottle_size":self.AddBottleBottleSize.currentText()}
        
        for term in wine_info:
            if wine_info[term] == '':
                wine_info[term] = None
        for term in bottle_info:
            if bottle_info[term] == '':
                bottle_info[term] = None

        if self.AddBottleSelLocation.isChecked() == True:
            bottle_info["location"] = self.AddBottleLocation.text()
            new_bottle = Bottle(wine_info=wine_info, bottle_info=bottle_info)
            new_bottle.add_new()
        else:
            for i in range(int(self.AddBottleQty.text())):
                next_location, ok_pressed = QInputDialog.getText(self, "Bottle {0}".format(i+1), "Enter location for Bottle {0}:".format(i+1), QLineEdit.Normal, "")
                if ok_pressed == True:
                    bottle_info['location'] = next_location
                    new_bottle = Bottle(wine_info=wine_info, bottle_info=bottle_info)
                    new_bottle.add_new()
    
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