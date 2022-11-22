import argparse
import calendar
import json
import os
import platform
import sys
import traceback
import traceback
## Custom Imports for time banning.
import time
import urllib.request
from random import randint, random

import utils
import yaml
from ratelimit import limits
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

# -------------------------------------------------------------
# -------------------------------------------------------------


# Global Variables
opts = Options()
opts.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/71.0"
)

# If you change this variable the scraping process will change
# and not all elements will be scraped.
# Variable is archaic and deprecated
# driver = None
# driver = webdriver.Chrome(options=opts)

# whether to download photos or not
download_uploaded_photos = True
download_friends_photos = False

# whether to download the full image or its thumbnail (small size)
# if small size is True then it will be very quick else if its false then it will open each photo to download it
# and it will take much more time
friends_small_size = False
photos_small_size = False

total_scrolls = 2500
current_scrolls = 0
scroll_time = 9

old_height = 0
facebook_https_prefix = "https://"

## Reducing these values now that a scroll time period has been added to avoid rate limit
# Actually did not change them.

# Values for rate limiting | lower is slower!
# Last worked at: low=10,high=25,time=600
# Failed at: low=3,high=10,time=300
rtqlow = 10
rtqhigh = 25
# You don't really need to change these at all.
rltime = 600
rhtime = 900

# Traversal speed is solely controlled by this variable
# Vales for time sleep in secs
# Last worked at: min=25,max=40
# Failed at: min=20, max=40
tsmin = 15
tsmax = 30


# CHROMEDRIVER_BINARIES_FOLDER = "bin"


# -------------------------------------------------------------
# Identify Image Links
# Important Note! The script scans the profiles and appends the
# links to a list, then downloads them later.
# -------------------------------------------------------------


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def get_facebook_images_url(img_links):
    urls = []

    for link in img_links:
        if link != "None":
            valid_url_found = False
            time.sleep(randint(tsmin, tsmax))
            driver.get(link)

            try:
                while not valid_url_found:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, selectors.get("spotlight"))
                        )
                    )
                    element = driver.find_element_by_class_name(
                        selectors.get("spotlight")
                    )
                    img_url = element.get_attribute("src")

                    if img_url.find(".gif") == -1:
                        valid_url_found = True
                        urls.append(img_url)
            except Exception:
                urls.append("None")
        else:
            urls.append("None")

    return urls


# -------------------------------------------------------------
# Image Downloader
# -------------------------------------------------------------

# takes a url and downloads image from that url
@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def image_downloader(img_links, folder_name):
    img_names = []
    print(folder_name)

    try:
        parent = os.getcwd()
        # try:
        folder = os.path.join(os.getcwd(), folder_name)
        utils.create_folder(folder)
        os.chdir(folder)
        # except Exception:
        #     print("Error in changing directory.")

        for link in img_links:
            img_name = "None"

            if link != "None":
                img_name = (link.split(".jpg")[0]).split("/")[-1] + ".jpg"

                # this is the image id when there's no profile pic
                if img_name == selectors.get("default_image"):
                    img_name = "None"
                else:
                    try:
                        # Requesting images too fast will get you blocked too.
                        time.sleep(randint(tsmin, tsmax))
                        urllib.request.urlretrieve(link, img_name)
                    except Exception:
                        img_name = "None"

            img_names.append(img_name)

        os.chdir(parent)
    except Exception:
        print("Exception (image_downloader):", sys.exc_info()[0])

    return img_names


# -------------------------------------------------------------
# -------------------------------------------------------------


def check_height():
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height


# -------------------------------------------------------------
# Exit immediately after being blocked
# -------------------------------------------------------------


# def block_check(b):
#     blocked = ""
#     try:
#         blocked = b.find_element_by_xpath("//div[@class='mvl ptm uiInterstitial uiInterstitialLarge uiBoxWhite']").text
#     except Exception:
#         pass
#     finally:
#         exit(1)

# -------------------------------------------------------------
# -------------------------------------------------------------

# helper function: used to scroll the page
from selenium.webdriver.common.keys import Keys
from driver_help import WebdriverHelper


def scroll(total_scrolls):
    global old_height
    for current_scrolls in tqdm(range(total_scrolls)):
        try:
            # old_height = driver.execute_script("return document.body.scrollHeight")
            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # WebDriverWait(driver, scroll_time, 0.05).until(
            #     lambda driver: check_height()
            # )
            time.sleep(2)
            WebdriverHelper(driver).send_keys(
                [Keys.ARROW_DOWN] * randint(rtqlow, rtqhigh),
                (0.1, 0.7),
                1)
            time.sleep(2)


            # current_scrolls += 1
        except:
            break
    return


# -------------------------------------------------------------
# -------------------------------------------------------------

# --Helper Functions for Posts


def get_status(x):
    status = ""
    try:
        status = x.find_element_by_xpath(
            ".//div[@class='_5wj-']"
        ).text  # use _1xnd for Pages
    except Exception:
        try:
            status = x.find_element_by_xpath(".//div[@class='userContent']").text
        except Exception:
            pass
    return status


def get_div_links(x, tag):
    try:
        temp = x.find_element_by_xpath(".//div[@class='_3x-2']")
        return temp.find_element_by_tag_name(tag)
    except Exception:
        return ""


def get_title_links(title):
    l = title.find_elements_by_tag_name("a")
    return l[-1].text, l[-1].get_attribute("href")


def get_title(x):
    title = ""
    title = x.find_element_by_xpath(".//div[@data-ft]//p//text() | //div[@data-ft]/div[@class]/div[@class]/text()")
    return title
    # try:
    #     title = x.find_element_by_xpath(".//span[@class='fwb fcg']")
    # except Exception:
    #     try:
    #         title = x.find_element_by_xpath(".//span[@class='fcg']")
    #     except Exception:
    #         try:
    #             title = x.find_element_by_xpath("//div[@data-ft]//p//text() | //div[@data-ft]/div[@class]/div[@class]/text()")
    #         except Exception:
    #             pass
    # finally:
    #     return title


def get_time(x):
    time = ""
    try:
        time = x.find_element_by_tag_name("abbr").get_attribute("title")
        time = (
            str("%02d" % int(time.split(", ")[1].split()[1]),)
            + "-"
            + str(
                (
                    "%02d"
                    % (
                        int(
                            (
                                list(calendar.month_abbr).index(
                                    time.split(", ")[1].split()[0][:3]
                                )
                            )
                        ),
                    )
                )
            )
            + "-"
            + time.split()[3]
            + " "
            + str("%02d" % int(time.split()[5].split(":")[0]))
            + ":"
            + str(time.split()[5].split(":")[1])
        )
    except Exception:
        pass

    finally:
        return time

import urllib.parse as urlparse
from urllib.parse import parse_qs
import numpy as np
import dateparser

def parse_date3(date_str):
    if type(date_str) == list:
        date_str = date_str[0]
    date_parse = dateparser.parse(date_str)
    if not date_parse:
        return None
    return date_parse

# Deals with scraping posts
# @limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def extract_and_write_posts(elements, filename):
    # try:
    f = open(filename, "w", newline="\r\n")
    f.writelines(
        " TIME || TYPE  || TITLE || STATUS  ||   LINKS(Shared Posts/Shared Links etc) "
        + "\n"
        + "\n"
    )
    list_href = []
    for x in tqdm(elements):
        # try:
        title = " "
        status = " "
        link = ""
        time = " "
        # test_text = x.get_attribute('innerHTML')
        # with open('test.txt', "w") as f:
        #     f.write(str(test_text))
        # print(x.find_elements_by_xpath("//a[@href]"))
        # try:
        #     element = x.find_element_by_xpath(".//a[contains(@href,'story_fbid') and contains(@href,'&id=')]")
        #     url_link = element.get_attribute("href")
        # except NoSuchElementException:
        #     url_link = None
        # if url_link:
        #     parsed = urlparse.urlparse(url_link)
        #     story_fbid = parse_qs(parsed.query)['story_fbid'][0]
        #     try:
        #         date_string = x.find_element_by_xpath(".//abbr")
        #     except NoSuchElementException:
        #         date_string = None
        #     if date_string:
        #         date_string = date_string.text
        #         date_obj = parse_date3(date_string)
        #     else:
        #         date_obj = None
        #     list_href.append({
        #         "post_id": story_fbid,
        #         "date": date_obj,
        #         "url": url_link,
        #     })

        try:
            element = x.find_element_by_xpath(".//a[contains(@href,'permalink/')]")
            url_link = element.get_attribute("href")
        except NoSuchElementException:
            url_link = None
        
        if url_link:
            story_fbid = url_link.split("permalink/")[-1].split("/")[0]
            try:
                date_string = x.find_element_by_xpath(".//abbr")
            except NoSuchElementException:
                date_string = None
            if date_string:
                date_string = date_string.text
                date_obj = parse_date3(date_string)
            else:
                date_obj = None
            list_href.append({
                "post_id": story_fbid,
                "date": date_obj,
                "url": url_link,
            })
        print(list_href[:10])
        # parsed = urlparse.urlparse(url_link)
        # story_fbid_list = parse_qs(parsed.query)['story_fbid']
        # post_id_list = parse_qs(parsed.query)['id']
        # if story_fbid_list and post_id_list:
        #     story_fbid = story_fbid_list[0]
        #     post_id = post_id_list[0]
        # for i in x.find_elements_by_xpath("//a[@href]"):
        #     url_link = i.get_attribute("href")
        #     # print(url_link)
        #     if "story_fbid" in url_link and "id" in url_link:
        #         parsed = urlparse.urlparse(url_link)
        #         story_fbid_list = parse_qs(parsed.query)['story_fbid']
        #         post_id_list = parse_qs(parsed.query)['id']
        #         if story_fbid_list and post_id_list:
        #             story_fbid = story_fbid_list[0]
        #             post_id = post_id_list[0]
                
        #             if f"{story_fbid}_{post_id}" not in list_href:
        #             #     break
        #             # else:
        #                 list_href.append(f"{story_fbid}_{post_id}")
        # print(list_href)
        np.save(filename.replace("txt", "npy"), list_href)
        # list_href.append(x.find_element_by_xpath(".//a[contains(@href,'footer')]/@href"))
        # time
        # time = utils.get_time(x)

        # # title
        # title = utils.get_title(x, selectors)
        # print(title)
        # # if not title:
        # if title.text.find("shared a memory") != -1:
        #     x = x.find_element_by_xpath(selectors.get("title_element"))
        #     title = utils.get_title(x, selectors)

        # status = utils.get_status(x, selectors)
        # if (
        #     title.text
        #     == driver.find_element_by_id(selectors.get("title_text")).text
        # ):
        #     if status == "":
        #         temp = utils.get_div_links(x, "img", selectors)
        #         if (
        #             temp == ""
        #         ):  # no image tag which means . it is not a life event
        #             link = utils.get_div_links(x, "a", selectors).get_attribute(
        #                 "href"
        #             )
        #             type = "status update without text"
        #         else:
        #             type = "life event"
        #             link = utils.get_div_links(x, "a", selectors).get_attribute(
        #                 "href"
        #             )
        #             status = utils.get_div_links(x, "a", selectors).text
        #     else:
        #         type = "status update"
        #         if utils.get_div_links(x, "a", selectors) != "":
        #             link = utils.get_div_links(x, "a", selectors).get_attribute(
        #                 "href"
        #             )

        # elif title.text.find(" shared ") != -1:

        #     x1, link = utils.get_title_links(title)
        #     type = "shared " + x1

        # elif title.text.find(" at ") != -1 or title.text.find(" in ") != -1:
        #     if title.text.find(" at ") != -1:
        #         x1, link = utils.get_title_links(title)
        #         type = "check in"
        #     elif title.text.find(" in ") != 1:
        #         status = utils.get_div_links(x, "a", selectors).text

        # elif (
        #     title.text.find(" added ") != -1 and title.text.find("photo") != -1
        # ):
        #     type = "added photo"
        #     link = utils.get_div_links(x, "a", selectors).get_attribute("href")

        # elif (
        #     title.text.find(" added ") != -1 and title.text.find("video") != -1
        # ):
        #     type = "added video"
        #     link = utils.get_div_links(x, "a", selectors).get_attribute("href")

        # else:
        #     type = "others"

        # if not isinstance(title, str):
        #     title = title.text

        # status = status.replace("\n", " ")
        # title = title.replace("\n", " ")

        # line = (
        #     str(time)
        #     + " || "
        #     + str(type)
        #     + " || "
        #     + str(title)
        #     + " || "
        #     + str(status)
        #     + " || "
        #     + str(link)
        #     + "\n"
        # )

        # try:
        #     f.writelines(line)
        # except Exception:
        #     print("Posts: Could not map encoded characters")
        # # except Exception:
        # #     traceback.print_exe()
        # #     break
    f.close()
    # except Exception:
    #     print("Exception (extract_and_write_posts)", "Status =", sys.exc_info()[0])

    return


# -------------------------------------------------------------
# -------------------------------------------------------------


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def save_to_file(name, elements, status, current_section):
    """helper function used to save links to files"""

    # status 0 = dealing with friends list
    # status 1 = dealing with photos
    # status 2 = dealing with videos
    # status 3 = dealing with about section
    # status 4 = dealing with posts

    # try:
    f = None  # file pointer

    if status != 4:
        f = open(name, "w", encoding="utf-8", newline="\r\n")

    results = []
    img_names = []

    # dealing with Friends
    if status == 0:
        # get profile links of friends
        results = [x.get_attribute("href") for x in elements]
        results = [create_original_link(x) for x in results]

        # get names of friends
        people_names = [
            x.find_element_by_tag_name("img").get_attribute("aria-label")
            for x in elements
        ]

        # download friends' photos
        try:
            if download_friends_photos:
                if friends_small_size:
                    img_links = [
                        x.find_element_by_css_selector("img").get_attribute("src")
                        for x in elements
                    ]
                else:
                    links = []
                    for friend in results:
                        try:
                            time.sleep(randint(tsmin, tsmax))
                            driver.get(friend)
                            WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located(
                                    (
                                        By.CLASS_NAME,
                                        selectors.get("profilePicThumb"),
                                    )
                                )
                            )
                            l = driver.find_element_by_class_name(
                                selectors.get("profilePicThumb")
                            ).get_attribute("href")
                        except Exception:
                            l = "None"

                        links.append(l)

                    for i, _ in enumerate(links):
                        if links[i] is None:
                            links[i] = "None"
                        elif links[i].find("picture/view") != -1:
                            links[i] = "None"

                    img_links = get_facebook_images_url(links)

                folder_names = [
                    "Friend's Photos",
                    "Mutual Friends' Photos",
                    "Following's Photos",
                    "Follower's Photos",
                    "Work Friends Photos",
                    "College Friends Photos",
                    "Current City Friends Photos",
                    "Hometown Friends Photos",
                ]
                print("Downloading " + folder_names[current_section])

                img_names = image_downloader(
                    img_links, folder_names[current_section]
                )
            else:
                img_names = ["None"] * len(results)
        except Exception:
            print(
                "Exception (Images)",
                str(status),
                "Status =",
                current_section,
                sys.exc_info()[0],
            )

    # dealing with Photos
    elif status == 1:
        results = [x.get_attribute("href") for x in elements]
        results.pop(0)

        try:
            if download_uploaded_photos:
                if photos_small_size:
                    background_img_links = driver.find_elements_by_xpath(
                        selectors.get("background_img_links")
                    )
                    background_img_links = [
                        x.get_attribute("style") for x in background_img_links
                    ]
                    background_img_links = [
                        ((x.split("(")[1]).split(")")[0]).strip('"')
                        for x in background_img_links
                    ]
                else:
                    background_img_links = get_facebook_images_url(results)

                folder_names = ["Uploaded Photos", "Tagged Photos"]
                print("Downloading " + folder_names[current_section])

                img_names = image_downloader(
                    background_img_links, folder_names[current_section]
                )
            else:
                img_names = ["None"] * len(results)
        except Exception:
            print(
                "Exception (Images)",
                str(status),
                "Status =",
                current_section,
                sys.exc_info()[0],
            )

    # dealing with Videos
    elif status == 2:
        results = elements[0].find_elements_by_css_selector("li")
        results = [
            x.find_element_by_css_selector("a").get_attribute("href")
            for x in results
        ]

        try:
            if results[0][0] == "/":
                results = [r.pop(0) for r in results]
                results = [(selectors.get("fb_link") + x) for x in results]
        except Exception:
            pass

    # dealing with About Section
    elif status == 3:
        results = elements[0].text
        f.writelines(results)

    # dealing with Posts
    elif status == 4:
        extract_and_write_posts(elements, name)
        return

    """Write results to file"""
    if status == 0:
        for i, _ in enumerate(results):
            # friend's profile link
            f.writelines(results[i])
            f.write(",")

            # friend's name
            f.writelines(people_names[i])
            f.write(",")

            # friend's downloaded picture id
            f.writelines(img_names[i])
            f.write("\n")

    elif status == 1:
        for i, _ in enumerate(results):
            # image's link
            f.writelines(results[i])
            f.write(",")

            # downloaded picture id
            f.writelines(img_names[i])
            f.write("\n")

    elif status == 2:
        for x in results:
            f.writelines(x + "\n")

    f.close()

    # except Exception:
    #     traceback.print_exe()
        # print("Exception (save_to_file)", "Status =", str(status), sys.exc_info()[0])

    return


# ----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def scrape_data(user_id, scan_list, section, elements_path, save_status, file_names):
    """Given some parameters, this function can scrap friends/photos/videos/about/posts(statuses) of a profile"""
    page = []

    if save_status == 4:
        page.append(user_id)
    # print(save_status)

    page += [user_id + s for s in section]

    for i, _ in enumerate(scan_list):
        # try:
        time.sleep(randint(tsmin, tsmax))
        driver.get(page[i])

        if (
            (save_status == 0) or (save_status == 1) or (save_status == 2)
        ):  # Only run this for friends, photos and videos

            # the bar which contains all the sections
            sections_bar = driver.find_element_by_xpath(
                selectors.get("sections_bar")
            )

            if sections_bar.text.find(scan_list[i]) == -1:
                continue

        if save_status != 3:
            scroll(total_scrolls)

        data = driver.find_elements_by_xpath(elements_path[i])

        save_to_file(file_names[i], data, save_status, i)

        # except Exception:
        #     traceback.print_exe()
        #     print(
        #         "Exception (scrape_data)",
        #         str(i),
        #         "Status =",
        #         str(save_status),
        #         sys.exc_info()[0],
        #     )


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


def create_original_link(url):
    if url.find(".php") != -1:
        original_link = (
            facebook_https_prefix + facebook_link_body + ((url.split("="))[1])
        )

        if original_link.find("&") != -1:
            original_link = original_link.split("&")[0]

    elif url.find("fnr_t") != -1:
        original_link = (
            facebook_https_prefix
            + facebook_link_body
            + ((url.split("/"))[-1].split("?")[0])
        )
    elif url.find("_tab") != -1:
        original_link = (
            facebook_https_prefix
            + facebook_link_body
            + (url.split("?")[0]).split("/")[-1]
        )
    else:
        original_link = url

    return original_link


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def create_folder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def scrap_profile(ids):
    folder = os.path.join(os.getcwd(), "data")
    utils.create_folder(folder)
    os.chdir(folder)

    # execute for all profiles given in input.txt file
    for user_id in ids:

        time.sleep(randint(tsmin, tsmax))
        # block_check()
        driver.get(user_id)
        url = driver.current_url
        user_id = create_original_link(url)

        print("\nScraping:", user_id)

        try:
            if "groups/" not in user_id:
                target_dir = os.path.join(folder, user_id.split("/")[-1].split("=")[-1])
            else:
                target_dir = os.path.join(folder, user_id.split("groups/")[-1].strip("/"))
            utils.create_folder(target_dir)
            os.chdir(target_dir)
        except Exception:
            print("Some error occurred in creating the profile directory.")
            continue

        # to_scrap = ["Friends", "Photos", "Videos", "About", "Posts"]
        to_scrap = ["Posts"]
        for item in to_scrap:
            print("----------------------------------------")
            print("Scraping {}..".format(item))

            if item == "Posts":
                scan_list = [None]
            elif item == "About":
                scan_list = [None] * 7
            else:
                scan_list = params[item]["scan_list"]

            section = params[item]["section"]
            elements_path = params[item]["elements_path"]
            file_names = params[item]["file_names"]
            save_status = params[item]["save_status"]

            scrape_data(
                user_id, scan_list, section, elements_path, save_status, file_names
            )

            print("{} Done!".format(item))

    print("\nProcess Completed.")
    os.chdir("../..")

    return


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


def safe_find_element_by_id(driver, elem_id):
    try:
        return driver.find_element_by_id(elem_id)
    except NoSuchElementException:
        return None
def init_driver():
    global driver

    options = Options()

    #  Code to disable notifications pop up of Chrome Browser
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--mute-audio")
    # options.add_argument("headless")

    try:
        platform_ = platform.system().lower()
        driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install(), options=options
        )

    except Exception:
        print(
            "Kindly replace the Chrome Web Driver with the latest one from "
            "http://chromedriver.chromium.org/downloads "
            "and also make sure you have the latest Chrome Browser version."
            "\nYour OS: {}".format(platform_)
        )
        exit(1)

    fb_path = facebook_https_prefix + facebook_link_body
    driver.get(fb_path)
    driver.maximize_window()

def login(email, password):
    """ Logging into our own profile """

    try:
        
        # filling the form
        driver.find_element_by_name("email").send_keys(email)
        driver.find_element_by_name("pass").send_keys(password)

        try:
            # clicking on login button
            driver.find_element_by_id("loginbutton").click()
        except NoSuchElementException:
            # Facebook new design
            driver.find_element_by_name("login").click()

        # if your account uses multi factor authentication
        time.sleep(2)
        mfa_code_input = safe_find_element_by_id(driver, "approvals_code")

        if mfa_code_input is None:
            return

        mfa_code_input.send_keys(input("Enter MFA code: "))
        driver.find_element_by_id("checkpointSubmitButton").click()

        # there are so many screens asking you to verify things. Just skip them all
        while safe_find_element_by_id(driver, "checkpointSubmitButton") is not None:
            dont_save_browser_radio = safe_find_element_by_id(driver, "u_0_3")
            if dont_save_browser_radio is not None:
                dont_save_browser_radio.click()

            driver.find_element_by_id("checkpointSubmitButton").click()

    except Exception:
        print("There's some error in log in.")
        print(sys.exc_info()[0])
        exit(1)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def scraper(**kwargs):
    with open("credentials.yaml", "r") as ymlfile:
        cfg = yaml.safe_load(stream=ymlfile)

    if ("password" not in cfg) or ("email" not in cfg):
        print("Your email or password is missing. Kindly write them in credentials.txt")
        exit(1)

    ids = [
        facebook_https_prefix + facebook_link_body + line.split("facebook.com/")[-1]
        for line in open("input.txt", newline="\n")
    ]

    if len(ids) > 0:
        print("\nStarting Scraping...")
        init_driver()
        login(cfg["email"], cfg["password"])
        scrap_profile(ids)
        driver.close()
    else:
        print("Input file is empty.")


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    # PLS CHECK IF HELP CAN BE BETTER / LESS AMBIGUOUS
    ap.add_argument(
        "-dup",
        "--uploaded_photos",
        help="download users' uploaded photos?",
        default=True,
    )
    ap.add_argument(
        "-dfp", "--friends_photos", help="download users' photos?", default=True
    )
    ap.add_argument(
        "-fss",
        "--friends_small_size",
        help="Download friends pictures in small size?",
        default=True,
    )
    ap.add_argument(
        "-pss",
        "--photos_small_size",
        help="Download photos in small size?",
        default=True,
    )
    ap.add_argument(
        "-ts",
        "--total_scrolls",
        help="How many times should I scroll down?",
        default=5,
    )
    ap.add_argument(
        "-st", "--scroll_time", help="How much time should I take to scroll?", default=8
    )

    args = vars(ap.parse_args())
    print(args)

    # ---------------------------------------------------------
    # Global Variables
    # ---------------------------------------------------------

    # whether to download photos or not
    download_uploaded_photos = utils.to_bool(args["uploaded_photos"])
    download_friends_photos = utils.to_bool(args["friends_photos"])

    # whether to download the full image or its thumbnail (small size)
    # if small size is True then it will be very quick else if its false then it will open each photo to download it
    # and it will take much more time
    friends_small_size = utils.to_bool(args["friends_small_size"])
    photos_small_size = utils.to_bool(args["photos_small_size"])

    total_scrolls = int(args["total_scrolls"])
    scroll_time = int(args["scroll_time"])

    current_scrolls = 0
    old_height = 0

    # driver = None
    # CHROMEDRIVER_BINARIES_FOLDER = "bin"

    with open("selectors.json") as a, open("params.json") as b:
        selectors = json.load(a)
        params = json.load(b)

    firefox_profile_path = selectors.get("firefox_profile_path")
    facebook_https_prefix = selectors.get("facebook_https_prefix")
    facebook_link_body = selectors.get("facebook_link_body")

    # get things rolling
    scraper()
