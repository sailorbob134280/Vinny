import os
import datetime
from data_tools import *
from barcode import generate


class Wine:
    '''
    A generic object to handle different wines and 
    the associated methods that may be useful to them
    '''
    def __init__(self, wine_info):
        self.wine_info = wine_info
        self.wine_search_flag = False
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
            self.wine_search_flag = True
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
        
            if len(res_list) is 1:
                self.wine_info = res_list[0]
            return res_list
        else:
            return None

    def get_wine_id(self):
        # Returns just the wine_id, or a list of wine_ids if there
        # are multiple. Useful for stitching together the inv and data
        # tables. If the bottle doesn't have a wine_id attached, it'll
        # try to find it
        if 'wine_id' in self.wine_info and self.wine_info['wine_id'] is not None:
            return self.wine_info['wine_id']
        else:
            result = self.search_wine(table='winedata')
            if len(result) is 1:
                self.wine_info['wine_id'] = result[0]
                return self.wine_info['wine_id']
            elif result is not None:
                id_list = []
                for i in range(len(result)):
                    id_list.append(result[i]['wine_id'])
                return id_list
            else:
                return None

    def add_wine_to_db(self):
        # Adds a wine to the database after checking if
        # it's already there. If the search flag is true,
        # the database has already been searched and there's
        # no need to do it again
        result = None
        if self.wine_search_flag is False:
            result = self.search_wine()
        if result is None:
            enter_db(self.wine_info, 'winedata')

    def update_wine_db(self):
        update_row(self.wine_info, 'winedata')

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


class Bottle(Wine):
    def __init__(self, wine_info, bottle_info):
        super().__init__(wine_info)
        self.bottle_info = bottle_info
        self.bottle_search_flag = False
    
    def search_bottle(self):
        if self.wine_search_flag is False:
            super().search_wine()

        if 'wine_id' in self.bottle_info and self.bottle_info['wine_id'] is not None:
            result = fetch_db({'wine_id':self.bottle_info['wine_id']})
        elif 'location' in self.bottle_info and self.bottle_info['location'] is not None:
            result = fetch_db({'location':self.bottle_info['location']})
        else:
            result = search_db(self.bottle_info)
        
        if result is not None:
            self.bottle_search_flag = True
            if isinstance(result, tuple):
                result = [result]
            res_list = []
            for i in range(len(result)):
                res_list.append({"wine_id":result[i][0],
                                 "user_id":result[i][1],
                                 "bottle_size":result[i][2],
                                 "location":result[i][3],
                                 "comments":result[i][4],
                                 "date_in":result[i][5],
                                 "date_out":result[i][6]})
            
            if len(res_list) is 1:
                self.bottle_info = res_list[0]
            return res_list
        else:
            return None
    
    def check_in(self, new_location, new_bottle_size=None):
        if self.bottle_search_flag is False:
            existing_botttles = self.search_bottle()
        if 'wine_id' not in self.bottle_info or self.bottle_info['wine_id'] is None:
            bottle_id = self.get_wine_id()
            if isinstance(bottle_id, list):
                raise Exception('Multiple wine entries found. Please be more specific.')
            else:
                self.bottle_info['wine_id'] = bottle_id
        while fetch_db({'location':new_location}) is not None:
            print('Error: Location is already occupied.')
            new_location = input('Please enter a new location: ')
        self.bottle_info['location'] = new_location
        if new_bottle_size is not None:
            self.bottle_info['bottle_size'] = new_bottle_size
        self.bottle_info['date_in'] = '{date:%Y-%m-%d %H:%M:%S}'.format(date=datetime.datetime.now())
        enter_db(self.bottle_info)

                 

# wine_dict = {"wine_id":'000000000002',
#              "upc":None,
#              "winery":'Burnt Bridge Cellars',
#              "region":'Walla Walla',
#              "name":None,
#              "varietal":'Grenache',
#              "wtype":'Table',
#              "vintage":2013,
#              "msrp":'$35',
#              "value":'$35'}

wine_dict = {"wine_id":'000000000003',
             "upc":None,
             "winery":None,
             "region":None,
             "name":None,
             "varietal":None,
             "wtype":None,
             "vintage":None,
             "msrp":None,
             "value":None}

bottle_dict = {"wine_id":None,
               "user_id":'000000000001',
               "bottle_size":'Standard (750 mL)',
               "location":None,
               "comments":None,
               "date_in":None,
               "date_out":None}

new_bottle = Bottle(wine_dict, bottle_dict)
new_bottle.check_in(new_location='A7')
