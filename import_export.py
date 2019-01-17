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


    # Ok, shits fucked here. Not sure why. Time for dinner
    old_id = None
    qty = 0
    dup_row = None
    for i in range(len(inv_rows)):
        write_row = list(db_export.db_fetch('SELECT * FROM winedata WHERE wine_id=?', (inv_rows[i][0],)))
        write_row.extend(inv_rows[i][2:])
        exp_full.append(write_row)
        write_row[qty_index] = qty
        del write_row[date_index:date_index+2]
        if old_id == inv_rows[i][0]:
            qty += 1
            dup_row = write_row.copy()
        else:
            qty += 1
            if dup_row == None:
                write_row[qty_index] = qty
                exp_condensed.append(write_row)
            else:
                dup_row[qty_index] = qty
                exp_condensed.append(dup_row)
                dup_row = None
            qty = 0
        old_id = inv_rows[i][0]



    # Save the file
    exp_wb.save(path)

path = 'test.xlsx'
export_db(path)


