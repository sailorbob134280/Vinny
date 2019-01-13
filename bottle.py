import db_man
from barcode import generate


class Bottle:
    '''
    A generic object to handle bottles and the associated methods
    that may be useful to them
    '''
    def __init__(self, wine_id=None, winery=None, region=None, name=None, varietal=None, wtype=None, vintage=None, msrp=None, value=None):
        self.wine_id = wine_id
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
        #tag_num = str(self.wine_id)
        new_label = generate('ITF', tag_num, output=str(self.wine_id))

new_bottle = Bottle(wine_id=6)
new_bottle.generate_label()