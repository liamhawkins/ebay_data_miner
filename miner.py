'''
TODO:
    Find better way of gathering scraping data, then manual data, then joining to full DB
    Index dataframe by ebay_id(?)
    ebay item class(?)
'''
import urllib.request
import pandas as pd
from bs4 import BeautifulSoup
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

AUTO_SCRAPE_ATTRIBUTES = ['ebay_id', 'item_url', 'date_complete', 'sold',
                          'listing_type', 'country', 'top_rated',
                          'price', 'shipping']


class EbayScraper:

    def __init__(self, manual_attributes, auto_scrape_attributes):
        self.new_items = OrderedDict()
        self.manual_attributes = manual_attributes
        self.auto_scrape_attributes = auto_scrape_attributes
        self.full_attribute_df = pd.DataFrame()

    def read_item_database(self):
        # TODO: read in item database csv
        pass

    def write_item_database(self):
        # TODO: write out item database csv
        pass

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
        for pg_num in range(1, 4):
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
        After search result URLs are scraped, returns dictionary will all itemIDs and item URLs
        '''
        for url in self.search_result_page_urls:
            r = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(r, "html5lib")
            listings = soup.find_all('li', class_='sresult lvresult clearfix li')
            for element in listings:
                listing_id = element['listingid']
                item = element.find_all('a', class_='img imgWr2')
                listing_url = item[0]['href']
                # TODO: Add in check for ebayID already in DB
                self.new_items[listing_id] = EbayItem({'ebay_id':listing_id, 'item_url':listing_url})

    def print_items(self):
        '''
        Prints scraped ebay items
        '''
        for ebay_id, item in self.new_items.items():
            print('{} - {}'.format(ebay_id, item.item_url))

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

    def get_manual_input(self, ebay_ids):
        '''
        Prompts user for ebay item attributes that need manual input
        '''
        for item_id in ebay_ids:
            inp_dict = dict()
            for attrib, question in self.manual_attributes.items():
                inp_dict[attrib] = prompt('{} - {}: '.format(item_id, question))
            self.new_items[item_id].set_attributes(inp_dict)

    def scrape_attributes(self, ebay_ids):
        '''
        Scrapes ebay items for attributes that are manually scraped
        '''
        for item_id in ebay_ids:
            scrape_dict = dict()
            for attrib in self.auto_scrape_attributes:
                scrape_dict[attrib] = 'fake data'
            self.new_items[item_id].set_attributes(scrape_dict)


class EbayItem:
    def __init__(self, *attributes):
        for dictionary in attributes:
            for key in dictionary:
                setattr(self, key, dictionary[key])

    def __str__(self):
        attribs = []
        for attr, value in vars(self).items():
            attribs.append('{} - {}'.format(attr, value))

        return '\n'.join(attribs)

    def set_attributes(self, *attributes):
        '''
        Set attributes of instance after instantiation
        '''
        for dictionary in attributes:
            for key in dictionary:
                setattr(self, key, dictionary[key])


if __name__ == '__main__':
    es = EbayScraper(MANUAL_ATTRIBUTES, AUTO_SCRAPE_ATTRIBUTES)
    #es.get_search_result_page_urls()
    #es.get_new_items()
    #es.print_items()
    es.new_items['1'] = EbayItem()
    es.new_items['2'] = EbayItem()
    es.get_manual_input(['1', '2'])
    es.scrape_attributes(['1', '2'])
    #es.join_dfs()
    for ebay_id, item in es.new_items.items():
        print('\n' + ebay_id)
        print(item)
