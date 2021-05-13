from selenium import webdriver # Selenium is an open-source web-based automation tool
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import time
from PIL import Image
from io import BytesIO

number = input('What pk? ')
token = '29d709ead46b76e50b486ac5f8db78ebc35e66ea'
screenshot_dir = str(Path(__file__).resolve().parent) # 'C:/Users/jbhol/Desktop'
full_screenshot_dir = screenshot_dir + "/static/images/problems/" + str(number) + "_statement.png"

base_dir = 'http://www.daily.mathpreppro.com'
# base_dir = 'http://127.0.0.1:8000'
url = "".join([base_dir,'/prolist/',token,'/',number,'/']) # Option 1 to grab Admin prolist detail
# url = "".join(['http://',get_current_site(self.request).domain,self.object.get_absolute_url()]) # This interestingly returns domain/list/1/
# url = self.request.build_absolute_uri() # Option 2

def screenshot():
    options = Options()
    # options.headless = True
    with webdriver.Chrome(chrome_options=options) as driver:
        # driver.maximize_window()
        driver.get(url)
        driver.implicitly_wait(3)
        time.sleep(2)
        element = driver.find_element_by_id('screenshot') # Methods to find web elements: https://chercher.tech/python/webelement-locator
        element.screenshot(full_screenshot_dir) # This will replace an image if one already exists with that name

if __name__ == '__main__':
    screenshot()

#################################### NOTES #####################################
###                                                                          ###
### In order to take screenshots of tall problems, you must rotate the       ###
### screen to portrate mode...                                               ###
###                                                                          ###
################################################################################
