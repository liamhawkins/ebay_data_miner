import pandas as pd
from collections import OrderedDict
from prompt_toolkit import prompt


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
        self.df = pd.DataFrame(columns=self.attributes.keys())
        print(self.df)

    def print_attributes(self):
        for attrib, question in self.attributes.items():
            print('Attribute: {} - Question: {}:'.format(attrib, question))

    def print_data(self):
        print(self.df)

    def get_input(self, ebay_ids):
        for item in ebay_ids:
            inp_list = []
            for attrib, question in self.attributes.items():
                inp_list.append(prompt('{} - {}: '.format(item, question)))
            print(inp_list)
            self.df.loc[len(self.df.index) + 1] = inp_list

if __name__ == '__main__':
    es = DataInput(ATTRIBUTES)
    es.get_input([1,2])
    es.print_data()
