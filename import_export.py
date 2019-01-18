from openpyxl import *
from db_man import DatabaseManager
import os


def export_db(path):
    # Exports the database to an excel file at the specified
    # file path
    # First, create a workbook. Condensed uses Qty instead of location
    # Expanded preserves location data
    exp_wb = Workbook()
    exp_condensed = exp_wb.active
    exp_condensed.title = 'Condensed Inventory'
    exp_full = exp_wb.create_sheet('Expanded Inventory')

    # Setup the pages to have the right headers. Grab lists of the col names and merge them
    db_export = DatabaseManager()
    col_keys = db_export.db_getcolnames('winedata')
    col_keys.extend(db_export.db_getcolnames('userinventory')[2:])
    exp_full.append(col_keys)

    # Replace the 'location' tag with 'qty' and add it to the condensed table and remove the dates
    qty_index = col_keys.index('location')
    col_keys[qty_index] = 'qty'
    date_index = col_keys.index('date_in')
    del col_keys[date_index:date_index+2]
    exp_condensed.append(col_keys)

    # now, grab everything from each table and store it in a list of lists
    inv_rows = db_export.db_fetch('SELECT * FROM userinventory ORDER BY wine_id', rows='all')


    # Add everything to the excel file sequentially
    # First, initialize the variables that may not exist 
    # until later in the loop
    old_id = None
    qty = 0
    dup_row = None
    old_row = None

    # Iterate through each of the entries in the inventory For each
    # entry, look it up in the winedata table and add create one 
    # long list which the relevant data. This is a little slower,
    # but more memory efficient. Write that to the extended page. 
    for i in range(len(inv_rows)):
        write_row = list(db_export.db_fetch('SELECT * FROM winedata WHERE wine_id=?', (inv_rows[i][0],)))
        write_row.extend(inv_rows[i][2:])
        exp_full.append(write_row)
        # Remove the date in/out entries
        del write_row[date_index:date_index+2]
        # The condensed row will run one iteration behind in order
        # to check for another of the same bottle. It is initialized
        # as none to avoid a definition error in the first loop
        if old_row != None:
            # if the wine id is the same, increment the counter
            if old_id == inv_rows[i][0]:
                qty += 1
            # if it's not, incriment the counter to account for the
            # last bottle, write it, and reset qty counter
            else:
                qty += 1
                old_row[qty_index] = qty
                exp_condensed.append(old_row)
                qty = 0
        # set old row and old id so we can check it against the 
        # next index on the next cycle
        old_row = write_row.copy()
        old_id = inv_rows[i][0]
    # Because the condensed table runs one cycle behind, we have to
    # run the write command one more time to finish the last entry
    qty += 1
    old_row[qty_index] = qty
    exp_condensed.append(old_row)


    # Save the file
    exp_wb.save(path)

def import_db(path):
    # This function imports an excel file (from a specified format),
    # checks for duplicates, and enters the non-duplicates into the
    # database. (Note: duplicates refer to the winedata table, not
    # the inventory. That will allow any)
    import_wb = load_workbook(path)
    import_ws = import_wb.active
    


path = 'test.xlsx'
#export_db(path)
import_db(path)