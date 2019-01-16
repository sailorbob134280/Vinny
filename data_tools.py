from db_man import DatabaseManager
import datetime

def cleanup_dbinput(input_dict, table):
    # first, figure out which table the input is for 
    # and assign the inputs to a dictionary (including none)
    # if table is 'userinventory':
    #     input_dict = {"wine_id":input_list[0],
    #                   "user_id":input_list[1],
    #                   "bottle_size":input_list[2],
    #                   "location":input_list[3],
    #                   "comments":input_list[4],
    #                   "date_in":input_list[5],
    #                   "date_out":input_list[6]}
    # elif table is 'winedata':
    #     input_dict = {"wine_id":input_list[0],
    #                   "upc":input_list[1],
    #                   "winery":input_list[2],
    #                   "region":input_list[3],
    #                   "name":input_list[4],
    #                   "varietal":input_list[5],
    #                   "wtype":input_list[6],
    #                   "vintage":input_list[7],
    #                   "msrp":input_list[8],
    #                   "value":input_list[9]}
    # elif table is 'userdata':
    #     input_dict = {"user_id":input_list[0],
    #                   "username":input_list[1],
    #                   "password":input_list[2],
    #                   "cellar_space":input_list[3]}
    # else:
    #     raise Exception('''Table does not exist! Please contact the devs about this... You really shouldn't see this.''')

    # if the term is not used, it is discarded from the dictionary
    terms = {}
    for wkey in input_dict:
        if input_dict[wkey] is not None:
            terms[wkey] = input_dict[wkey]
    return terms

def search_db(search_input, table='userinventory'):
    # searches for a wine in the database that resembles the input
    # first, assign the inputs to a list to be cleaned up
    # this function takes a list of the following format:
    # search_input = [wine_id, upc, winery, region,
    #                 name, varietal, wtype,
    #                 vintage, msrp, value]
    # it is critical that the list is complete, even if some
    # of the values are null

    terms = cleanup_dbinput(search_input, table)

    # craft the sql query string
    arg = 'SELECT * FROM ' + table + ' WHERE '
    for term in terms:
        arg += '{0} LIKE {1} AND '.format(term, ':' + term)
    arg = arg.rstrip(' AND ')

    # finally, call the search function from the db_man object
    db_search = DatabaseManager()
    result = db_search.db_fetch(arg, terms, 'all')
    if len(result) is not 0:
        return result
    else:
        return None

def fetch_db(fetch_input, table='userinventory'):
    # fetches a row from the database
    # shoud be faster than searching, but only returns one row 
    # (so should only be used when one value is expected to be returned)
    terms = cleanup_dbinput(fetch_input, table)

    arg = 'SELECT * FROM ' + table + ' WHERE '
    for term in terms:
        arg += '{0}={1} AND '.format(term, ':' + term)
    arg = arg.rstrip(' AND ')

    fetch = DatabaseManager()
    return fetch.db_fetch(arg, terms, 'one')

def lookup_db(lookup_number, table='userinventory'):
    # This is a function to quickly lookup based on either a upc or wine_id
    # This is really similar to the fetch_db function (and may end up
    # replacing it).
    lookup = DatabaseManager()
    arg = 'SELECT * FROM ' + table + ' WHERE upc=?'
    result = lookup.db_fetch(arg, (lookup_number,), 'one')
    if result is None:
        arg = 'SELECT * FROM ' + table + ' WHERE wine_id=?'
        return lookup.db_fetch(arg, (lookup_number,), 'one')
    else:
        return result

def enter_db(entry_input, table='userinventory'):
    # enters a wine into the database
    # this function takes a list of the following format:
    # entry_input = [wine_id, upc, winery, region,
    #                name, varietal, wtype,
    #                vintage, msrp, value]
    # it is critical that the list is complete, even if some
    # of the values are null
    db_enter = DatabaseManager()
    terms = cleanup_dbinput(entry_input, table)

    #arg = 'INSERT INTO ' + table + ' (upc, winery, region, name, varietal, wtype, vintage, msrp, value) VALUES (?,?,?,?,?,?,?,?,?)'
    arg = 'INSERT INTO ' + table + ' ('
    values = '('
    for term in terms:
        arg +=  term + ', '
        values += ':'+ term + ', '
    values = values.rstrip(', ') + ')'
    arg = arg.rstrip(', ') + ') VALUES ' + values

    db_enter.db_execute(arg, terms)

def drop_row(wine_id, table='userinventory'):
    # drops a row from the database, if for example it is 
    # entered by mistake 
    # this function only takes a wine_id input, which forces
    # the wine to be positively identified before it is 
    # deleted
    # This also allows the table to be selected. By default,
    # the table is the user inventory (which is less dangerous)

    arg = 'DELETE FROM ' + table + ' WHERE wine_id = ?'

    db_drop = DatabaseManager()
    db_drop.db_execute(arg, (wine_id,))

def update_row(update_input, table='userinventory'):
    # updates a specific row in a specified table
    # this function takes a list of the following format:
    # entry_input = [wine_id, upc, winery, region,
    #                name, varietal, wtype,
    #                vintage, msrp, value]
    terms = cleanup_dbinput(update_input, table)
    arg = 'UPDATE ' + table + ' SET '
    for term in terms:
        arg += term + ' = :' + term + ', '
    arg = arg.rstrip(', ')
    arg += ' WHERE wine_id = :wine_id'

    db_update = DatabaseManager()
    db_update.db_execute(arg, terms)


####################################################################
############################ Test Code #############################
####################################################################

# userinv_dict = {"wine_id":input_list[0],
#                 "user_id":input_list[1],
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
  
# userdata_dict = {"user_id":input_list[0],
#                  "username":input_list[1],
#                  "password":input_list[2],
#                  "cellar_space":input_list[3]}

# enter_db(winedata_dict, 'winedata')
# drop_row(winedata_dict['wine_id'], 'winedata')
# print(search_db(winedata_dict, 'winedata'))
# find_bottle = input('Enter a bottle ID: ')
# print(lookup_db(find_bottle, 'winedata'))