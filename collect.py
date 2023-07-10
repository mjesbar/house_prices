
import os, time, pandas
from threading import Thread
from selenium import webdriver
from selenium.webdriver import common
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# *************************************************************************************************************
#
# The following script does web scraping of the sites 'metrocuadrado.com', 'fincaraiz.com', 'puntopropiedad.com'
# with the aim of gather data related to prices of Offices, Apartments and  Houses.
#
# *************************************************************************************************************

BASE_DIR = './'
LOGS_DIR = './logs/'

### Creating the WebDriver ###
#=======================================================================================================================================

options = webdriver.ChromeOptions()
options.page_load_strategy = 'normal'
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
options.add_argument('--headless')
options.add_argument('--incognito')
options.add_argument('--blink-settings=imagesEnabled=false')
#options.add_argument('--window-position=960,0')
#options.add_argument('--window-size=960,1080')

### Defining script variables
#=======================================================================================================================================

# iterable lists
baseurl = ['https://www.metrocuadrado.com',
           'https://fincaraiz.com.co',
           'https://www.puntopropiedad.com']

cities = ['buenaventura','barranquilla','mompos','barrancabermeja','cali','cartagena',
          'medellin','bogota','riohacha','santa-marta','turbo','tumaco']

facility = ['casa','apartamento','oficina']

via = 'venta'

### Metro Cuadrado tag classes
# 'li' tag of every item
mecu_list_class = "sc-gPEVay dibcyk card-result-img"
# 'a' tag contained in 'li' tag, used to redirect to the post page
mecu_link_class = "sc-bdVaJa ebNrSm"
# 'ul' page numbers list
page_number_class = "sc-dVhcbM kVlaFh Pagination-w2fdu0-0 cxBThU paginator justify-content-center align-items-baseline pagination"
# 'a' page link number: this will allow to get last page of each searching
page_number_box_class = "page-item"
page_active_class = "page-item active disabled"

### Finca raiz tag_classes
# 'div' tags that contains 'a' tags
finra_link_class = "MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-sm-6 MuiGrid-grid-lg-4 MuiGrid-grid-xl-4"
# 'button' tags to click on
finra_page_number_class = "MuiButtonBase-root MuiPaginationItem-root MuiPaginationItem-page MuiPaginationItem-outlined MuiPaginationItem-rounded"
finra_page_end_class = "MuiButtonBase-root MuiPaginationItem-root MuiPaginationItem-page MuiPaginationItem-outlined MuiPaginationItem-rounded Mui-disabled Mui-disabled"

### PuntoPropiedad tag_classes
# 'li' tags
punpro_list_box_class = "ad featured"
# 'a' tag contined inside of 'li' tags 
punpro_link_class = "detail-redirection"
# 'ul' tag that contain all the page index
punpro_page_index_class = "pagination"
punpro_page_current_class = "current"
punpro_page_next_class = "next"

### Functions Scope ###
#=======================================================================================================================================

def clattr(__class_name): # this function adapt the class attributes strings for use of the 'find_element()' which does not support spaces

    __response = __class_name.replace(" ",".")
    return __response


def write_log(__message, __log_file=f"{LOGS_DIR}collect.log"): # this write and print info about the runtime status

    with open(__log_file, "a") as log:

        log.write(f"{__message}\n")
        print(__message)


def try_get(__url): # this function try 3 times with different proxies, if none of them works, use the local IP    

    write_log(f" >>> Trying GET method for link {__url} ... ")
    # getting the main list tag of the DOM where lies all the tags that we''re gonna use along the whole script
    # all the 'li' tags constains the 'a' tag that will be stored in a csv formatted file, to scrap later in
    # other separated script.
    __driver = webdriver.Chrome(options=options,
                                service=Service(executable_path=ChromeDriverManager().install()))

    try:

        __driver.get(__url)
        write_log("Got it!")

    except:

        write_log("Site can't be reached, Retrying")

    return __driver



def collect_metrocuadrado(__data):
    # this gather links for scraping from 'metrocuadrado.com'
    
    if (__data == None): raise AttributeError("you haven't passed '__data' argument")

    for facility_item in facility:

        for city_item in cities:
            # setting the url link structure of every website that we're gonna scrap
            mecu_url = "%s/%s/%s/%s/" % (baseurl[0], facility_item, via, city_item)
            # trying connection
            driver = try_get(mecu_url)
            driver.implicitly_wait(2)
            # declaring the variables that we'll use, and the 'data' dictionary that will be returned
            current_page = 0
            a_tags = []
            # gathering data and writing into gather.dat

            while (True):

                # finding list of items
                li_tags = driver.find_elements(By.CLASS_NAME, clattr(mecu_list_class))

                # finding links of items, I mean "href" attributes
                for li in li_tags:

                    item_to_append = li.find_element(By.CLASS_NAME, clattr(mecu_link_class))
                    a_tags.append(item_to_append.get_attribute("href"))

                # writing log for more info about process
                current_page += 1
                info = f" L[{baseurl[0].split('/')[-1]}:page-{current_page}:{facility_item}-{city_item}] a:href links > {len(a_tags)}"
                write_log(info)

                #  getting all the page item links
                try:

                    page_index = driver.find_elements(By.CLASS_NAME, clattr(page_number_box_class))
                    # finding the 'current page' and seek for the 'next page element' to click on
                    for i in range(len(page_index)):

                        if (page_index[i].get_attribute("class") == page_active_class):

                            page_next = page_index[i + 1]
                            break

                    # exiting the loop in case 'page next' were the last page listed
                    if(page_next.get_attribute("class") == "item-icon-next page-item disabled"): break
                    # clicking on the 'next page element', to redirect scraping the next page
                    next_page_element = page_next.find_element(By.TAG_NAME, "a")
                    driver.execute_script("arguments[0].click();", next_page_element)

                except:

                    break

            # closing the browser session
            driver.quit()

            # Appending info to data variable to save in 'gather.dat'
            write_log(f"Appending links for {baseurl[0]} ... ")
            
            for a in a_tags:

                __data['href'].append(a)
                __data['facility'].append(facility_item)
                __data['city'].append(city_item)
                __data['website'].append(baseurl[0]) 
                __data['code'].append(a.split("/")[-1])
    


def collect_fincaraiz(__data):
    
    if (__data == None): raise AttributeError("You haven't passed '__data' argument")

    for facility_item in facility:

        for city_item in cities:

            # declaring the variables that we'll use, and the 'data' dictionary that will be returned
            a_tags = []
            # setting the url structure
            finra_url = "%s/%ss/%s/%s?pagina=1" % (baseurl[1], facility_item, via, city_item)
            # trying the connection
            driver = try_get(finra_url)

            # searching info inside each tag and going through the page list
            while (True):

                # waiting for all the a tags inside divs
                try:

                    WebDriverWait(driver, timeout=5).until(expected_conditions.visibility_of_all_elements_located(
                            (By.CLASS_NAME, clattr(finra_link_class))))

                except:

                    write_log('TimeOut Error 5 seconds elapsed, skipping this page and continue ...')
                    continue

                time.sleep(0.5)
                # checks wheather one page only
                # getting the list of page elements
                page_index = driver.find_elements(By.CLASS_NAME, clattr(finra_page_number_class))
                # multi-page availables case
                current_page : int = int(driver.current_url.split('=')[-1])
                # getting all the 'div' container of 'a' tags to extract href links
                div_tags = driver.find_elements(By.CLASS_NAME, clattr(finra_link_class))

                for div in div_tags:

                    try:

                        item_to_append = div.find_element(By.TAG_NAME, "a").get_attribute("href")

                    except:

                        item_to_append = False   # some 'div' tags has sponsor, so we need skip them

                    if (item_to_append != False): a_tags.append(item_to_append)
                
                info = f" L[{baseurl[1].split('/')[-1]}:page-{current_page}:{facility_item}-{city_item}] a:href links > {len(a_tags)}"
                write_log(info)
    
                #pass the page or quit the loop to the next city iteration
                if (len(page_index) == 0):

                    break

                else:

                    time.sleep(1)
                    page_next = page_index[-1]

                    try:

                        page_end = driver.find_element(By.CLASS_NAME, clattr(finra_page_end_class))
                        aria_label = page_end.get_attribute("aria-label")
                        assert (aria_label == "Go to next page")
                        break

                    except:

                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        driver.execute_script("arguments[0].click();", page_next)
                        continue
                
            # closing the browser session
            driver.quit()

            # Appending info to data variable to save in 'gather.dat'
            write_log(f"Appending links for {baseurl[1]} ... ")
            
            for a in a_tags:

                __data['href'].append(a)
                __data['facility'].append(facility_item)
                __data['city'].append(city_item)
                __data['website'].append(baseurl[1]) 
                __data['code'].append(a.split("/")[-1])



def collect_puntopropiedad(__data):

    if (__data == None): raise AttributeError("You haven't passed '__data' argument")
    
    for facility_item in facility:

        for city_item in cities:

            # setting the url structure
            punpro_url = "%s/%s/%ss/%s" % (baseurl[2], via, facility_item, city_item)
            # trying the connection
            driver = try_get(punpro_url)
            driver.implicitly_wait(2)
            # declaring the variables that we'll use, and the 'data' dictionary that will be returned
            a_tags = []

            # gathering data and writing into gather.dat
            while (True):

                # finding li elements in DOM
                li_tags = driver.find_elements(By.CLASS_NAME, clattr(punpro_list_box_class))

                # finding a tags in li elements
                for li in li_tags:

                    item_to_append = li.find_element(By.CLASS_NAME, clattr(punpro_link_class))
                    a_tags.append(item_to_append.get_attribute("href"))

                # getting the page index
                page_current = ""
                page_next = ""
                page_text = ""

                try:

                    page_box = driver.find_element(By.CLASS_NAME, clattr(punpro_page_index_class))
                    page_index = page_box.find_elements(By.TAG_NAME, "li")

                    for page in page_index:

                        if (page.get_attribute("class") == punpro_page_next_class):

                            page_next = page.find_element(By.TAG_NAME, "span")

                        elif (page.get_attribute("class") == punpro_page_current_class):

                            page_current = page.find_element(By.TAG_NAME, "span")
                            page_text = page_current.text

                except:

                    page_text = "1"
                    write_log("Warning: Just has found only one page ... ")

                # writing log for more info about process
                #info = f" L[{baseurl[2].split('/')[-1]} : page : {page_text} : {city_item}] a:href links got > {len(a_tags)}"
                info = f" L[{baseurl[2].split('/')[-1]}:page-{page_text}:{facility_item}-{city_item}] a:href links > {len(a_tags)}"
                write_log(info)
                
                # click in the next page 
                try:
                    
                    driver.execute_script("arguments[0].click();", page_next)

                except:

                    break
                
            # closing the browser session
            driver.quit()

            # Appending info to data variable to save in 'gather.dat'
            write_log(f"Appending links for {baseurl[2]} ... ")
            
            for a in a_tags:

                __data['href'].append(a)
                __data['facility'].append(facility_item)
                __data['city'].append(city_item)
                __data['website'].append(baseurl[2]) 
                __data['code'].append(a.split("/")[-1])



### Main Function ###
#========================================================================================================================================

if __name__=="__main__":
    
    # updating or creating 'gather.dat' file
    os.system(f"touch {BASE_DIR}/data/collect.dat")
    os.system(f"rm {LOGS_DIR}collect.log || touch {LOGS_DIR}collect.log")
    
    # dictionary where all sources are gonna merge
    data = {'href':[],
            'facility':[],
            'city':[],
            'website':[],
            'code':[]}
    
    # defining the threads
    task1 = Thread(target=collect_metrocuadrado, args=([data]))
    task1.start()
    
    task2 = Thread(target=collect_fincaraiz, args=([data]))
    task2.start()

    task3 = Thread(target=collect_puntopropiedad, args=([data]))
    task3.start()

    task1.join(timeout=float(21800))
    task2.join(timeout=float(21800))
    task3.join(timeout=float(21800))
    
    # Saving to CSV file
    try:

        df = pandas.DataFrame(data=data,
                              index=range(0, len(data['href'])),
                              columns=['facility','city','code','website','href'])

        df.to_csv(f"{BASE_DIR}/data/collect.dat", sep=",", header=True)

    except:

        write_log("[ERROR] Saving links into csv file.")

    else:

        write_log("[OK] All the things went good.")







