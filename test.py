from miner import EbayItem

item = EbayItem({'id':'45324523', 'hdd':200})
print(item.id)
print(item.hdd)

item.set_attributes({'id':'fdsadfas'}, {'temp':'adfasdf'})
print(item.id)
print(item.temp)
