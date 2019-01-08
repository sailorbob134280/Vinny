class Bottle:
    '''
    A generic object to handle bottles and the associated methods
    that may be useful to them
    '''
    def __init__(self, bottle_id=None, winery=None, region=None, name=None, varietal=None, msrp=None, value=None):
        self.bottle_id = bottle_id
        self.winery = winery
        self.region = region
        self.name = name
        self.varietal = varietal
        self.msrp = msrp
        self.value = value

#    def in_database(self, bottle_id=None, winery=None, region=None, name=None, varietal=None, msrp=None, value=None):
#        cursor.execute()