'''
TODO:
    Add/Check for Errors
    Implement proper error handling
    Cleanup requirements.txt
    Add proper doc strings
    remove hardcoding url
'''
import pandas as pd
import os
import urllib.request
import selenium
import json
from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.contrib.completers import WordCompleter
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
MANUAL_ATTRIBUTES['lot_size'] = 'Lot Size'


class EbayScraper:

    def __init__(self, manual_attributes):
        self.unfilled_items = []
        self.new_items = []
        self.manual_attributes = manual_attributes
        self.full_attribute_df = pd.DataFrame()

    def read_item_database(self):
        '''Read DATABASE file and store as EbayScraper.db, and extract 'ebay_id's as strings stored in EbayScraper.db_ids'''
        # TODO: UPDATE DOC STRING
        self.completion_dict = dict()
        try:
            self.db = pd.read_csv(DATABASE)
            self.db_ids = [str(i) for i in self.db['ebay_id'].tolist()]

            for key in self.manual_attributes:
                    self.completion_dict[key] = WordCompleter([str(i) for i in self.db[key].tolist() if str(i) != 'nan'], ignore_case=True)

        except FileNotFoundError:
            for key in self.manual_attributes:
                self.completion_dict[key] = WordCompleter([], ignore_case=True)  # TODO: Refactor to avoid duplication
            print('Database not found, a new one will be created')

    def write_item_database(self):
        '''Write EbayScraper.new_items to DATABASE .csv file'''
        items_attribs = list()
        for item in self.new_items:
            items_attribs.append(vars(item))
        item_df = pd.DataFrame(items_attribs)
        if os.path.isfile(DATABASE):
            with open(DATABASE, 'a') as f:
                item_df.to_csv(f, header=False)
        else:
            item_df.to_csv(DATABASE)

    def get_num_search_result_pages(self, orig_url):
        r = urllib.request.urlopen(orig_url).read()
        soup = BeautifulSoup(r, 'html.parser')
        num_results = soup.find('span', class_='rcnt').get_text()
        num_results_pages = int(int(num_results) / 50)
        return num_results_pages if num_results_pages % 50 == 0 else num_results_pages + 1


    def get_search_results(self):
        '''Scrape ebay search results and store urls of first 3 pages in EbayScraper.search_result_page_urls'''
        self.search_result_page_urls = []
        orig_url = ('http://www.ebay.ca/sch/i.html?_from=R40&_nkw=thinkpad+x220'
                    '&_in_kw=1&_ex_kw=&_sacat=0&LH_Complete=1&_udlo=&_udhi=&LH_A'
                    'uction=1&LH_BIN=1&_samilow=&_samihi=&_sadis=15&_stpos=k1r7t8'
                    '&_sargn=-1%26saslc%3D1&_salic=2&_sop=13&_dmd=1&_ipg=200')
        num_search_result_pages = self.get_num_search_result_pages(orig_url)
        for pg_num in range(num_search_result_pages + 1):  # TODO: determine this num with logic
            if pg_num == 1:
                page = ''
            else:
                page = '&_pgn=' + str(pg_num) + \
                       '&_skc=' + str((pg_num - 1) * 50)

            url = (
               'http://www.ebay.ca/sch/i.html?_from=R40&_sacat=0'
               '&LH_Complete=1&_udlo=&_udhi=&LH_Auction=1&LH_BIN=1'
               '&_samilow=&_samihi=&_sadis=15&_stpos=k1r7t8&_sop=13'
               '&_dmd=1&_nkw=thinkpad+x220' + page + '&rt=nc'
            )
            self.search_result_page_urls.append(url)

    def get_new_items(self):
        '''
        Create EbayItem objects for items not in database

        Parse URLs from EbayScraper.search_result_page_urls, check that corresponding listing id
        is not already present in DATABASE, and create EbayItem object containing ebay_id and item_url
        for each listing. Then store each EbayItem in EbayScraper.unfilled_items
        '''
        for url in self.search_result_page_urls:
            r = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(r, 'html.parser')
            listings = soup.find_all('li', class_='sresult ' +
                                     'lvresult clearfix li')
            for element in listings:
                listing_id = element['listingid']
                item = element.find('a', class_='img imgWr2')
                # TODO: Find out what causes this error
                try:
                    listing_url = item['href']
                except TypeError:
                    pass
                if hasattr(self, 'db'):
                    if not (listing_id in self.db_ids):
                        self.unfilled_items.append(EbayItem({'ebay_id': listing_id, 'item_url': listing_url}))
                else:
                    self.unfilled_items.append(EbayItem({'ebay_id': listing_id, 'item_url': listing_url}))

    def print_items(self):
        '''Print ebay items that have had attributes filled in (Stored in EbayScraper.new_items)'''
        for item in self.new_items:
            print(item)

    def print_manual_attributes(self):
        '''Prints ebay item attributes that need manual input'''
        for attrib, question in self.manual_attributes.items():
            print('Attribute: {} - Question: {}:'.format(attrib, question))

    def process_items(self):
        '''
        Loop over EbayScraper.unfilled_items, open url, prompt user for attribute input, then scrape

        Uses BROWSER to determine which selenium webdriver to use. Launches webdriver and opens url
        from EbayItem.item_url. Then calls EbayItem.prompt_item_attributes() to gather manual input
        for attributes that cannot be scraped. After manual input is complete it calls
        EbayItem.scrape_attributes(). After all attributes are collected the EbayItem is appended to
        EbayScraper.new_items, and this process is repeated with the next EbayItem until CTRL+C is
        detected or there are no more EbayItem objects in EbayScraper.unfilled_items
        '''
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
        try:
            driver.set_window_rect(x=0, y=0, width=1920//2, height=1080)  # TODO: Remove hardcoding with screeninfo
        except selenium.common.exceptions.WebDriverException:
            print('Cant set window parameters')
        driver.accept_untrusted_certs = True
        driver.assume_untrusted_cert_issuer = True
        for item in self.unfilled_items:
            try:
                try:
                    print('Loading listing webpage...')
                    driver.get(item.item_url)
                except selenium.common.exceptions.WebDriverException:  # XXX: BAD FIREFOX, FIX THIS
                    pass
                print('--------------')
                print('({}/{}) - {}'.format(self.unfilled_items.index(item)+1,
                                            len(self.unfilled_items),
                                            item.ebay_id))
                print('--------------')
                self.completion_dict = item.prompt_item_attributes(self.manual_attributes, self.completion_dict)
                item.scrape_attributes()
                _ = os.system('clear')
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
        '''Loop over object variables and print each one'''
        attribs = []
        for attr, value in vars(self).items():
            attribs.append('{} - {}'.format(attr, value))
        return '\nEbay item: ' + self.ebay_id + '\n' + '\n'.join(attribs)

    def set_attributes(self, *attributes):
        '''Set/update attributes of instance after instantiation'''
        for dictionary in attributes:
            for key in dictionary:
                setattr(self, key, dictionary[key])

    def get_location(self, soup):
        '''Scrape listing page for location item is shipping from'''
        location = soup.find('span', {'itemprop': 'availableAtOrFrom'})
        self.location = location.get_text()

    def get_price_shipping_import(self, soup):
        '''Scrape listing page for shipping, and import fees'''
        shipping = soup.find('span', {'id': 'fshippingCost'})
        try:
            shipping = shipping.find('span')
            shipping = shipping.get_text()
            if shipping == 'FREE':
                self.shipping = 0
            else:
                shipping = shipping.split()
                self.shipping = shipping[1][1:]
        except AttributeError:
            self.shipping = 'Does not ship to Canada'

        import_ = soup.find('span', {'id': 'impchCost'})
        if len(import_) > 0:
            import_ = import_.get_text()
            import_ = import_.split()
            self.import_cost = import_[1][1:]
        else:
            self.import_cost = 0

    def get_seller_information(self, soup):
        '''Scrape listing page for whether seller is top rated, their feedback score, and positive feedback percentage'''
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

    @staticmethod
    def get_json(soup):
        json_start = str(soup).find('{"largeButton"')
        json_end = str(soup).find('"key":"ItemSummary"}')
        json_data = str(soup)[json_start:json_end+len('"key":"ItemSummary"}')]
        json_data = json.loads(json_data)
        return json_data

    def get_times(self, json_data):
        self.start_time = json_data['startTime']
        self.end_time = json_data['endTime']

        start = datetime.fromtimestamp(int(self.start_time)//1000)
        end = datetime.fromtimestamp(int(self.end_time)//1000)
        self.duration_days = (end - start).days

    def get_json_listing_type_and_status(self, json_data):
        self.item_condition = json_data['itmCondition']

        if json_data['bin']:
            self.listing_type = 'Buy it now'
            self.price = json_data['convertedBinPrice']
        elif json_data['bid']:
            self.listing_type = 'Auction'
            self.price = json_data['convertedBidPrice']

        if json_data['won'] or json_data['sold']:
            self.sold = 'True'
        elif json_data['reserveNotMet']:
            self.sold = 'Reserve Not Met'
        else:
            self.sold = 'False'

        self.bids = json_data['totalBids']

    def scrape_attributes(self):
        '''Create BeautifulSoup object that is then passed to parsing methods'''
        print('Scraping in progress...')
        try:
            r = urllib.request.urlopen(self.item_url).read()
            soup = BeautifulSoup(r, 'html.parser')
            json_data = self.get_json(soup)
            self.get_times(json_data)
            self.get_json_listing_type_and_status(json_data)
            self.get_location(soup)
            self.get_price_shipping_import(soup)
            self.get_seller_information(soup)
        except json.JSONDecodeError:
            print('JSON ERROR - RETRYING')
            self.scrape_attributes()

    def prompt_item_attributes(self, manual_attributes, completion_dict):
        '''Prompts user to input attributes defined in MANUAL_ATTRIBUTES'''
        # TODO: UPDATE DOC STRING
        inp_dict = dict()
        for attrib, question in manual_attributes.items():
            inp_dict[attrib] = prompt('{}: '.format(question), completer=completion_dict[attrib], complete_while_typing=True)
            if inp_dict[attrib] not in completion_dict[attrib].words:
                if inp_dict[attrib] != '':
                    completion_dict[attrib].words.append(inp_dict[attrib])
        answer = confirm('\nAre these details correct? (y/n) ')
        if answer:
            self.set_attributes(inp_dict)
        else:
            completion_dict = self.prompt_item_attributes(manual_attributes, completion_dict)

        return completion_dict


if __name__ == '__main__':
    es = EbayScraper(MANUAL_ATTRIBUTES)
    es.read_item_database()
    es.get_search_results()
    es.get_new_items()
    es.process_items()
    es.write_item_database()
