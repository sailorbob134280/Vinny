from db_man import DatabaseManager

def cleanup_wine_input(input_list):
    # first, assign the inputs to a dictionary (including none)
    wine_input = {"wine_id":input_list[0],
                  "winery":input_list[1],
                  "region":input_list[2],
                  "name":input_list[3],
                  "varietal":input_list[4],
                  "wtype":input_list[5],
                  "vintage":input_list[6],
                  "msrp":input_list[7],
                  "value":input_list[8]}
    # if the term is not used, it is discarded from the search
    terms = {}
    for wkey in wine_input:
        if wine_input[wkey] is not None:
            terms[wkey] = wine_input[wkey]
    return terms

def search_winedb(search_input):
    # searches for a wine in the database that resembles the input
    # first, assign the inputs to a list to be cleaned up
    # this function takes a list of the following format:
    # search_input = [wine_id, winery, region,
    #                 name, varietal, wtype,
    #                 vintage, msrp, value]
    # it is critical that the list is complete, even if some
    # of the values are null

    terms = cleanup_wine_input(search_input)

    # craft the sql query string
    arg = 'SELECT * FROM winedata WHERE '
    for term in terms:
        arg += '{0} LIKE {1} AND '.format(term, ':' + term)
    arg = arg.rstrip(' AND ') + ';'

    # finally, call the search function from the db_man object
    db_search = DatabaseManager()
    return db_search.db_fetch(arg, terms, 'all')

def enter_winedb(entry_input):
    # enters a wine into the database
    # this function takes a list of the following format:
    # entry_input = [wine_id, winery, region,
    #                name, varietal, wtype,
    #                vintage, msrp, value]
    # it is critical that the list is complete, even if some
    # of the values are null
    
    db_enter = DatabaseManager()
    db_enter.db_execute('INSERT INTO winedata (wine_id, winery, region, name, varietal, wtype, vintage, msrp, value) VALUES (?,?,?,?,?,?,?,?,?)', entry_input)

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

def update_table(update_input, table='winedata'):
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
