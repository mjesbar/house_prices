import os, pandas
from collect import clattr, BASE_DIR, LOGS_DIR
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date


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
driver.implicitly_wait(1.5)
#driver.minimize_window()



    ### Util functions ###
#=========================================================================================================================

def write_log(__message="\n", newl=True, __logfile=f"{LOGS_DIR}punpro.log"):
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
    baseurl = "https://www.puntopropiedad.com"
    write_log("Starting Scraping : Punto Propiedad ... \n")
    write_log(str(post_links.loc[post_links['website'] == baseurl, 'website'].count()) + " Records from <PuntoPropiedad>")
    write_log(str(post_links.loc[post_links['website'] != baseurl, 'website'].count()) + " Records from other sources")
    write_log("Total-----------")
    write_log(str(post_links['website'].count()) + " Records")

    # filtering 'metrocuadrado.com' only
    punpro = post_links.loc[post_links['website'] == baseurl]

    # verifying duplicated data
    if (len(punpro['code'].drop_duplicates()) - len(punpro['code']) == 0):
        write_log("No codes Duplicated")
    else:
        lendif = len(punpro['code']) - len(punpro['code'].drop_duplicates())
        write_log(f"{lendif} codes Duplicated")
        punpro = punpro.drop_duplicates('code')
        write_log(f"{len(punpro)} codes Stuck")
    
    # getting 'href' links
    links = list(punpro['href'].values)    # this is the final list to scrap every link previously obtained from collect.py
    
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
neighborhood_class = "location_info"
room_class = "bedrooms"
bath_class = "bathrooms"
area_class = "dimensions"
info_class = "tick"
price_class = "price"#[0 or 1]
price_area = lambda price, area: round(price/area)
offertype = "Venta"
#property
old_class = "tick"# repeated class



    ### Main execution ###
#=========================================================================================================================

if __name__ == '__main__':
    
    # opening the log file where we'll write all the process information
    os.system(f"touch {LOGS_DIR}punpro.log")
    
    __stop=0
    # starting road through links
    for link in range(len(links)):
        # going for every link
        driver.get(links[link])
        neighborhood, price, rooms, baths, built_area, private_area, old, parking_lot, stratus = [None] * 9
        
        try:
            # getting main info
            __header = driver.find_elements(By.CLASS_NAME, "priceChars")
            for h in __header:
                __info_key = h.text
                #print(repr(__info_key))
                if ("COP$" in __info_key):
                    price = h.find_element(By.CLASS_NAME, clattr(price_class))
                    price = price.text
                    price = price.replace(".","").replace(" ","").replace("COP$","")
                if ("m2" in __info_key):
                    built_area = h.find_element(By.CLASS_NAME, clattr(area_class))
                    built_area = built_area.text
                    built_area = built_area.replace("m2","")
                    private_area = built_area
                if ("Habitaciones" in __info_key):
                    rooms = h.find_element(By.CLASS_NAME, clattr(room_class))
                    rooms = rooms.text
                    rooms = rooms.split(" ")[0]
                if ("Baños" in __info_key):
                    baths = h.find_element(By.CLASS_NAME, clattr(bath_class))
                    baths = baths.text
                    baths = baths.split(" ")[0]
     
            # getting miscellaneus info
            __info = driver.find_elements(By.CLASS_NAME, clattr(info_class))

            for i in __info:
                #print(i.text)
                __info_key = i.text
                if ("Área útil" in __info_key):
                    built_area = __info_key.split(": ")[-1]
                    private_area = built_area
                if ("Estrato" in __info_key):
                    stratus = __info_key.split(": ")[-1]
                if ("Parqueadero" in __info_key):
                    parking_lot = str(1)
                if ("Año de construcción" in __info_key):
                    old = __info_key.split(": ")[-1]
                    old = old.replace(".","")
                    old = date.today().year - int(old)
                    old = str(old)
                    
            neighborhood = driver.find_element(By.CLASS_NAME, clattr(neighborhood_class))
            neighborhood = neighborhood.text
            neighborhood = neighborhood.split(",")[0]

        except:
            write_log(f"[{link}/{len(links)}] [ERROR] link:{links[link]} ... skiped")
            continue
        
        # confirming the struture of information
        #print(repr(neighborhood), repr(rooms), repr(baths), repr(price), repr(old), repr(built_area), repr(private_area), repr(stratus), repr(parking_lot))
        
        # printing the gathering status
        write_log(f"[{link}/{len(links)}] [OK] link:{links[link]} ... ")
        
        try:
            neighborhood = str(neighborhood)
            price = str(price)
            built_area = str(built_area)
            # appending scraped-data into data dictionary
            write_log("Appending data ... ", newl=False)
            data['code'].append(punpro['code'].values[link])
            data['neighborhood'].append(neighborhood)
            data['city'].append(punpro['city'].values[link].capitalize())
            data['offer type'].append(offertype.capitalize())
            data['property'].append(punpro['facility'].values[link].capitalize())
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
            #print(data)
        except:
            write_log("Data Successfully appended [FAILURE]")
            continue

        #__stop += 1    # used to stop the for loop due to test purposes
        if (__stop == 30):
            break

    # saving data to .dat file
    write_log("Saving data collect to punpro.dat ... ", newl=False)
    try:
        df = pandas.DataFrame(data=data)
        df.to_csv(f"{BASE_DIR}/data/punpro.dat", sep=",", na_rep="", header=False) 
    except:
        write_log("Error: Data Not Saved [FAILURE]")
    else:
        write_log("Data Saved to punpro.dat [OK], exiting script ...")


    driver.quit()


