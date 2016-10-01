#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4, urllib.request, datetime, sqlite3, json

def get_webdata(w):
#this function gets the specifics from a certain house advert and adds it to the dictionary
    fundaUrl = 'http://www.funda.nl'
    html = urllib.request.urlopen(fundaUrl + w['link']).read().decode('latin-1')
    soup = bs4.BeautifulSoup(html,'html.parser')
    r={}
    #print(soup.findAll('a'))
    for ad in soup.findAll(attrs={'class' : 'object-kenmerken-body'}):
        for n in ad.findAll(attrs={'class' : 'object-kenmerken-list'},recursive=False):
            for k in n.findAll(['dd','dt']):
                #print(k)
                try:
                    if k.find_next_sibling().name == 'dd':
                        r[k.text.strip()] = k.find_next_sibling().text.strip()
                except AttributeError:
                    next
    return(r)

#===== DEFINE SEARCH OPTIONS ======
MAX_PAGES = 9999999 #max number of pages to search
city = 'rotterdam'
minPrice=str(100000)
maxPrice=str(200000)

fundaUrl = 'http://www.funda.nl'
baseUrl = fundaUrl + '/koop/' + city + '/' + minPrice + '-' + maxPrice + '/' + 'bestaande-bouw' + '/'
#met garage:
#baseUrl = baseUrl + "/aangebouwde-garage/inpandige-garage/vrijstaande-garage/"
baseUrl = baseUrl + 'p'

data_file_name = 'data.json'

#===== START SCRAPE =====
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
print("Welcome! Today is ", current_date)
print("Scraping ... " + baseUrl)
html = urllib.request.urlopen(baseUrl).read().decode('latin-1')
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
    print("More pages found than MAX_PAGES -> only processing first " + str(MAX_PAGES) + " pages.\n")
    numberOfPages = MAX_PAGES
items = []

#load file if exists
try:
    with open(data_file_name, 'x+') as data_file:    
        data_file.write('[]')
        data = []
except FileExistsError:
    with open(data_file_name, 'r+') as data_file:
        data = json.load(data_file)
#print(json.dumps(data,indent=4))

#check each page
for pageNo in range(1, numberOfPages + 1):
    nextUrl = baseUrl + str(pageNo)
    print('Scraping page ' + str(pageNo) + ' - ' + nextUrl)
    html = urllib.request.urlopen(nextUrl).read().decode('latin-1')
    soup = bs4.BeautifulSoup(html,'html.parser')
    #check ads on page
    for ad in soup.findAll(attrs={'class' : 'search-result-content-inner'}):
        #extract basic data from each ad
        webdata = {}
        try:
            webdata['title']     = ad.find(attrs={'class':'search-result-title'}).contents[0].strip()
            webdata['subtitle']  = ad.find(attrs={'class':'search-result-subtitle'}).contents[0].strip()
            webdata['link']      = ad.find(attrs={'class':'search-result-header'}).a['href'].strip()
            webdata['price']     = ad.find(attrs={'class':'search-result-price'}).contents[0].replace('â\x82¬',"").replace("k.k.","").strip().replace(".","")
        except: #for any error, we just continue with the next add
            print('Error getting listing. Going to next ...')
            continue
        try: 
            webdata['area'] = ad.find(attrs={'title':'Woonoppervlakte'}).contents[0].replace("m²","").strip()
        except: #at an error for area, we do go on
            webdata['area'] = '0'
            
        #find if this entry exists in our json-data
        adAlreadyInDatabase = False
        for n in data:
            #print(data)
            if n['title']==webdata['title']:
                adAlreadyInDatabase = True
                newPrice = True
                for p in n['price']:
                    if p['date'] == current_date:
                        newPrice = False
                if newPrice:
                    print('Updating price for: ', [webdata['title'],webdata['subtitle']])
                    n['price'].append({'price':webdata['price'],'date': current_date})
                n['last_seen'] = current_date
                
        if not adAlreadyInDatabase: 
            print('Adding new entry: ',[webdata['title'],webdata['subtitle']])
            #get add specific data
            r = get_webdata(webdata)
            #add the high level info
            r['title'] = webdata['title']
            r['link'] = webdata['link']
            r['subtitle'] = webdata['subtitle']
            r['price'] = [{'price':webdata['price'],'date': current_date}]
            r['area'] = webdata['area']
            r['last_seen'] = current_date
            data.append(r)
    #to be sure, we write our data every page so we don't loose too much
    with open(data_file_name, 'w') as data_file:
        print('Writing to file ...')
        data_file.write(json.dumps(data,indent=4))    

#export the JSON


