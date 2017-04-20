from collections import OrderedDict

'''
Categories: *Ebay ID
            *Data Completes
            *Sold?
            *Aution/BIN
            Model
            *Country of Origin
            *Top Rated Seller Status
            *Price
            *Shipping
            Processor
            Ram Cap
            Primary HD Cap
            Primary HD Type
            Secondary HD Cap
            Secondary HD Type
            OS
            Battery
            Charger
'''
ATTRIBUTES = OrderedDict()
ATTRIBUTES['model'] = 'Model'
ATTRIBUTES['processor'] = 'Processor'
ATTRIBUTES['ram_cap'] = 'Ram Capacity'
ATTRIBUTES['pri_hd_cap'] = 'Primary HD Capacity'
ATTRIBUTES['pri_hd_type'] = 'Primary HD Type'
ATTRIBUTES['sec_hd_cap'] = 'Secondary HD Capacity'
ATTRIBUTES['sec_hd_type'] = 'Secondary HD Type'
ATTRIBUTES['os'] = 'OS'
ATTRIBUTES['battery'] = 'Battery Included'
ATTRIBUTES['ac_charger'] = 'AC Charger Included'

class DataInput:

    def __init__(self, attributes):
        self.attributes = attributes
