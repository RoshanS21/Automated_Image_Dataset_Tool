import os
import io
import time
import hashlib
import requests
import pandas as pd
from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver

def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    # build the google query
    octopus = "https://www.google.com/search?q=octopus&tbm=isch&ved=2ahUKEwi3vo-xj7vtAhXE_KwKHaIMDtUQ2-cCegQIABAA&oq=octopus&gs_lcp=CgNpbWcQAzIECCMQJzIECCMQJzIECAAQQzIFCAAQsQMyBwgAELEDEEMyBwgAELEDEEMyBAgAEEMyBAgAEEMyBwgAELEDEEMyBAgAEENQ9X9YkIUBYIKIAWgAcAB4AIABWogBkQGSAQEymAEAoAEBqgELZ3dzLXdpei1pbWfAAQE&sclient=img&ei=OrvNX7e5KMT5swWimbioDQ&bih=978&biw=960"
    starfish = "https://www.google.com/search?q=starfish+photography&tbm=isch&ved=2ahUKEwi21-iFyrztAhWFJ6wKHXrbCsQQ2-cCegQIABAA&oq=starfish+photography&gs_lcp=CgNpbWcQAzICCAAyBggAEAUQHjIGCAAQBRAeMgYIABAFEB4yBggAEAgQHjIECAAQGDoECCMQJzoFCAAQsQNQwRJYuydghSloAHAAeACAAU2IAaoGkgECMTOYAQCgAQGqAQtnd3Mtd2l6LWltZ8ABAQ&sclient=img&ei=9X7OX_aIEYXPsAX6tqugDA&bih=978&biw=960"
    donuts = "https://www.google.com/search?q=donuts&tbm=isch&ved=2ahUKEwihnajekbvtAhVMja0KHSGiAQAQ2-cCegQIABAA&oq=donuts&gs_lcp=CgNpbWcQAzIECCMQJzIECCMQJzICCAAyBQgAELEDMgIIADICCAAyAggAMgIIADICCAAyAggAOgQIABAeUN0NWIIbYKIgaABwAHgAgAFSiAHLA5IBATiYAQCgAQGqAQtnd3Mtd2l6LWltZ8ABAQ&sclient=img&ei=sr3NX6H8EsyatgWhxAY&bih=978&biw=960"
    dog = "https://www.google.com/search?q=dog&sxsrf=ALeKk02JLX80UdJuenQBzVwhZUeGrDp_NA:1607394480643&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiLhaGIq73tAhUCi6wKHfM8BiUQ_AUoAXoECC0QAw&biw=1536&bih=763&dpr=2.5"
    cat = "https://www.google.com/search?q=cat&tbm=isch&ved=2ahUKEwinz8aJq73tAhWQSawKHfqkDucQ2-cCegQIABAA&oq=cat&gs_lcp=CgNpbWcQAzIECCMQJzIECCMQJzIHCAAQsQMQQzIECAAQQzIECAAQQzIECAAQQzIECAAQQzIHCAAQsQMQQzIECAAQQzIHCAAQsQMQQ1CsX1ibYWDvYmgAcAB4AIABigGIAeICkgEDMS4ymAEAoAEBqgELZ3dzLXdpei1pbWfAAQE&sclient=img&ei=s-TOX-epFZCTsQX6ybq4Dg&bih=763&biw=1536"
    horse = "https://www.google.com/search?q=horse&sxsrf=ALeKk008HVfG_gNiB7N7Wer588-honTZtQ:1607796396656&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiQ3d-ohMntAhUPna0KHRhnA2EQ_AUoAXoECBIQAw&biw=1536&bih=763"
    tomato = "https://www.google.com/search?q=tomato+leaves&sxsrf=ALeKk00vf98Tcz2KoaoOCw0O9HgjNiPcLg:1607797123450&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiww6eDh8ntAhUMbKwKHax4A_8Q_AUoAXoECBoQAw&biw=1536&bih=763"
    christmasTree = "https://www.google.com/search?q=christmas+tree&tbm=isch&hl=en&chips=q:christmas+tree,g_1:decorated:ZZjyhDQ5A3I%3D&sa=X&ved=2ahUKEwiSqtKbq8ntAhXBRawKHbSpAmwQ4lYoAXoECAEQGw&biw=1903&bih=922"
    waterBottle = "https://www.google.com/search?q=plastic+water+bottles&tbm=isch&chips=q:plastic+water+bottles,g_1:empty:-nsNL-_ORx4%3D&hl=en&sa=X&ved=2ahUKEwi_9Mnci8ntAhUQRawKHTYLA08Q4lYoAXoECAEQGw&biw=1519&bih=763"
    search_url = christmasTree
    
    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls

def persist_image(folder_path:str,url:str):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")

def search_and_download(search_term:str,driver_path:str,target_path='./images',number_images=110):
    target_folder = os.path.join(target_path,'_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=driver_path) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5)
        
    for elem in res:
        persist_image(target_folder,elem)

search_term = 'christmasTree'
driver_path = (r"C:\Users\rosha\Desktop\proj05\chromedriver.exe")
target_path = '/images'
search_and_download(search_term=search_term,driver_path=driver_path)