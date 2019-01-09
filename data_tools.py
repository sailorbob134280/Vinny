from db_man import DatabaseManager

def cleanup_wine_input(input_list):
    # first, assign the inputs to a dictionary (including none)
    wine_input = {"wine_id":input_list[1],
                    "winery":input_list[2],
                    "region":input_list[3],
                    "name":input_list[4],
                    "varietal":input_list[5],
                    "wtype":input_list[6],
                    "vintage":input_list[7],
                    "msrp":input_list[8],
                    "value":input_list[9]}
    # if the term is not used, it is discarded from the search
    terms = {}
    for wkey in wine_input:
        if wine_input[wkey] is not None:
            terms[wkey] = wine_input[wkey]
    return terms

def search_winedb(wine_id=None, winery=None, region=None, name=None, varietal=None, wtype=None, vintage=None, msrp=None, value=None):
    # searches for a wine in the database that resembles the input
    # first, assign the inputs to a list to be cleaned up
    search_input = [wine_id, winery, region,
                    name, varietal, wtype,
                    vintage, msrp, value]

    terms = cleanup_wine_input(search_input)

    # craft the sql query string
    arg = 'SELECT * FROM winedata WHERE '
    for term in terms:
        arg += '{0} LIKE {1} AND '.format(term, ':' + term)
    arg = arg.rstrip(' AND ') + ';'
    print(terms)
    print(arg)

    # finally, call the search function from the db_man object
    db_search = DatabaseManager()
    return db_search.db_fetch(arg, terms, 'all')

def enter_winedb(wine_id=None, winery=None, region=None, name=None, varietal=None, wtype=None, vintage=None, msrp=None, value=None):
    # enters a wine into the database
    entry_input = (wine_id, winery, region,
                   name, varietal, wtype,
                   vintage, msrp, value)
    
    db_enter = DatabaseManager()
    db_enter.db_execute('INSERT INTO winedata (wine_id, winery, region, name, varietal, wtype, vintage, msrp, value) VALUES (?,?,?,?,?,?,?,?,?)', entry_input)
