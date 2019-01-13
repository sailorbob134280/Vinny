from db_man import DatabaseManager

def cleanup_dbinput(input_list, table):
    # first, figure out which table the input is for 
    # and assign the inputs to a dictionary (including none)
    if table is 'userinventory':
        input_dict = {"transaction_id":input_list[0],
                      "wine_id":input_list[1],
                      "user_id":input_list[2],
                      "bottle_size":input_list[3],
                      "location":input_list[4],
                      "comments":input_list[5],
                      "date_in":input_list[6],
                      "date_out":input_list[7]}
    elif table is 'winedata':
        input_dict = {"wine_id":input_list[0],
                      "winery":input_list[1],
                      "region":input_list[2],
                      "name":input_list[3],
                      "varietal":input_list[4],
                      "wtype":input_list[5],
                      "vintage":input_list[6],
                      "msrp":input_list[7],
                      "value":input_list[8]}
    elif table is 'userdata':
        input_dict = {"user_id":input_list[0],
                      "username":input_list[1],
                      "password":input_list[2],
                      "cellar_space":input_list[3]}
    else:
        raise Exception('''Table does not exist! Please contact the devs about this... You really shouldn't see this.''')

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
    # search_input = [wine_id, winery, region,
    #                 name, varietal, wtype,
    #                 vintage, msrp, value]
    # it is critical that the list is complete, even if some
    # of the values are null

    terms = cleanup_dbinput(search_input, table)

    # craft the sql query string
    arg = 'SELECT * FROM ' + table + ' WHERE '
    for term in terms:
        if term is 'wine_id':
            arg += 'wine_id LIKE '
        else:
            arg += '{0} LIKE %{1}% AND '.format(term, ':' + term)
    arg = arg.rstrip(' AND ')

    # finally, call the search function from the db_man object
    db_search = DatabaseManager()
    return db_search.db_fetch(arg, terms, 'all')

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

def enter_db(entry_input, table='userinventory'):
    # enters a wine into the database
    # this function takes a list of the following format:
    # entry_input = [wine_id, winery, region,
    #                name, varietal, wtype,
    #                vintage, msrp, value]
    # it is critical that the list is complete, even if some
    # of the values are null
    db_enter = DatabaseManager()
    terms = cleanup_dbinput(entry_input, table)

    # we need to check if the specific requested wine_id is 
    # currently in use. If it is, we need to reassign the old
    # one to something new. (This is so that we don't risk a
    # collision when entering a UPC code as an asset tag)
    # this checks for a collision and if one exists, it reenters
    # the old row as a new one to get a new wine_id assigned. 
    # THIS WILL ALSO NEED TO WARN THE USER TO UPDATE THE OLD
    # BARCODE ONCE THE UI IS IMPLIMENTED
    if table is 'winedata' and 'wine_id' in terms:
        old_row = fetch_db([terms['wine_id'], None, None, None, None, None, None, None, None], 'winedata')
        print(old_row)
        if old_row is not None:
            move_entry = list(old_row)
            move_entry[0] = None
            print(move_entry)
            db_enter.db_execute('INSERT INTO winedata (wine_id, winery, region, name, varietal, vintage, wtype, msrp, value) VALUES (?,?,?,?,?,?,?,?,?)', tuple(move_entry))
            relocated_entry = fetch_db(move_entry, 'winedata')
            print('''WARNING: This wine_id is currently in use! The old bottle, {0} {1} {2} {3},
             has been assigned a new wine_id of {4}. Please print a new barcode now.'''.format(relocated_entry[1],
             relocated_entry[6], relocated_entry[3], relocated_entry[4], relocated_entry[0]))
            drop_row(terms['wine_id'], 'winedata')

    #arg = 'INSERT INTO ' + table + ' (wine_id, winery, region, name, varietal, wtype, vintage, msrp, value) VALUES (?,?,?,?,?,?,?,?,?)'
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

def update_table(update_input, table='userinventory'):
    # updates a specific row in a specified table
    # this function takes a list of the following format:
    # entry_input = [wine_id, winery, region,
    #                name, varietal, wtype,
    #                vintage, msrp, value]
    terms = cleanup_dbinput(update_input)
    arg = 'UPDATE ' + table + ' SET '
    for term in terms:
        arg += term + ' = :' + term + ', '
    arg = arg.rstrip(', ')
    arg += ' WHERE wine_id = :wine_id'

    db_update = DatabaseManager()
    db_update.db_execute(arg, terms)
