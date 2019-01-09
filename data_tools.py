from db_man import DatabaseManager

def cleanup_dbinput(input_list, table):
    # first, figure out which table the input is for 
    # and assign the inputs to a dictionary (including none)
    if table is 'userinventory':
        input_dict = {"transaction_id":input_list[0],
                      "wine_id":input_list[1],
                      "user_id":input_list[2],
                      "qty":input_list[3],
                      "bottle_size":input_list[4],
                      "location":input_list[5],
                      "comments":input_list[6],
                      "date_in":input_list[7],
                      "date_out":input_list[8]}
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
        arg += '{0} LIKE {1} AND '.format(term, ':' + term)
    arg = arg.rstrip(' AND ')

    # finally, call the search function from the db_man object
    db_search = DatabaseManager()
    return db_search.db_fetch(arg, terms, 'all')

def enter_db(entry_input, table='userinventory'):
    # enters a wine into the database
    # this function takes a list of the following format:
    # entry_input = [wine_id, winery, region,
    #                name, varietal, wtype,
    #                vintage, msrp, value]
    # it is critical that the list is complete, even if some
    # of the values are null
    terms = cleanup_dbinput(entry_input, table)

    #arg = 'INSERT INTO ' + table + ' (wine_id, winery, region, name, varietal, wtype, vintage, msrp, value) VALUES (?,?,?,?,?,?,?,?,?)'
    arg = 'INSERT INTO ' + table + ' ('
    values = '('
    for term in terms:
        arg +=  term + ', '
        values += ':'+ term + ', '
    values = values.rstrip(', ') + ')'
    arg = arg.rstrip(', ') + ') VALUES ' + values

    db_enter = DatabaseManager()
    db_enter.db_execute(arg, entry_input)

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
    terms = cleanup_wine_input(update_input)
    arg = 'UPDATE ' + table + ' SET '
    for term in terms:
        arg += term + ' = :' + term + ', '
    arg = arg.rstrip(', ')
    arg += ' WHERE wine_id = :wine_id'

    db_update = DatabaseManager()
    db_update.db_execute(arg, terms)

# entry_input = [6, 'burnt', None,
#                None, 'cab', 'Table',
#                2008, None, None]

