import os
import data_tools
from barcode import generate


class Bottle:
    '''
    A generic object to handle bottles and the associated methods
    that may be useful to them
    '''
    # def __init__(self, wine_id=None, upc=None, winery=None, region=None, name=None, varietal=None, wtype=None, vintage=None, msrp=None, value=None):
    def __init__(self, bottle_info):
        # self.wine_id = wine_id
        # self.upc = upc
        # self.winery = winery
        # self.region = region
        # self.name = name
        # self.varietal = varietal
        # self.wtype = wtype
        # self.vintage = vintage
        # self.msrp = msrp
        # self.value = value

        self.bottle_info = bottle_info
    # userinv_dict = {"wine_id":input_list[0],
    #                 "user_id":input_list[1],
    #                 "bottle_size":input_list[2],
    #                 "location":input_list[3],
    #                 "comments":input_list[4],
    #                 "date_in":input_list[5],
    #                 "date_out":input_list[6]}

    # winedata_dict = {"wine_id":None,
    #                  "upc":'791863140506',
    #                  "winery":'Burnt Bridge Cellars',
    #                  "region":'Walla Walla',
    #                  "name":None,
    #                  "varietal":'Merlot',
    #                  "wtype":'Table',
    #                  "vintage":2013,
    #                  "msrp":'$30',
    #                  "value":'$30'}
  
    # userdata_dict = {"user_id":input_list[0],
    #                  "username":input_list[1],
    #                  "password":input_list[2],
    #                  "cellar_space":input_list[3]}
    
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

# new_bottle = Bottle(wine_id=791863140506)
# new_bottle.generate_label()