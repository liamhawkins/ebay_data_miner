'''
TODO:
    Add/Check for Errors
    Implement proper error handling
    Cleanup requirements.txt
    Confirm prompts before moving to next
    When scraping error encountered prompt manual entry
    Fix EbayItem.sold, always set to yes
    Add proper doc strings
'''
import pandas as pd
import os
import urllib.request
import selenium
from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime
from prompt_toolkit import prompt
from selenium import webdriver

BROWSER = 'firefox'
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
MANUAL_ATTRIBUTES['dock'] = 'Dock'


class EbayScraper:

    def __init__(self, manual_attributes):
        self.unfilled_items = []
        self.new_items = []
        self.manual_attributes = manual_attributes
        self.full_attribute_df = pd.DataFrame()

    def read_item_database(self):
        try:
            self.db = pd.read_csv(DATABASE)
            self.db_ids = [str(i) for i in self.db['ebay_id'].tolist()]
        except FileNotFoundError:
            print('Database not found, a new one will be created')

    def write_item_database(self):
        items_attribs = list()
        for item in self.new_items:
            items_attribs.append(vars(item))
        item_df = pd.DataFrame(items_attribs)
        if os.path.isfile(DATABASE):
            with open(DATABASE, 'a') as f:
                item_df.to_csv(f, header=False)
        else:
            item_df.to_csv(DATABASE)

    def get_search_results(self):
        '''
        Scrapes ebay search results and returns urls of first 3 pages
        '''
        self.search_result_page_urls = []
        for pg_num in range(1, 4):  # TODO: determine this num with logic
            if pg_num == 1:
                page = ''
            else:
                page = '&_pgn=' + str(pg_num) + \
                       '&_skc=' + str((pg_num - 1) * 200)

            url = 'http://www.ebay.ca/sch/i.html?_from=R40&_sacat=0' \
                  '&LH_Complete=1&_udlo=&_udhi=&LH_Auction=1&LH_BIN=1' \
                  '&_samilow=&_samihi=&_sadis=15&_stpos=k1r7t8&_sop=13' \
                  '&_dmd=1&_nkw=thinkpad+x220' + page + '&rt=nc'
            self.search_result_page_urls.append(url)

    def get_new_items(self):
        '''
        After search result URLs are scraped,
        creates dictionary will all itemIDs and item URLs
        '''
        for url in self.search_result_page_urls:
            r = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(r, 'html.parser')
            listings = soup.find_all('li', class_='sresult ' +
                                     'lvresult clearfix li')
            for element in listings:
                listing_id = element['listingid']
                item = element.find('a', class_='img imgWr2')
                listing_url = item['href']
                if hasattr(self, 'db'):
                    if not (listing_id in self.db_ids):
                        self.unfilled_items.append(EbayItem({'ebay_id': listing_id, 'item_url': listing_url}))
                else:
                    self.unfilled_items.append(EbayItem({'ebay_id': listing_id, 'item_url': listing_url}))

    def print_items(self):
        '''
        Prints ebay items with completed attributes
        '''
        for item in self.new_items:
            print(item)

    def print_manual_attributes(self):
        '''
        Prints ebay item attributes that need manual input
        '''
        for attrib, question in self.manual_attributes.items():
            print('Attribute: {} - Question: {}:'.format(attrib, question))

    def process_items(self):
        if BROWSER == 'firefox':
            driver = webdriver.Firefox()
        elif BROWSER == 'chrome':
            driver = webdriver.Chrome()
        elif BROWSER == 'edge':
            driver = webdriver.Edge()
        elif BROWSER == 'safari':
            driver = webdriver.Safari()
        else:
            raise ValueError('{} is not a currently supported browser, feel free to make a pull request'.format(BROWSER))
        driver.set_window_rect(x=0, y=0, width=1920//2, height=1080)  # TODO: Remove hardcoding with screeninfo
        driver.accept_untrusted_certs = True
        driver.assume_untrusted_cert_issuer = True
        for item in self.unfilled_items:
            try:
                try:
                    driver.get(item.item_url)
                except selenium.common.exceptions.WebDriverException:  # XXX: BAD FIREFOX, FIX THIS
                    pass
                print('--------------')
                print('({}/{}) - {}'.format(self.unfilled_items.index(item)+1,
                                            len(self.unfilled_items),
                                            item.ebay_id))
                print('--------------')
                item.prompt_item_attributes(self.manual_attributes)
                item.scrape_attributes()
                self.new_items.append(item)
            except KeyboardInterrupt:
                print('Ctrl-C Detected...Closing and writing database')
                try:
                    driver.quit()
                except selenium.common.exceptions.WebDriverException:  # XXX: BAD FIREFOX, FIX THIS
                    pass
                return
        try:
            driver.quit()
        except selenium.common.exceptions.WebDriverException:  # XXX: BAD FIREFOX, FIX THIS
            pass


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

    def get_date_completed(self, main_content):
        try:
            span = main_content.find('span', {'class': 'timeMs'})
            ms = span.attrs['timems']
            self.date_completed = datetime.fromtimestamp(int(ms)/1000)
        except AttributeError:  # FIXME: Error occurs alot
            print('CANNOT DETERMINE DATE COMPLETED')
            self.date_completed = 'PARSING ERROR'

    def get_sold_type_and_status(self, main_content):
        # TODO: Scrape for # bids if auction
        sold_for = len(main_content.findAll(text='Sold for:'))
        winning_bid = len(main_content.findAll(text='Winning bid:'))
        price = len(main_content.findAll(text='Price:'))
        starting_bid = len(main_content.findAll(text='Starting bid:'))

        if sold_for > 0 or winning_bid > 0:   # FIXME: ALWAYS RETURNS YES
            self.sold = 1
        elif price > 0 or starting_bid > 0:
            self.sold = 0
        else:
            print('PARSING ERROR! CANNOT DETERMINE SOLD STATUS')
            self.sold = 'PARSING ERROR'

        if sold_for > 0 or price > 0:
            self.listing_type = 'Buy it now'
        elif winning_bid > 0 or starting_bid > 0:
            self.listing_type = 'Auction'
        else:
            print('PARSING ERROR! CANNOT DETERMINE LISTING TYPE')
            self.listing_type = 'PARSING ERROR'

    def get_location(self, soup):
        location = soup.find('span', {'itemprop': 'availableAtOrFrom'})
        self.location = location.get_text()

    def get_price_shipping_import(self, soup):
        price = soup.find('span', {'itemprop': 'price'})
        self.price = price.attrs['content']

        # TODO: Check for free shipping
        shipping = soup.find('span', {'id': 'fshippingCost'})
        shipping = shipping.find('span')
        shipping = shipping.get_text()
        shipping = shipping.split()
        self.shipping = shipping[1][1:]

        import_ = soup.find('span', {'id': 'impchCost'})
        if len(import_) > 0:
            import_ = import_.get_text()
            import_ = import_.split()
            self.import_cost = import_[1][1:]
        else:
            self.import_cost = 0

    def get_seller_information(self, soup):
        top_rated = soup.findAll('a', href='http://pages.ebay.ca/topratedsellers/index.html')
        if len(top_rated) > 0:
            self.top_rated = 1
        else:
            self.top_rated = 0

        feedback_score = soup.find('span', class_='mbg-l')
        feedback_score = feedback_score.find('a')
        self.feedback_score = feedback_score.get_text()

        feedback_percentage = soup.find('div', id='si-fb')
        feedback_percentage = feedback_percentage.get_text()
        feedback_percentage = feedback_percentage.split('%')
        self.feedback_percentage = feedback_percentage[0]

    def scrape_attributes(self):
        # TODO: Implement scrapers: # bids
        print('Scraping in progress...')
        r = urllib.request.urlopen(self.item_url).read()
        soup = BeautifulSoup(r, 'html.parser')
        self.get_date_completed(soup)
        self.get_sold_type_and_status(soup)
        self.get_location(soup)
        self.get_price_shipping_import(soup)
        self.get_seller_information(soup)

    def prompt_item_attributes(self, manual_attributes):
        inp_dict = dict()
        for attrib, question in manual_attributes.items():
            inp_dict[attrib] = prompt('{}: '.format(question))
        self.set_attributes(inp_dict)


if __name__ == '__main__':
    es = EbayScraper(MANUAL_ATTRIBUTES)
    es.read_item_database()
    es.get_search_results()
    es.get_new_items()
    es.process_items()
    es.write_item_database()
