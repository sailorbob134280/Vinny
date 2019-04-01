import os
import shutil
import datetime
import tempfile
import brother_ql
import brother_ql.backends
import brother_ql.backends.helpers
import brother_ql.backends.pyusb
from db_man import *
from data_tools import search_db, fetch_db, lookup_db, enter_db, drop_row, update_winedata_row, update_userinv_row, get_rowid
from barcode import generate
from barcode.writer import ImageWriter


class Wine:
    '''
    A generic object to handle different wines and 
    the associated methods that may be useful to them
    '''
    def __init__(self, wine_info):
        self.wine_info = wine_info
        self.wine_search_flag = False
        
        # Create a temporary directory to hold generated barcodes. This will be removed
        self.temp_dir = tempfile.mkdtemp()

        # self.wine_id = self.get_wine_id()
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
        if 'upc' in self.wine_info and self.wine_info['upc'] != None:
            result = lookup_db(self.wine_info['upc'], 'winedata')
        elif 'wine_id' in self.wine_info and self.wine_info['wine_id'] != None:
            result = lookup_db(self.wine_info['wine_id'], 'winedata')
        # If not, we'll try to find it with the search function. This may
        # return multiple entries, so we have to return them all (long-ass list)
        else:
            result = search_db(self.wine_info, 'winedata')
        # Now we need to format it. Due to the way the output is formatted, we need
        # to ensure that it becomes a list of tuples, regardless of how many entries
        # there actually are. We also need to handle the case that there may not be 
        # any matches at all. We also need to dynamically assign names because we can't
        # guarantee the structure of the db
        if result is not None:
            self.wine_search_flag = True
            db_names = DatabaseManager()
            keys = db_names.db_getcolnames(table='winedata')
            if isinstance(result, tuple):
                result = [result]
            res_list = []
            for res in result:
                res_list.append(res)
        
            if len(res_list) is 1:
                self.wine_info = {}
                for i, key in enumerate(keys):
                    self.wine_info[key] = res_list[0][i]
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
            result = self.search_wine()
            if isinstance(result, list) and result != []:
                self.wine_info['wine_id'] = result[0][int(0)]
                return self.wine_info['wine_id']
            elif result == []:
                return None
            elif result is not None:
                id_list = []
                for i in range(len(result)):
                    id_list.append(result[i][int('wine_id')])
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
            new_id = enter_db(self.wine_info, 'winedata', ret_id=True)
            return new_id

    def update_wine(self):
        update_winedata_row(self.wine_info)

    def generate_label(self):
        # Function to generate a barcode for the wine based off the unique wine
        # id. First, it grabs the wine_id however it needs to. Then, it generates
        # a unique ITF barcode and stores it as an svg in the temp file and returns
        # the file path
        self.wine_id = self.get_wine_id()
        if self.wine_id != None:
            tag_num = (12 - len(str(self.wine_id))) * '0' + str(self.wine_id)
            options = {'dpi': 162,
                    'module_width': 0.25,
                    'module_height': 12,
                    'quiet_zone': 0, 
                    'font_size': 14,
                    'text_distance': 0.25}
            output = self.temp_dir + '/' + self.wine_id
            writer = ImageWriter()
            writer.dpi = 600
            generate('ITF', tag_num, writer=writer , output=output, writer_options = options)
            return output
        else:
            raise Exception('Cannot generate barcode because wine has no id')

    def print_label(self):
        # Prints the generated label for the wine as long as it has been generated
        image = self.temp_dir + '/' + self.wine_id + '.png'
        # If the image file doesn't exist, generate it first
        if not os.path.isfile(image):
            self.generate_label()
        ql_printer = brother_ql.BrotherQLRaster(model='QL-500')
        ql_printer.cut_at_end = False
        brother_ql.create_label(ql_printer, image, label_size='12', cut=False, dither=True, compress=False, red=False, rotate=90)
        printer = brother_ql.backends.pyusb.list_available_devices()[0]['identifier']
        brother_ql.backends.helpers.send(ql_printer.data, printer_identifier=printer, backend_identifier='pyusb')

    def __del__(self):
        shutil.rmtree(self.temp_dir)


class Bottle(Wine):
    def __init__(self, wine_info, bottle_info=None):
        super().__init__(wine_info)
        self.bottle_info = bottle_info
        if self.bottle_info == None:
            self.bottle_info = {}
        self.bottle_search_flag = False
    
    def search_bottle(self, in_cellar=True, sort_by=None):
        # Starts by searching for a matching wine. This will add the wine_id to the 
        # bottle info as well. 
        wine_res_list = None
        if self.wine_search_flag is False and self.wine_info != None:
            wine_res_list = self.search_wine()
        # assigns wine_id only if the exact wine is positively identified
        if wine_res_list != None and len(wine_res_list) == 1:
            self.bottle_info['wine_id'] = self.wine_info['wine_id']

        # takes the path of least resistance to find the bottle or bottles we're looking for
        if 'wine_id' in self.bottle_info and self.bottle_info['wine_id'] is not None:
            result = fetch_db({'wine_id':self.bottle_info['wine_id']}, in_cellar=in_cellar, sort_by=sort_by)
        elif 'location' in self.bottle_info and self.bottle_info['location'] is not None:
            result = fetch_db({'location':self.bottle_info['location']}, in_cellar=in_cellar, sort_by=sort_by)
        else:
            result = search_db(self.bottle_info, in_cellar=in_cellar, sort_by=sort_by)
        if result is not None:
            self.bottle_search_flag = True
            if self.wine_search_flag == False:
                if self.wine_info == None:
                    self.wine_info = {}
                self.wine_info['wine_id'] = result[0][0]
                self.search_wine()
            db_names = DatabaseManager()
            keys = db_names.db_getcolnames(table='userinventory')
            if isinstance(result, tuple):
                result = [result]
            res_list = []
            for res in result:
                res_list.append(res)
            
            if len(res_list) is 1:
                self.bottle_info = {}
                for i, key in enumerate(keys):
                    self.bottle_info[key] = res_list[0][i]
            return res_list
        else:
            return None
    
    def add_new(self):
        # This method adds a wine to the inventory by first checking if the wine exists, 
        # adding it if it does not, acquiring the wine_id, then checking in a bottle of 
        # the new wine. Meant to be called from the advanced search screen.
        if 'wine_id' not in self.bottle_info or self.bottle_info['wine_id'] == None:
            bottle_id = self.get_wine_id()
            if isinstance(bottle_id, list):
                raise Exception('Multiple wine entries found. Please be more specific.')
            elif bottle_id == None:
                bottle_id = self.add_wine_to_db()
                
            self.bottle_info['wine_id'] = bottle_id
        self.check_in()
        
    def check_in(self, new_location=None, new_bottle_size=None):
        # This method adds a wine to the inventory based on a selected wine_id. Since it will
        # only be called if there's a wine_id, it can be assumed that it exists. Meant to be 
        # called from the main inventory screen.

        if new_location != None:
            self.bottle_info['location'] = new_location
        if new_bottle_size != None:
            self.bottle_info['bottle_size'] = new_bottle_size
        self.bottle_info['date_in'] = '{date:%Y-%m-%d %H:%M:%S}'.format(date=datetime.datetime.now())
        self.bottle_info['date_out'] = None
        enter_db(self.bottle_info)

    def check_out(self):
        # Checks out a bottle from the inventory (really just adds a date out
        # entry) based on the row id of the selected wine_id and location
        row_id = get_rowid(self.bottle_info)
        # row_id = get_rowid({'wine_id':self.bottle_info['wine_id'], 'location':self.bottle_info['location']})
        date_out = '{date:%Y-%m-%d %H:%M:%S}'.format(date=datetime.datetime.now())
        update_dict = {'date_out':date_out}
        update_userinv_row(update_dict, row_id)

    def update_bottle(self, new_info):
        # Updates the selected bottle with new information, such
        # as location and bottle size
        row_id = get_rowid(self.bottle_info)
        if 'wine_id' in new_info:
            del new_info['wine_id']
        if 'date_in' in new_info:
            del new_info['date_in']
        self.bottle_info = new_info
        update_userinv_row(self.bottle_info, row_id)

    def delete_wine(self):
        # Deletes a wine from the database. Dangerous command. Use with care.
        # Requires an explicit wine_id input to function. 
        drop_row(self.wine_info['wine_id'], table='winedata')
        drop_row(self.wine_info['wine_id'])


    def delete_bottle(self):
        # Deletes a bottle from the db. Less dangerous than deleting wines, 
        # but still meant to be handled with care. Uses wine_id and other data
        # to get row id, then uses that to delete the entry. 
        row_id = get_rowid(self.bottle_info)
        drop_row(self.wine_info['wine_id'], rowid=row_id)


    def clear_bottle(self):
        self.bottle_info = {}
        self.wine_info = {}
        self.wine_search_flag = False


####################################################################
############################ Test Code #############################
####################################################################

wine_id = '000000000006'
# wine_id = None

# wine_dict = {"wine_id":wine_id,
#              "upc":None,
#              "winery":'Turly',
#              "region":'Walla Walla',
#              "name":None,
#              "varietal":'Zinfandel',
#              "wtype":'Table',
#              "vintage":2011,
#              "msrp":'$40',
#              "value":'$25',
#              "comments":'Young vines'}
wine_dict = {"wine_id":wine_id}
bottle_dict = {}

# wine_dict = {"wine_id":'000000000003',
#              "upc":None,
#              "winery":None,
#              "region":None,
#              "name":None,
#              "varietal":None,
#              "wtype":None,
#              "vintage":None,
#              "msrp":None,
#              "value":None}

# bottle_dict = {"wine_id":wine_id,
#                "bottle_size":'Standard (750 mL)',
#                "location":'C9',
#                "date_in":None,
#                "date_out":None}

# new_bottle_dict = {"wine_id":None,
#                "bottle_size":'Standard (750 mL)',
#                "location":'B12',
#                "date_in":None,
#                "date_out":None}

new_bottle = Bottle(wine_dict, bottle_dict)
new_bottle.generate_label()
# new_bottle.check_in()
# new_bottle.add_wine_to_db()
# new_bottle.add_new()
# new_bottle.check_out()
# new_bottle.update_bottle(new_bottle_dict)
# new_bottle.delete_wine()
# new_bottle.delete_bottle()
# new_bottle = Bottle(wine_dict, None)
# print(new_bottle.search_bottle())
# print(new_bottle.wine_info)
# print(new_bottle.bottle_info)
