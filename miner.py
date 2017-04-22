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


MANUAL_ATTRIBUTES = OrderedDict()
MANUAL_ATTRIBUTES['model'] = 'Model'
MANUAL_ATTRIBUTES['processor'] = 'Processor'
MANUAL_ATTRIBUTES['ram_cap'] = 'Ram Capacity'
MANUAL_ATTRIBUTES['pri_hd_cap'] = 'Primary HD Capacity'
MANUAL_ATTRIBUTES['pri_hd_type'] = 'Primary HD Type'
MANUAL_ATTRIBUTES['sec_hd_cap'] = 'Secondary HD Capacity'
MANUAL_ATTRIBUTES['sec_hd_type'] = 'Secondary HD Type'
MANUAL_ATTRIBUTES['os'] = 'OS'
MANUAL_ATTRIBUTES['battery'] = 'Battery Included'
MANUAL_ATTRIBUTES['ac_charger'] = 'AC Charger Included'

AUTO_SCRAPE_ATTRIBUTES = ['ebay_id', 'date_complete', 'sold',
                          'listing_type', 'country', 'top_rated',
                          'price', 'shipping']


class DataInput:

    def __init__(self, manual_attributes, auto_scrape_attributes):
        self.manual_attributes = manual_attributes
        self.auto_scrape_attributes = auto_scrape_attributes
        self.manual_attribute_df = pd.DataFrame(columns=self.manual_attributes.keys())
        self.auto_scrape_attribute_df = pd.DataFrame(columns=self.auto_scrape_attributes)
        self.full_attribute_df = pd.DataFrame()

    def print_manual_attributes(self):
        for attrib, question in self.manual_attributes.items():
            print('Attribute: {} - Question: {}:'.format(attrib, question))

    def print_auto_scrap_attributes(self):
        for attrib in self.auto_scrape_attributes:
            print(attrib)

    def get_manual_input(self, ebay_ids):
        for item in ebay_ids:
            inp_list = []
            for attrib, question in self.manual_attributes.items():
                inp_list.append(prompt('{} - {}: '.format(item, question)))
            self.manual_attribute_df.loc[len(self.manual_attribute_df.index) + 1] = inp_list

    def scrape_attributes(self, ebay_ids):
        for item in ebay_ids:
            scrape_list = []
            for attrib in self.auto_scrape_attributes:
                scrape_list.append('fake data')
            self.auto_scrape_attribute_df.loc[len(self.auto_scrape_attribute_df.index) + 1] = scrape_list

    def join_dfs(self):
        self.full_attribute_df = pd.concat([self.auto_scrape_attribute_df, self.manual_attribute_df], axis=1)
        print(self.full_attribute_df)

if __name__ == '__main__':
    es = DataInput(MANUAL_ATTRIBUTES, AUTO_SCRAPE_ATTRIBUTES)
    es.get_manual_input([1, 2])
    es.scrape_attributes([1, 2])
    es.join_dfs()
    print(es.manual_attribute_df)
