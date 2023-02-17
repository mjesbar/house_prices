import os, pandas
from collect import clattr
from collect import BASE_DIR, LOGS_DIR
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

    ### Creating WebDriver ###
#========================================================================================================================

options = webdriver.ChromeOptions()
options.add_argument('--incognito')
options.add_argument('--headless')
options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
options.add_argument('--blink-settings=imagesEnabled=false')
options.page_load_strategy = 'eager'
#options.add_argument('--window-position=960,0')
#options.add_argument('--window-size=960,1080')

service = Service(executable_path=ChromeDriverManager().install())

driver = webdriver.Chrome(options=options, service=service)
#driver.minimize_window()



    ### Util functions ###
#=======================================================================================================================

def write_log(__message="\n", newl=True, __logfile=f"{LOGS_DIR}mecu.log"):
    # printing conditional
    if (newl):
        print(__message)
        # writing logfile
        with open(__logfile, "a") as file:
            file.write(__message + "\n")
    else:
        print(__message, end="")
        # writing logfile
        with open(__logfile, "a") as file:
            file.write(__message)



    ### Catching all the Post data from Metro Cuadrado ###
#========================================================================================================================

post_links = pandas.read_csv(f"{BASE_DIR}/data/collect.dat")

if (post_links.empty):
    raise Exception("CsvFileEmpty: The csv file has no information.")
else:
    # verifying data integrity and value counting
    baseurl = "https://www.metrocuadrado.com"
    write_log("Starting Scraping : Metro Cuadrado ... \n")
    write_log(str(post_links.loc[post_links['website'] == baseurl, 'website'].count()) + " Records from <MetroCuadrado>")
    write_log(str(post_links.loc[post_links['website'] != baseurl, 'website'].count()) + " Records from other sources")
    write_log("Total-----------")
    write_log(str(post_links['website'].count()) + " Records")

    # filtering 'metrocuadrado.com' only
    mecu = post_links.loc[post_links['website'] == baseurl]

    # verifying duplicated data
    if (len(mecu['code'].drop_duplicates()) - len(mecu['code']) == 0):
        write_log("No codes Duplicated")
    else:
        lendif = len(mecu['code']) - len(mecu['code'].drop_duplicates())
        write_log(f"{lendif} codes Duplicated")
        mecu = mecu.drop_duplicates('code')
        write_log(f"{len(mecu)} codes Stuck")
    
    # getting 'href' links
    links = list(mecu['href'].values)    # this is the final list to scrap every link previously obtained from collect.py

    # dictionary that will be populated with data from every iteration in the main scope
    data = {
        'code':[],
        'neighborhood':[],
        'city':[],
        'offer type':[],
        'property':[],
        'rooms':[],
        'baths':[],
        'parking lots':[],
        'private area':[],
        'built area':[],
        'stratus':[],
        'price':[],
        'price/area':[],
        'old':[]
    }


    ### tag classes to find in site ###
#========================================================================================================================

#city
neighborhood_class = 'H1-xsrgru-0 jdfXCo mb-2 card-title'
headers_class = 'H2-kplljn-0 igCxTv vcenter-text card-text'
basics_class = 'Col-sc-14ninbu-0 lfGZKA mb-3 pb-1 col-12 col-lg-3'
stratus_class = "H2-kplljn-0 igCxTv card-text"
price_area = lambda price, area: round(price/area)
offertype = "Venta"
#property



    ### Main execution ###
#=========================================================================================================================

if __name__ == '__main__':

    # opening the log file where we'll write all the process information
    os.system(f"touch {LOGS_DIR}mecu.log")

    __stop=0
    # starting road through links
    for link in range(len(links)):
        # going for every link
        driver.get(links[link])
        neighborhood, price, rooms, baths, built_area, private_area, old, parking_lot, stratus = [None] * 9

        try:
            # getting the neighborhood
            try:
                neighborhood = driver.find_element(By.CLASS_NAME, clattr(neighborhood_class))
                neighborhood = neighborhood.text
                neighborhood = neighborhood.split(",")[1]
                neighborhood = neighborhood.lstrip()
                neighborhood = neighborhood.capitalize()
            except:
                pass

            # getting main information
            __header = driver.find_elements(By.CLASS_NAME, clattr(headers_class))
            # locating such data in webpage
            for h in __header:
                __info_key =  h.find_element(By.TAG_NAME, 'span').text
                __info_value =  h.text
                #print("->", __info_key, "|", __info_value)
                # addigning info to variables
                if (__info_key == 'Habitaciones'): 
                    rooms = __info_value
                    rooms = rooms.splitlines()[0]
                if (__info_key == 'Baños'):
                    baths = __info_value
                    baths = baths.splitlines()[0]
            
            # getting stratus info which has a special tag
            __stratus_tag = driver.find_elements(By.CLASS_NAME, clattr(stratus_class))
            for s in __stratus_tag:
                __info_key =  s.find_element(By.TAG_NAME, 'span').text
                __info_value =  s.text
                #print("->", __info_key, "|", __info_value)
                if (__info_key == 'Estrato'):
                    stratus = __info_value
                    stratus = stratus.splitlines()[0]

            # getting miscellaneous information
            __info = driver.find_elements(By.CLASS_NAME, clattr(basics_class))
            # locating such data in webpage
            for c in __info:
                __info_key =  c.find_element(By.TAG_NAME, 'h3').text
                __info_value =  c.find_element(By.TAG_NAME, 'p').text
                #print("->", __info_key, "|", __info_value)
                # assigning info to variables
                if (__info_key == 'Precio'):
                    price = __info_value    
                    price = price.replace("$","").replace(".","")
                if (__info_key == 'Antigüedad'):
                    old = __info_value
                    old = old.replace("Más de ", "").replace("Entre ","").replace(" años","").replace(" y ", "-")
                if (__info_key == 'Área construida'):
                    built_area = __info_value
                    built_area = built_area.split(" ")[0]
                if (__info_key == 'Área privada'):
                    private_area = __info_value
                    private_area = private_area.split(" ")[0]
                if (__info_key == 'Parqueaderos'):
                    parking_lot = __info_value
            
        except:
            write_log(f"[{link}/{len(links)}] [ERROR] link:{links[link]} ... Skiped")
            continue
        
        # confirming the struture of information
        #print(repr(neighborhood), repr(rooms), repr(baths), repr(price), repr(old), repr(built_area), repr(private_area), repr(parking_lot), repr(stratus))
        
        # printing the gathering status
        write_log(f"[{link}/{len(links)}] [OK] link:{links[link]}")
        
        try:
            neighborhood = str(neighborhood)
            price = str(price)
            built_area = str(built_area)
            # appending scraped-data into data dictionary
            write_log("Appending data ... ", newl=False)
            data['code'].append(mecu['code'].values[link])
            data['neighborhood'].append(neighborhood.capitalize())
            data['city'].append(mecu['city'].values[link].capitalize())
            data['offer type'].append(offertype.capitalize())
            data['property'].append(mecu['facility'].values[link].capitalize())
            data['rooms'].append(rooms)
            data['baths'].append(baths)
            data['parking lots'].append(parking_lot)
            data['built area'].append(built_area)
            data['private area'].append(private_area)
            data['stratus'].append(stratus)
            data['price'].append(price)
            data['price/area'].append(price_area(float(price), float(built_area)))
            data['old'].append(old)
            write_log("Data Successfully appended [OK]")
        except:
            write_log("Data Successfully appended [FAILURE]")
            continue

        #__stop += 1    # used to stop the for loop due to test purposes
        if (__stop == 30):
            break

    # saving data to .dat file
    write_log("Saving data collect to mecu.dat ... ", newl=False)
    try:
        df = pandas.DataFrame(data=data)
        df.to_csv(f"{BASE_DIR}/data/mecu.dat", sep=",", na_rep="", header=False) 
    except:
        write_log("Error: Data Not Saved [FAILURE]")
    else:
        write_log("Data Saved to mecu.dat [OK], exiting script ...")


    driver.quit()


