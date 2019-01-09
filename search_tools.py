from db_man import DatabaseManager
# import sqlite3
# import os
# cwd = os.getcwd() + '\wineinv_data.db'
# print(cwd)


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

    # make a tuple to contain the placeholders for the sql query
    # placeholder = [None] * (2 * len(terms))
    # placeholder[::2] = list(terms.keys())
    # placeholder[1::2] = list(terms.values())
    # placeholder = tuple(placeholder)

    # craft the sql query string
    arg = 'SELECT * FROM winedata WHERE '
    # for i in range(int(len(placeholder) / 2)):
    #     arg += '{} LIKE ? AND '.format
    for term in terms:
        arg += '{0} LIKE {1} AND '.format(term, ':' + term)
    arg = arg.rstrip(' AND ') + ';'
    print(terms)
    print(arg)

    # finally, call the search function from the db_man object
    db_search = DatabaseManager()
    return db_search.db_fetch(arg, terms, 'all')
    # db_fetch(arg, placeholder, 'all')


result = in_database(wine_id=1, winery="burnt", vintage=2008)
print(result)