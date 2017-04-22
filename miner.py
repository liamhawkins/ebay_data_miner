'''
TODO:
    Find better way of gathering scraping data, then manual data, then joining to full DB
    Index dataframe by ebay_id(?)
    Refactor for better names
    ebay item class(?)
'''
import pandas as pd
from collections import OrderedDict
from prompt_toolkit import prompt


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

SCRAPES = ['ebay_id', 'date_complete', 'sold',
           'listing_type', 'country', 'top_rated',
           'price', 'shipping']

class DataInput:

    def __init__(self, attributes, scrapes):
        self.attributes = attributes
        self.scrapes = scrapes
        self.manual_input_df = pd.DataFrame(columns=self.attributes.keys())
        self.scrapes_df = pd.DataFrame(columns=self.scrapes)
        self.full_attribute_df = pd.DataFrame()

    def print_attributes(self):
        for attrib, question in self.attributes.items():
            print('Attribute: {} - Question: {}:'.format(attrib, question))

    def print_data(self):
        print(self.manual_input_df)

    def get_manual_input(self, ebay_ids):
        for item in ebay_ids:
            inp_list = []
            for attrib, question in self.attributes.items():
                inp_list.append(prompt('{} - {}: '.format(item, question)))
            self.manual_input_df.loc[len(self.manual_input_df.index) + 1] = inp_list

    def scrape_input(self, ebay_ids):
        for item in ebay_ids:
            scrape_list = []
            for attrib in self.scrapes:
                scrape_list.append('fake data')
            self.scrapes_df.loc[len(self.scrapes_df.index) + 1] = scrape_list

    def join_dfs(self):
        self.full_attribute_df = pd.concat([self.scrapes_df, self.manual_input_df], axis=1)
        print(self.full_attribute_df)

if __name__ == '__main__':
    es = DataInput(ATTRIBUTES, SCRAPES)
    es.get_manual_input([1,2])
    es.scrape_input([1,2])
    es.join_dfs()
    es.print_data()
