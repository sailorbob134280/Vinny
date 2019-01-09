from db_man import DatabaseManager

def in_database(wine_id=None, winery=None, region=None, name=None, varietal=None, wtype=None, vintage=None, msrp=None, value=None):
    # searches for a wine in the database that resembles the input
    # first, assign the inputs to a dictionary (including none)
    search_input = {"wine_id":wine_id,
                    "winery":winery,
                    "region":region,
                    "name":name,
                    "varietal":varietal,
                    "wtype":wtype,
                    "vintage":vintage,
                    "msrp":msrp,
                    "value":value}
    # if the term is not used, it is discarded from the search
    terms = {}
    for skey in search_input:
        if search_input[skey] is not None:
            terms[skey] = search_input[skey]

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