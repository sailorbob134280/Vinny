from db_man import DatabaseManager
import datetime


def cleanup_dbinput(input_dict):
    # if the term is not used, it is discarded from the dictionary
    terms = {}
    for wkey in input_dict:
        if input_dict[wkey] != None and input_dict[wkey] != 'None':
            terms[wkey] = input_dict[wkey]
    return terms

def search_db(search_input, table='userinventory', in_cellar=True, sort_by=None):
    # searches for a wine in the database that resembles the input
    # first, assign the inputs to a list to be cleaned up
    # this function takes a list of the following format:
    # search_input = [wine_id, upc, winery, region,
    #                 name, varietal, wtype,
    #                 vintage, msrp, value]
    # it is critical that the list is complete, even if some
    # of the values are null

    terms = cleanup_dbinput(search_input)

    # craft the sql query string
    if table == 'both':
        arg = 'SELECT * FROM winedata JOIN userinventory USING (wine_id) WHERE '
    else:
        arg = 'SELECT * FROM ' + table + ' WHERE '
    for term in terms:
        arg += '{0} LIKE {1} AND '.format(term, ':' + term)
        terms[term] = '%' + terms[term] + '%'
    arg = arg.rstrip(' AND ')
    if in_cellar == True and table != 'winedata':
        arg += ' AND date_out IS NULL'
    if sort_by != None:
        arg += ' ORDER BY ' + sort_by

    # finally, call the search function from the db_man object
    db_search = DatabaseManager()
    result = db_search.db_fetch(arg, terms, 'all')
    if result:
        return result
    else:
        return None

def fetch_db(fetch_input, table='userinventory', in_cellar=True, sort_by=None):
    # fetches a row from the database
    # shoud be faster than searching since it doesn't have to guess
    terms = cleanup_dbinput(fetch_input)

    if table == 'both':
        arg = 'SELECT * FROM winedata JOIN userinventory USING (wine_id) WHERE '
    else:
        arg = 'SELECT * FROM ' + table + ' WHERE '
    for term in terms:
        arg += '{0}={1} AND '.format(term, ':' + term)
    arg = arg.rstrip(' AND ')
    if in_cellar == True and table != 'winedata':
        arg += ' AND date_out IS NULL'
    if sort_by != None:
        arg += ' ORDER BY ' + sort_by
    fetch = DatabaseManager()
    return fetch.db_fetch(arg, terms, 'all')

def lookup_db(lookup_number, table='userinventory', in_cellar=True, sort_by=None):
    # This is a function to quickly lookup based on either a upc or wine_id
    # This is really similar to the fetch_db function (and may end up
    # replacing it).
    lookup = DatabaseManager()
    placeholders = [lookup_number]
    if table == 'both':
        arg = 'SELECT * FROM winedata JOIN userinventory USING (wine_id) WHERE '
    else:
        arg = 'SELECT * FROM ' + table + ' WHERE '
    arg += 'wine_id=?'
    if table != 'userinventory':
        arg += ' OR upc=?'
        placeholders.append(lookup_number)
    if in_cellar == True and table != 'winedata':
        arg += ' AND date_out IS NULL'
    if sort_by != None:
        arg += ' ORDER BY ' + sort_by
    return lookup.db_fetch(arg, tuple(placeholders), 'all')

def enter_db(entry_input, table='userinventory',ret_id=False):
    # enters a wine into the database
    # this function takes a list of the following format:
    # entry_input = [wine_id, upc, winery, region,
    #                name, varietal, wtype,
    #                vintage, msrp, value]
    # it is critical that the list is complete, even if some
    # of the values are null
    db_enter = DatabaseManager()
    terms = cleanup_dbinput(entry_input)

    #arg = 'INSERT INTO ' + table + ' (upc, winery, region, name, varietal, wtype, vintage, msrp, value) VALUES (?,?,?,?,?,?,?,?,?)'
    arg = 'INSERT INTO ' + table + ' ('
    values = '('
    for term in terms:
        arg +=  term + ', '
        values += ':'+ term + ', '
    values = values.rstrip(', ') + ')'
    arg = arg.rstrip(', ') + ') VALUES ' + values

    return db_enter.db_execute(arg, terms, ret_id)

def drop_row(wine_id, rowid=None, table='userinventory'):
    # drops a row from the database, if for example it is 
    # entered by mistake 
    # this function only takes a wine_id input, which forces
    # the wine to be positively identified before it is 
    # deleted
    # This also allows the table to be selected. By default,
    # the table is the user inventory (which is less dangerous)
    terms = [wine_id]
    arg = 'DELETE FROM ' + table + ' WHERE wine_id = ?'
    if rowid:
        arg += ' AND rowid = ?'
        terms.append(rowid)

    terms = tuple(terms)
    db_drop = DatabaseManager()
    db_drop.db_execute(arg, terms)

def update_winedata_row(update_input):
    # updates a specific row in a specified table
    # this function takes a list of the following format:
    # entry_input = [wine_id, upc, winery, region,
    #                name, varietal, wtype,
    #                vintage, msrp, value]
    terms = cleanup_dbinput(update_input)
    arg = 'UPDATE winedata SET '
    for term in terms:
        arg += term + ' = :' + term + ', '
    arg = arg.rstrip(', ')
    arg += ' WHERE wine_id = :wine_id'

    db_update = DatabaseManager()
    db_update.db_execute(arg, terms)

def update_userinv_row(update_input, rowid):
    # Updates a userinventory row using the row id (so duplicates aren't
    # affected). This will mostly be used for moving and checking out bottles
    arg = 'UPDATE userinventory SET '
    for term in update_input:
        arg += term + ' = :' + term + ', '
    arg = arg.rstrip(', ')
    arg += ' WHERE rowid = ' + str(rowid)

    inv_update = DatabaseManager()
    inv_update.db_execute(arg, update_input)

def get_rowid(entry_input, table='userinventory'):
    # Returns the row id of the desired input
    terms = cleanup_dbinput(entry_input)

    arg = 'SELECT rowid FROM ' + table + ' WHERE '
    for term in terms:
        arg += '{0} = {1} AND '.format(term, ':' + term)
    arg = arg.rstrip(' AND ')

    getid = DatabaseManager()
    return getid.db_fetch(arg, terms, 'one')[0]


####################################################################
############################ Test Code #############################
####################################################################

# userinv_dict = {"wine_id":input_list[0],
#                 "bottle_size":input_list[2],
#                 "location":input_list[3],
#                 "comments":input_list[4],
#                 "date_in":input_list[5],
#                 "date_out":input_list[6]}

# winedata_dict = {"wine_id":None,
#                  "upc":'081128011680',
#                  "winery":'Burnt Bridge Cellars',
#                  "region":'Walla Walla',
#                  "name":None,
#                  "varietal":'Cabernet Sauvignon',
#                  "wtype":'Table',
#                  "vintage":2012,
#                  "msrp":'$35',
#                  "value":'$35'}

# winedata_dict = {"winery":'ur'}

# enter_db(winedata_dict, 'winedata')
# drop_row(winedata_dict['wine_id'], 'winedata')
# print(search_db(winedata_dict, 'both'))
# find_bottle = input('Enter a bottle ID: ')
# print(lookup_db(find_bottle, 'winedata'))