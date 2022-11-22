import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from urllib.parse import urlparse



class WebdriverHelper(object):
    BROWSER_NAME_CHROME = 'Chrome'
    BROWSER_NAME_FIREFOX = 'Firefox'

    def __init__(self, driver=None):
        self.driver = driver
        pass

    def create(self, browser_name, headless=False, url='', load_timeout=60, user_agent=None):
        if browser_name == self.BROWSER_NAME_CHROME:
            chromeOptions = webdriver.ChromeOptions()
            if headless:
                chromeOptions.headless = True
                chromeOptions.add_argument('--no-sandbox')
            if user_agent:
                chromeOptions.add_argument(f"user-agent={user_agent}")
            driver = webdriver.Chrome(options=chromeOptions)
            driver.get(url)
            driver.set_page_load_timeout(load_timeout)
            return driver

        elif browser_name == self.BROWSER_NAME_FIREFOX:
            firefoxOptions = webdriver.FirefoxOptions()
            profile = webdriver.FirefoxProfile()
            if headless:
                firefoxOptions.headless = True
            if user_agent:
                profile.set_preference('general.useragent.override', user_agent)
            driver = webdriver.Firefox(options=firefoxOptions)
            driver.get(url)
            driver.set_page_load_timeout(load_timeout)
            return driver

    def send_keys(self, keys, delay=(), sleep=0):
        actions = ActionChains(self.driver)

        # Delay between keys
        if len(delay) == 2:
            delay_time = random.uniform(delay[0], delay[1])
            for key in keys:
                actions.send_keys(key)
                actions.perform()
                time.sleep(delay_time)
        else:
            actions.send_keys(keys)
            actions.perform()

        # Delay after all keys sent
        if sleep != 0:
            time.sleep(sleep)

    def click(self, element, xoffset=None, yoffset=None):
        actions = ActionChains(self.driver)
        if (xoffset is not None) and (yoffset is not None):
            actions.move_to_element_with_offset(element, xoffset, yoffset)
        else:
            actions.move_to_element(element)
        actions.click()
        actions.perform()
