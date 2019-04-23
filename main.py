import PySide2 
from PySide2.QtWidgets import QInputDialog, QLineEdit, QFileDialog, QMessageBox, QFileDialog
from wine_bottle import *
from db_man import DatabaseManager
from main_window import *
import import_export
import shutil
import os


class MainInterface(QtWidgets.QMainWindow, Ui_Vinny):
    def __init__(self):
        super().__init__()
        self.setupUi(Vinny)

        # Connect the buttons to their respective functions
        self.actionBottle.triggered.connect(self.delete_bottle)
        self.actionWine.triggered.connect(self.delete_wine)
        self.actionExport.triggered.connect(self.export_to_excel)
        self.actionImport.triggered.connect(self.import_from_excel)
        self.actionGenerate_Barcode.triggered.connect(self.generate_barcode)
        self.actionBackup_Database.triggered.connect(self.backup_database)
        self.actionPreferences.triggered.connect(self.edit_preferences)
        
        self.InventorySearch.clicked.connect(self.quick_search)
        self.InventoryCheckOut.clicked.connect(self.inv_check_out)
        self.InventoryMoveBottle.clicked.connect(self.inv_move_bottle)
        self.InventoryAddCopy.clicked.connect(self.inv_add_copy)
        self.InventoryEditBottle.clicked.connect(self.inv_edit_bottle)
        self.InventoryTable.cellClicked.connect(self.inv_get_bottle)

        self.AddBottleSearch.clicked.connect(self.ab_deep_search)
        self.AddBottleAdd.clicked.connect(self.ab_add_to_cellar)
        self.AddBottleTable.doubleClicked.connect(self.ab_get_wine)
        self.AddBottleClearFields.clicked.connect(self.ab_clear_fields)
        self.AddBottleUpdate.clicked.connect(self.ab_update_wine)
        self.AddBottleUPC.returnPressed.connect(self.ab_upc_fill)
        self.AddBottleGenerateBarcode.clicked.connect(self.generate_barcode)

        self.HistoryTable.cellClicked.connect(self.hist_get_bottle)

        # Connect all fields in the wines tab to a function to detect modifications
        self.ab_modified_flag = True
        self.AddBottleUPC.textChanged.connect(self.ab_modified)
        self.AddBottleWinery.textChanged.connect(self.ab_modified)
        self.AddBottleAVA.textChanged.connect(self.ab_modified)
        self.AddBottleBlendName.textChanged.connect(self.ab_modified)
        self.AddBottleVarietal.textChanged.connect(self.ab_modified)
        self.AddBottleType.currentIndexChanged.connect(self.ab_modified)
        self.AddBottleVintage.textChanged.connect(self.ab_modified)
        self.AddBottleMSRP.textChanged.connect(self.ab_modified)
        self.AddBottleCurrentValue.textChanged.connect(self.ab_modified)
        self.AddBottleComments.textChanged.connect(self.ab_modified)
        self.AddBottleRating.textChanged.connect(self.ab_modified)

        # Get the names of the collumns at the beginning so we don't have to do that a million times
        # Start by verifying that the database actually exists
        self.db_manager = DatabaseManager()
        self.db_manager.verify_db()
        self.wine_col_names = self.db_manager.db_getcolnames('winedata')
        self.inv_col_names = self.db_manager.db_getcolnames('userinventory')
        self.combined_col_names = self.wine_col_names.copy()
        self.combined_col_names.extend(self.inv_col_names[1:])
        self.location_index  = self.combined_col_names.index('location')

        # Initialize the table sizes so they don't have to be queried every single time
        self.InventoryTable.setColumnCount(len(self.combined_col_names))
        self.InventoryTable.setHorizontalHeaderLabels(self.translate_col_names(self.combined_col_names))
        
        self.AddBottleTable.setColumnCount(len(self.wine_col_names))
        self.AddBottleTable.setHorizontalHeaderLabels(self.translate_col_names(self.wine_col_names))

        self.HistoryTable.setColumnCount(len(self.combined_col_names))
        self.HistoryTable.setHorizontalHeaderLabels(self.translate_col_names(self.combined_col_names))        

        # Create a new bottle object to be manipulated by the user 
        self.bottle = Bottle({}, {})

        # Populate the inventory table so it's ready to go at the start
        self.inv_table_pop(None, None)

        # Disable the 'Generate Barcode' button until it's ready to be used
        self.AddBottleGenerateBarcode.setEnabled(False)

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
                          'region':'Region',
                          'name':'Blend Name',
                          'varietal':'Varietal',
                          'vintage':'Vintage',
                          'wtype':'Type',
                          'msrp':'MSRP',
                          'value':'Value',
                          'comments':'Comments',
                          'rating':'Rating',
                          'bottle_size':'Bottle Size',
                          'location':'Location',
                          'date_in':'Date In',
                          'date_out':'Date Out',
                          'Wine ID':'wine_id',
                          'UPC':'upc',
                          'Winery':'winery',
                          'Region':'region',
                          'Blend Name':'name',
                          'Varietal':'varietal',
                          'Vintage':'vintage',
                          'Type':'wtype',
                          'MSRP':'msrp',
                          'Value':'value',
                          'Comments':'comments',
                          'Rating':'rating',
                          'Bottle Size':'bottle_size',
                          'Location':'location',
                          'Date In':'date_in',
                          'Date Out':'date_out'}

        output_list = []
        for name in input_list:
            output_list.append(translate_dict[name])
        return output_list

    def inv_table_pop(self, wine_id=None, location=None):
        # Populates the inventory table. Called any time there is a possible change
        # Organizes the table based on expected length of the returned entries
        sort_term = self.translate_col_names([self.InventorySortBy.currentText()])[0]
        
        if wine_id or location:
            # If there's a search term, it'll just use the integrated method in wine-bottle
            wine_info = {}
            bottle_info = {}
            if wine_id:
                wine_info['wine_id'] = wine_id
                bottle_info['wine_id'] = wine_id
            if location:
                bottle_info['location'] = location

            self.bottle.clear_bottle()
            self.bottle.wine_info = wine_info
            self.bottle.bottle_info = bottle_info
            bottles = self.bottle.search_bottle()
            inv_rows = []
            if bottles:
                for i, bottle in enumerate(bottles):
                    inv_rows.append(list(self.bottle.wine_info.values()))
                    inv_rows[i].extend(bottle[1:])

        # Craft the SQL search query. I suspect having SQL doing the sorting is a tad faster.
        # If no terms specified, return all entries
        else:
            arg = 'SELECT * FROM winedata JOIN userinventory USING (wine_id) WHERE '
            arg += 'date_out IS NULL ORDER BY ' + sort_term
            if self.InventorySortAsc.isChecked():
                arg += ' ASC'
            else:
                arg += ' DESC'
            inv_rows = list(self.db_manager.db_fetch(arg, rows='all'))

        # Iteratively fills the table
        self.InventoryTable.setRowCount(0)
        if inv_rows:
            for row_num, row in enumerate(inv_rows):
                self.InventoryTable.insertRow(row_num)
                for col_num, col_entry in enumerate(row):
                        self.InventoryTable.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(str(col_entry)))
            self.InventoryTable.selectRow(0)
        else:
            self.bottle.clear_bottle()
        
        # Populates the history table as well
        self.history_table_pop()

    def history_table_pop(self):
        # Populates the history table as needed. Functions in mostly the same 
        # way as the inv_table_pop method
        arg = 'SELECT * FROM winedata JOIN userinventory USING (wine_id) WHERE date_out IS NOT NULL ORDER BY date_out'
        hist_rows = list(self.db_manager.db_fetch(arg, rows='all'))

        self.HistoryTable.setRowCount(0)
        for row_num, row in enumerate(hist_rows):
            self.HistoryTable.insertRow(row_num)
            for col_num, col_entry in enumerate(row):
                self.HistoryTable.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(str(col_entry)))

    def ab_fill_fields(self, wine_info):
        # Takes an input dictionary and filles the add bottle fields
        for term in wine_info:
            wine_info[term] = str(wine_info[term])
            
        self.AddBottleUPC.setText(wine_info['upc'])
        self.AddBottleWinery.setText(wine_info['winery'])
        self.AddBottleAVA.setText(wine_info['region'])
        self.AddBottleBlendName.setText(wine_info['name'])
        self.AddBottleVarietal.setText(wine_info['varietal'])
        self.AddBottleType.setCurrentText(wine_info['wtype'])
        self.AddBottleVintage.setText(wine_info['vintage'])
        self.AddBottleMSRP.setText(wine_info['msrp'])
        self.AddBottleCurrentValue.setText(wine_info['value'])
        self.AddBottleComments.setText(wine_info['comments'])
        self.AddBottleRating.setText(wine_info['rating'])

        # Set modified flag to false so it doesn't make duplicates
        self.ab_modified_flag = False

    def get_other_size(self):
        new_size, ok_pressed = QInputDialog.getText(self, 'Other Size', 'Enter Custom Size:', QLineEdit.Normal, '')
        if ok_pressed:
            return new_size

    @QtCore.Slot()
    def hist_get_bottle(self):
        # Activated when a table item is selected. Grabs all info about a specific bottle and stores
        # it in the bottle object. 

        # First, ensure that the dictionary is empty to prevent extra data being added
        self.bottle.clear_bottle()

        # Get the current row that has been selected. 
        selection_row = self.HistoryTable.currentRow()
        # Highlight the whole row to be more visible (quality of life thing)
        self.HistoryTable.selectRow(selection_row)

        # Assign all items to the dictionary based on the col names
        for i, term in enumerate(self.wine_col_names):
            self.bottle.wine_info[term] = self.HistoryTable.item(selection_row, i).text()
        # Bottle info needs to be offset since its at the end
        for i, term in enumerate(self.inv_col_names):
            self.bottle.bottle_info[term] = self.HistoryTable.item(selection_row, i + len(self.wine_col_names) - 1).text()
        # wine_id only appears at the beginning, make sure it's editted properly
        self.bottle.bottle_info['wine_id'] = self.bottle.wine_info['wine_id']

    @QtCore.Slot()
    def inv_get_bottle(self):
        # Activated when a table item is selected. Grabs all info about a specific bottle and stores
        # it in the bottle object. 

        # First, ensure that the dictionary is empty to prevent extra data being added
        self.bottle.clear_bottle()

        # Get the current row that has been selected. 
        selection_row = self.InventoryTable.currentRow()
        # Highlight the whole row to be more visible (quality of life thing)
        self.InventoryTable.selectRow(selection_row)

        # Assign all items to the dictionary based on the col names
        for i, term in enumerate(self.wine_col_names):
            self.bottle.wine_info[term] = self.InventoryTable.item(selection_row, i).text()
        # Bottle info needs to be offset since its at the end
        for i, term in enumerate(self.inv_col_names):
            self.bottle.bottle_info[term] = self.InventoryTable.item(selection_row, i + len(self.wine_col_names) - 1).text()
        # wine_id only appears at the beginning, make sure it's editted properly
        self.bottle.bottle_info['wine_id'] = self.bottle.wine_info['wine_id']

    @QtCore.Slot()
    def quick_search(self):
        # Checks if there are search terms and calls the inv_table_pop method
        wine_id = None
        location = None
        if self.InventoryWineID.text():
            wine_id = self.InventoryWineID.text()
        if self.InventoryLocation.text():
            location = self.InventoryLocation.text()
        self.inv_table_pop(wine_id, location)
    
    @QtCore.Slot()
    def inv_check_out(self):
        # Checks out the selected bottle with the integrated method
        self.bottle.check_out()
        self.quick_search()

    @QtCore.Slot()
    def inv_add_copy(self, new_loc=None, new_size=None):
        # Adds a copy of the selected bottle by asking for a new size and location
        bottle_sizes = [self.AddBottleBottleSize.itemText(i) for i in range(self.AddBottleBottleSize.count())]
        if not new_size:
            new_size, ok_pressed = QInputDialog.getItem(self, 'New Size', 'Select New Bottle Size:', bottle_sizes, 2, False)
            if ok_pressed == True:
                pass
            if new_size == 'Other...':
                new_size = self.get_other_size()
        self.bottle.bottle_info['bottle_size'] = new_size
        if not new_loc:
            new_loc, ok_pressed = QInputDialog.getText(self, 'New Location', 'Enter new location:', QLineEdit.Normal, '')
            if ok_pressed == True:
                pass
        self.bottle.bottle_info['location'] = new_loc
        self.bottle.add_new()
        self.quick_search()

    @QtCore.Slot()
    def inv_edit_bottle(self):
        # Switches to the Wines tab and fills the fields with the selected
        # bottle info. Only activates if a wine has been selected
        if 'wine_id' in self.bottle.bottle_info:
            self.main_tab.setCurrentIndex(1)
            self.ab_fill_fields(self.bottle.wine_info)
    
    @QtCore.Slot()
    def inv_move_bottle(self):
        # Moves a bottle by querying the user for a new location and updating
        # the row
        new_location, ok_pressed = QInputDialog.getText(self, 'Move Bottle', 'Enter new location:', QLineEdit.Normal, '')
        if ok_pressed == True:
            self.bottle.update_bottle(new_info={'location':new_location})
        self.quick_search()

    @QtCore.Slot()
    def ab_deep_search(self):
        # Grabs the text from each box and searches for wines matching the
        # criteria. First creates a dictionary from the inputs
        wine_info = {"upc":self.AddBottleUPC.text(),
                     "winery":self.AddBottleWinery.text(),
                     "region":self.AddBottleAVA.text(),
                     "name":self.AddBottleBlendName.text(),
                     "varietal":self.AddBottleVarietal.text(),
                     "wtype":self.AddBottleType.currentText(),
                     "vintage":self.AddBottleVintage.text(),
                     "msrp":self.AddBottleMSRP.text(),
                     "value":self.AddBottleCurrentValue.text(),
                     "rating":self.AddBottleRating.text(),
                     "comments":self.AddBottleComments.toPlainText()}

        # Filters out empty text boxes
        for term in wine_info:
            if not wine_info[term]:
                wine_info[term] = None

        # For simplicity, bypasses the object since it isn't really needed here
        table_rows = search_db(wine_info, 'winedata', in_cellar=False)

        # Iteratively populates the table
        self.AddBottleTable.setRowCount(0)
        if table_rows:
            for row_num, row in enumerate(table_rows):
                self.AddBottleTable.insertRow(row_num)
                for col_num, col in enumerate(row):
                    self.AddBottleTable.setItem(row_num, col_num, QtWidgets.QTableWidgetItem(str(col)))

    @QtCore.Slot()
    def ab_get_wine(self):
        # Activated when a row is double clicked on the wine table
        # Autofills all the fields in the area to be modified

        # Clear the bottle so that important stuff can be stored
        self.bottle.clear_bottle()
        
        # Get current row and highlight the whole row
        selection_row = self.AddBottleTable.currentRow()
        self.AddBottleTable.selectRow(selection_row)

        # Assign all items to the fields by iterating through
        # and assigning to a dictionary
        wine_info = {}
        for i, term in enumerate(self.wine_col_names):
            if self.AddBottleTable.item(selection_row, i).text() != 'None':
                wine_info[term] = self.AddBottleTable.item(selection_row, i).text()
            else:
                wine_info[term] = ''

        # Assign the wine_id to the current bottle object so we know it's 
        # a duplicate
        self.bottle.bottle_info['wine_id'] = self.AddBottleTable.item(selection_row, 0).text()
        self.bottle.wine_info['wine_id'] = self.AddBottleTable.item(selection_row, 0).text()

        self.ab_fill_fields(wine_info)

    @QtCore.Slot()
    def ab_modified(self):
        self.ab_modified_flag = True
        self.bottle.clear_bottle()
        self.AddBottleGenerateBarcode.setEnabled(False)

    @QtCore.Slot()
    def ab_update_wine(self):
        if 'wine_id' in self.bottle.wine_info and self.ab_modified_flag == True:
            wine_info = {"upc":self.AddBottleUPC.text(),
                        "winery":self.AddBottleWinery.text(),
                        "region":self.AddBottleAVA.text(),
                        "name":self.AddBottleBlendName.text(),
                        "varietal":self.AddBottleVarietal.text(),
                        "wtype":self.AddBottleType.currentText(),
                        "vintage":self.AddBottleVintage.text(),
                        "msrp":self.AddBottleMSRP.text(),
                        "value":self.AddBottleCurrentValue.text(),
                        "rating":self.AddBottleRating.text(),
                        "comments":self.AddBottleComments.toPlainText()}
            for term in wine_info:
                if term not in self.bottle.wine_info or wine_info[term] != self.bottle.wine_info[term]:
                    self.bottle.wine_info[term] = wine_info[term]
            self.bottle.update_wine()
            self.inv_table_pop()

    @QtCore.Slot()
    def ab_clear_fields(self):
        # Clear all fields, including the current bottle object
        self.AddBottleUPC.clear()
        self.AddBottleWinery.clear()
        self.AddBottleAVA.clear()
        self.AddBottleBlendName.clear()
        self.AddBottleVarietal.clear()
        self.AddBottleType.setCurrentIndex(0)
        self.AddBottleVintage.clear()
        self.AddBottleMSRP.clear()
        self.AddBottleCurrentValue.clear()
        self.AddBottleComments.clear()
        self.AddBottleRating.clear()
        self.AddBottleLocation.clear()
        self.AddBottleQty.clear()

        self.bottle.clear_bottle()

        # Disable the barcode button
        self.AddBottleGenerateBarcode.setEnabled(False)

        self.ab_deep_search()
    
    @QtCore.Slot()
    def ab_add_to_cellar(self):
        # Adds a new bottle to the cellar. If the wine_id exists, it's a copy
        # and can be added as such. Otherwise a new bottle is added. 
        new_size = self.AddBottleBottleSize.currentText()
        if new_size == 'Other...':
            new_size = self.get_other_size()
        if 'wine_id' in self.bottle.bottle_info or 'wine_id' in self.bottle.wine_info:
            if self.AddBottleSelLocation.isChecked():
                new_loc = self.AddBottleLocation.text()
                self.inv_add_copy(new_size=new_size, new_loc=new_loc)
                
            else:
                for i in range(int(self.AddBottleQty.text())):
                   self.inv_add_copy(new_size=new_size)
        else:
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

            bottle_info = {"bottle_size":new_size}
            
            if wine_info['wtype'] == 'Other...':
                new_type, ok_pressed = QInputDialog.getText(self, 'Other Type', 'Enter Custom Type:', QLineEdit.Normal, '')
                if ok_pressed:
                    wine_info['wtype'] = new_type

            for term in wine_info:
                if wine_info[term] == '':
                    wine_info[term] = None
            for term in bottle_info:
                if bottle_info[term] == '':
                    bottle_info[term] = None

            self.bottle.clear_bottle()
            if self.AddBottleSelLocation.isChecked() == True:
                bottle_info["location"] = self.AddBottleLocation.text()
                self.bottle.wine_info = wine_info
                self.bottle.bottle_info=bottle_info
                wine_id = self.bottle.add_new()
            else:
                for i in range(int(self.AddBottleQty.text())):
                    next_location, ok_pressed = QInputDialog.getText(self, "Bottle {0}".format(i+1), "Enter location for Bottle {0}:".format(i+1), QLineEdit.Normal, "")
                    if ok_pressed == True:
                        bottle_info['location'] = next_location
                        self.bottle.wine_info = wine_info
                        self.bottle.bottle_info=bottle_info
                        wine_id = self.bottle.add_new()
        self.bottle.clear_bottle()
        self.quick_search()
        self.bottle.wine_info['wine_id'] = wine_id

        # Enable the barcode button now that there's a wine id
        self.AddBottleGenerateBarcode.setEnabled(True)
    
    @QtCore.Slot()
    def ab_upc_fill(self):
        upc = self.AddBottleUPC.text()
        self.bottle.clear_bottle()
        self.bottle.wine_info['upc'] = upc
        self.bottle.search_wine()
        self.ab_fill_fields(wine_info=self.bottle.wine_info)

    @QtCore.Slot()
    def delete_bottle(self):
        # Deletes bottle from the database entirely. This is different
        # from checking out a bottle because the entire thing is removed.
        # This is permenant and dangerous, so it uses a message box to 
        # confirm.
        if 'wine_id' in self.bottle.bottle_info and self.bottle.bottle_info['wine_id'] != None:
            msg_box = QMessageBox()
            msg_box.setText("WARNING: You are about to delete this bottle from the database. You cannot undo this. Continue?")
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Cancel)
            msg_box.setIcon(QMessageBox.Warning)
            ret = msg_box.exec_()
        
            if ret == QMessageBox.Ok:
                self.bottle.delete_bottle()
            else:
                return
            
            self.inv_table_pop()

    @QtCore.Slot()
    def delete_wine(self):
        # Deletes wine from the database entirely. This is permenant and 
        # dangerous, so it uses a message box to confirm.
        if 'wine_id' in self.bottle.wine_info and self.bottle.wine_info['wine_id'] != None:
            msg_box = QMessageBox()
            msg_box.setText("WARNING: You are about to delete this wine from the database, along with all bottles of it. You cannot undo this. Continue?")
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Cancel)
            msg_box.setIcon(QMessageBox.Warning)
            ret = msg_box.exec_()
        
            if ret == QMessageBox.Ok:
                self.bottle.delete_wine()
            else:
                return
            
            self.inv_table_pop()

    @QtCore.Slot()
    def export_to_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export...", "", "Excel Files (*.xlsx)")
        import_export.export_db(path)

    @QtCore.Slot()
    def import_from_excel(self):
        msg_box = QMessageBox()
        msg_box.setText("Use one of the available templates to import your collection from an Excel spreadsheet.")
        msg_box.setInformativeText("Note: do not change the filename of the template.")
        msg_box.setStandardButtons(QMessageBox.Open | QMessageBox.Cancel)
        expanded = msg_box.addButton('Create Expanded...', QMessageBox.ApplyRole)
        condensed = msg_box.addButton('Create Condensed...', QMessageBox.ApplyRole)
        msg_box.setDefaultButton(QMessageBox.Cancel)
        ret = msg_box.exec_()

        if msg_box.clickedButton() == expanded:
            path = QFileDialog.getExistingDirectory(self, "Select Directory for Template...") + '/'
            import_export.generate_sheet(path, expanded=True)
        elif msg_box.clickedButton() == condensed:
            path = QFileDialog.getExistingDirectory(self, "Select Directory for Template...") + '/'
            import_export.generate_sheet(path, expanded=False)
        elif ret == QMessageBox.Open:
            path = QFileDialog.getOpenFileName(self, "Select Filled-Out Template...")
            import_export.import_db(path[0])

    @QtCore.Slot()
    def backup_database(self):
        path = QFileDialog.getSaveFileName(self, "Backup...", '', 'Database Files (*.db)')
        shutil.copyfile(os.getcwd() + '/wineinv_data.db', path[0])

    @QtCore.Slot()
    def generate_barcode(self):
        barcode_img = self.bottle.generate_label()
        msg_box = QMessageBox()
        msg_box.setText("Lable has been created. Select one of the options below to continue:")
        msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)
        pr_button = msg_box.addButton('Print', QMessageBox.ApplyRole)
        msg_box.setDefaultButton(QMessageBox.Cancel)
        ret = msg_box.exec_()

        if ret != QMessageBox.Cancel:
            if msg_box.clickedButton() == pr_button:
                self.bottle.print_label()
            elif ret == QMessageBox.Save:
                path = QFileDialog.getSaveFileName(self, "Save As...", '', 'Picture Files (*.png)')[0]
                shutil.copyfile(barcode_img + '.png', path)

    @QtCore.Slot()
    def edit_preferences(self):
        msg_box = QMessageBox()
        msg_box.setText('Coming soon!')
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()                


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Vinny = QtWidgets.QMainWindow()
    ui = MainInterface()
    Vinny.show()
    sys.exit(app.exec_())