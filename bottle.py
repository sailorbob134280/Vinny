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

    def generate_barcode(self):
        name = generate('ITF', str(self.wine_id), output=str(self.wine_id))