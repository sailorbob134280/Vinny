import os
from data_tools import *
from barcode import generate


class Wine:
    '''
    A generic object to handle different wines and 
    the associated methods that may be useful to them
    '''
    def __init__(self, wine_info):
        self.wine_info = wine_info
        # wine_info = {"wine_id":None,
        #              "upc":'791863140506',
        #              "winery":'Burnt Bridge Cellars',
        #              "region":'Walla Walla',
        #              "name":None,
        #              "varietal":'Merlot',
        #              "wtype":'Table',
        #              "vintage":2013,
        #              "msrp":'$30',
        #              "value":'$30'}
    
    def search_wine(self):
        # This function is meant to take a partial wine dataset
        # and turn it into a full dataset (or as full as it's 
        # going to get). It simply updates the bottle's attributes.
        # Ideally, this will be done with a upc/wine_id lookup:
        if 'upc' in self.wine_info and self.wine_info['upc'] is not None:
            result = lookup_db(self.wine_info['upc'], 'winedata')
        elif 'wine_id' in self.wine_info and self.wine_info['wine_id'] is not None:
            result = lookup_db(self.wine_info['wine_id'], 'winedata')
        # If not, we'll try to find it with the search function. This may
        # return multiple entries, so we have to return them all (long-ass list)
        else:
            result = search_db(self.wine_info, 'winedata')
        
        # Now we need to format it. Due to the way the output is formatted, we need
        # to ensure that it becomes a list of tuples, regardless of how many entries
        # there actually are. We also need to handle the case that there may not be 
        # any matches at all.
        if result is not None:
            if isinstance(result, tuple):
                result = [result]
            res_list = []
            for i in range(len(result)):
                res_list.append({"wine_id":result[i][0],
                                 "upc":result[i][1],
                                 "winery":result[i][2],
                                 "region":result[i][3],
                                 "name":result[i][4],
                                 "varietal":result[i][5],
                                 "wtype":result[i][6],
                                 "vintage":result[i][7],
                                 "msrp":result[i][8],
                                 "value":result[i][9]})
        
            return res_list
        else:
            return None

    def generate_label(self):
        tag_num = (12 - len(str(self.wine_id))) * '0' + str(self.wine_id)
        options = {'dpi': 200,
                   'module_height': 5,
                   'quiet_zone': 0,
                   'text_distance': 3}
        new_label = generate('ITF', tag_num, output=str(self.wine_id), writer_options = options)

    # def __del__(self):
    #     svg_filename = str(self.wine_id) + '.svg'
    #     if os.path.exists(svg_filename):
    #         os.remove(svg_filename)


# winedata_dict = {"wine_id":None,
#                  "upc":'12345',
#                  "winery":None,
#                  "region":None,
#                  "name":None,
#                  "varietal":None,
#                  "wtype":None,
#                  "vintage":None,
#                  "msrp":None,
#                  "value":None}
# new_bottle = Wine(winedata_dict)
# print(new_bottle.search_wine())