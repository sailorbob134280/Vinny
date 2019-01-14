import db_man
import os
from barcode import generate


class Bottle:
    '''
    A generic object to handle bottles and the associated methods
    that may be useful to them
    '''
    def __init__(self, wine_id=None, upc=None, winery=None, region=None, name=None, varietal=None, wtype=None, vintage=None, msrp=None, value=None):
        self.wine_id = wine_id
        self.upc = upc
        self.winery = winery
        self.region = region
        self.name = name
        self.varietal = varietal
        self.wtype = wtype
        self.vintage = vintage
        self.msrp = msrp
        self.value = value

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