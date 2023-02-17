import sys
import csv
import random
import requests
from bs4 import BeautifulSoup as besoup

# NOTE:
# this script is experimental and it is not implemented in the process due to proxies were too slow



### functions Scope ###
#----------------------------------------------------------------------------------------------------------------------------------------

def roll_proxy(proxy_list, module="bs"):
    
    # Rotate proxy for new requests apart of ourself original IP data
    if module == "bs":
        proxy_bs = {
            'https':proxy_list[random.randint(0,len(proxy_list)-1)]
        }
        print(f"Using IP Proxy: {proxy_bs} ... ")
        return proxy_bs
    elif module == "se": 
        proxy_se = proxy_list[random.randint(0,len(proxy_list)-1)]
        print(f"Using IP Proxy: {proxy_se} ... ")
        return proxy_se

test_proxy = {'https':'173.249.198.244:8080'}

### Attributes Scope ###
#---------------------------------------------------------------------------------------------------------------------------------------- 

_FOUND_URL = 'https://www.showmyip.com'
_HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

_proxies = []
with open("../proxies.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for row in reader:
        data_to_append = str("https://%s:%s" % (row[0], row[1]))
        _proxies.append(data_to_append)    

# seeking the connnection (original)
_response = requests.request('GET', url=_FOUND_URL, headers=_HEADERS, timeout=10)

# obtaining the html page
_page = besoup(_response.text, 'html.parser')

# Obtaining the table where is the information about our IP address
_table = _page.find('table', class_='iptab').find_all('tr')

### The following is not human readable
# gathering every data about ip
ipdata = {}
ipdata['IPv4'] = _table[0].find_all('td')[1].find('b').string
ipdata['IPv6'] = _table[1].find_all('td')[1].find('div', id='ipv6').string  #this one is dinamically charged from page
ipdata['Country'] = _table[2].find_all('td')[1].string
ipdata['Region'] = _table[3].find_all('td')[1].string
ipdata['City'] = _table[4].find_all('td')[1].string
ipdata['Zip_'] = _table[5].find_all('td')[1].string
ipdata['Timezone'] = _table[6].find_all('td')[1].string
ipdata['ISP'] = _table[7].find_all('td')[1].string
ipdata['Organization'] = _table[8].find_all('td')[1].string 
ipdata['AS_number'] = _table[9].find_all('td')[1].string 
ipdata['user_agent'] = _table[0].find_all('td')[1].string 



### Module's Isolated Execution ###
#-----------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    msg = "\nData Extracted:\n"
    print(msg)
    for item, value in ipdata.items():
        print(" > ", item, ' - ', value, end="\n")

    print()







