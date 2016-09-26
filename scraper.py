# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

# import scraperwiki
# import lxml.html
#
# # Read in a page
# html = scraperwiki.scrape("http://foo.com")
#
# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library
# scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries.
# You can use whatever libraries you want: https://morph.io/documentation/python
# All that matters is that your final data is written to an SQLite database
# called "data.sqlite" in the current working directory which has at least a table
# called "data".

import bs4, urllib.request, datetime, sqlite3

#start database
conn = sqlite3.connect('data.sqlite')
c = conn.cursor()

#make sure we have a table called data
c.execute("CREATE TABLE IF NOT EXISTS data (title text, link text, subtitle text, price integer, area integer);")
#scraperwiki.metadata.save('data_columns', ['id', 'date', 'street', 'city', 'postcode', 'livingspace', 'otherspace', 'price'])

MAX_PAGES = 1 #max number of pages to search
city = 'rotterdam'
minPrice=str(100000)
maxPrice=str(200000)

fundaUrl = 'http://www.funda.nl'
startUrl = fundaUrl + '/koop/' + city + '/' + minPrice + '-' + maxPrice + '/' + '/' + 'bestaande-bouw' + '/'

#met garage:
#startUrl = startUrl + "/aangebouwde-garage/inpandige-garage/vrijstaande-garage/"

baseUrl = startUrl

print(baseUrl)

html = urllib.request.urlopen(startUrl).read().decode('latin-1')
soup = bs4.BeautifulSoup(html,'html.parser')

#print(soup.prettify('latin-1'))

# get number of pages
try:
	pages = soup.findAll(attrs={'class' : 'pagination-number pagination-last'})
	numberOfPages = int(pages[0]['data-pagination-page'])
except IndexError:
	print("IndexError when trying to find number of pages")
	numberOfPages = 1
	
print("Pages found: " + str(numberOfPages))

if numberOfPages > MAX_PAGES:
	print("More pages found than MAX_PAGES -> only processing first " + str(MAX_PAGES) + " pages.")
	numberOfPages = MAX_PAGES
items = []
today = datetime.date.today()



for pageNo in range(1, numberOfPages + 1):
 
    nextUrl = baseUrl + str(pageNo)
    print('page: ' + nextUrl)
    html = urllib.request.urlopen(nextUrl).read().decode('latin-1')
    soup = bs4.BeautifulSoup(html,'html.parser')
    #print(soup.findAll('a'))
    for ad in soup.findAll(attrs={'class' : 'search-result-content-inner'}):
        #print(ad)
        item = {}
        item['title']    = ad.find(attrs={'class':'search-result-title'}).contents[0].strip()
        item['link']     = ad.find(attrs={'class':'search-result-header'}).a['href'].strip()        
        item['subtitle'] = ad.find(attrs={'class':'search-result-subtitle'}).contents[0].strip()
        item['price']    = ad.find(attrs={'class':'search-result-price'}).contents[0].replace('â\x82¬',"").replace("k.k.","").strip().replace(".","")
        item['area']     = ad.find(attrs={'title':'Woonoppervlakte'}).contents[0].replace("m²","").strip()
        
		
        print(item)
        #print(ad.find(attrs={'class':'search-result-price'}).string)
        #for item in ad.find(attrs={'class':'search-result-price'}):
        #    print(item.string)
            #realItem['id'] = fundaUrl + item['href']
                    
        #items.append(realItem)
        #scraperwiki.datastore.save(unique_keys=['id'], data=realItem)
        #print('items saved: ' + str(len(items)))
