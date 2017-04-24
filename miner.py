'''
TODO:
    Add/Check for Errors
'''
import urllib.request
import pandas as pd
import os
from bs4 import BeautifulSoup
from collections import OrderedDict
from prompt_toolkit import prompt


DATABASE = 'item_database.csv'

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


class EbayScraper:

    def __init__(self, manual_attributes):
        self.unfilled_items = OrderedDict()
        self.new_items = OrderedDict()
        self.manual_attributes = manual_attributes
        self.auto_scrape_attributes = ['date_complete', 'sold',
                                       'listing_type', 'country',
                                       'top_rated', 'price',
                                       'shipping']
        self.full_attribute_df = pd.DataFrame()

    def read_item_database(self):
        try:
            self.database = pd.read_csv(DATABASE)
            self.database_ids = [str(i) for i in self.database['ebay_id'].tolist()]
            # self.database_ids = [str(i) for i in self.database_ids]
        except FileNotFoundError:
            print('Database not found, a new one will be created')

    def write_item_database(self):
        items = self.new_items.values()
        items_attribs = list()
        for item in items:
            items_attribs.append(vars(item))
        item_df = pd.DataFrame(items_attribs)
        if os.path.isfile(DATABASE):
            with open(DATABASE, 'a') as f:
                item_df.to_csv(f, header=False)
        else:
            item_df.to_csv(DATABASE)

    def open_ebay_listing(self):
        # TODO: open ebay listing page (selenium?)
        pass

    def close_ebay_listing(self):
        # TODO: close ebay listing page (selenium?)
        pass

    def get_search_result_page_urls(self):
        '''
        Scrapes ebay search results and returns urls of first 3 pages
        '''
        self.search_result_page_urls = []
        for pg_num in range(1, 4): # first 3 pages TODO: determine this num from search results
            if pg_num == 1:
                page = ''
            else:
                page = '&_pgn=' + str(pg_num) + '&_skc=' + str((pg_num - 1) * 200)

            url = 'http://www.ebay.ca/sch/i.html?_from=R40&_sacat=0' \
                  '&LH_Complete=1&_udlo=&_udhi=&LH_Auction=1&LH_BIN=1' \
                  '&_samilow=&_samihi=&_sadis=15&_stpos=k1r7t8&_sop=13' \
                  '&_dmd=1&_nkw=thinkpad+x220' + page + '&rt=nc'
            self.search_result_page_urls.append(url)

    def get_new_items(self):
        '''
        After search result URLs are scraped, creates dictionary will all itemIDs and item URLs
        '''
        for url in self.search_result_page_urls:
            r = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(r, "html5lib")
            listings = soup.find_all('li', class_='sresult lvresult clearfix li')
            for element in listings:
                listing_id = element['listingid']
                item = element.find_all('a', class_='img imgWr2')
                listing_url = item[0]['href']
                if hasattr(self, 'database') :
                    if not (listing_id in self.database_ids):
                        self.unfilled_items[listing_id] = EbayItem({'ebay_id':listing_id, 'item_url':listing_url})
                else:
                    self.unfilled_items[listing_id] = EbayItem({'ebay_id':listing_id, 'item_url':listing_url})


    def print_items(self):
        '''
        Prints ebay items with completed attributes
        '''
        for item in self.new_items.values():
            print(item)

    def print_manual_attributes(self):
        '''
        Prints ebay item attributes that need manual input
        '''
        for attrib, question in self.manual_attributes.items():
            print('Attribute: {} - Question: {}:'.format(attrib, question))

    def print_auto_scrap_attributes(self):
        '''
        Prints ebay item attributes that are automatically scraped
        '''
        for attrib in self.auto_scrape_attributes:
            print(attrib)

    def scrape_item_attributes(self, item):
        '''
        Scrapes ebay listing for scrapable attributes
        '''
        # TODO: Move into EbayItem class
        scrape_dict = dict()
        for attrib in self.auto_scrape_attributes:
            scrape_dict[attrib] = 'fake data'
        item.set_attributes(scrape_dict)
        return item

    def get_item_attributes(self, id_item_pair):
        '''
        Prompts user for ebay listing attributes that need manual input
        '''
        # TODO: Move into EbayItem class
        inp_dict = dict()
        item_id = id_item_pair[0]
        item = id_item_pair[1]
        for attrib, question in self.manual_attributes.items():
            inp_dict[attrib] = prompt('{} - {}: '.format(item_id, question))
        item.set_attributes(inp_dict)
        item = self.scrape_item_attributes(item)
        self.new_items[item_id] = item


class EbayItem:
    def __init__(self, *attributes):
        for dictionary in attributes:
            for key in dictionary:
                setattr(self, key, dictionary[key])

    def __str__(self):
        attribs = []
        for attr, value in vars(self).items():
            attribs.append('{} - {}'.format(attr, value))
        return '\nEbay item: ' + self.ebay_id + '\n' + '\n'.join(attribs)

    def set_attributes(self, *attributes):
        '''
        Set/update attributes of instance after instantiation
        '''
        for dictionary in attributes:
            for key in dictionary:
                setattr(self, key, dictionary[key])

    def scrape_attributes():
        # TODO: move from EbayScraper class
        pass

    def prompt_item_attributes():
        # TODO: move from EbayScraper class
        pass


if __name__ == '__main__':
    es = EbayScraper(MANUAL_ATTRIBUTES)
    es.read_item_database()
    es.get_search_result_page_urls()
    es.get_new_items()
    for id_item_pair in es.unfilled_items.items():
        try:
            es.get_item_attributes(id_item_pair)
        except KeyboardInterrupt:
            break

    es.write_item_database()
