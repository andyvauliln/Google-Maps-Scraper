from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementNotInteractableException
from dash import html
from parsel import Selector
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import re
import time
import json
import sys
from selenium.common.exceptions import StaleElementReferenceException
import traceback
from multiprocessing import Pool
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from concurrent.futures.thread import ThreadPoolExecutor
import selenium_async
import asyncio

executor = ThreadPoolExecutor(10)


def initialize_driver():
    chrome_options = Options()
    # Run in headless mode. Comment this line if you want to see the browser actions
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the Chrome driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    return driver


driver = initialize_driver()


def scrollDownLeftMenuOnGoogleMaps(waitingTime):
    try:
        menu_xpath = '/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div[1]/div[1]/div[1]'
        WebDriverWait(driver, waitingTime).until(
            EC.visibility_of_element_located((By.XPATH, menu_xpath)))
        element = driver.find_element("xpath", menu_xpath)
        driver.execute_script("arguments[0].scrollIntoView();", element)
    except TimeoutException:
        print("Timeout for scrollDownLeftMenuOnGoogleMaps")


def getPhone(htmlCode):
    phone = ""
    phoneEl = htmlCode.xpath(
        '//button[contains(@data-tooltip, "Copy phone number")]')
    if phoneEl and len(phoneEl) > 0:
        phoneStr = phoneEl[0].xpath('@data-item-id').extract_first('')
        if phoneStr:
            numbers = ''.join(c for c in phoneStr if c.isdigit())
            if numbers.startswith('0'):
                numbers = '+62' + numbers[1:]
            phone = numbers
    return phone


def getPrice(htmlCode):
    price = 0
    element = htmlCode.xpath('//button[@aria-haspopup="dialog" and @class="Tc0rEd fT414d plVN2c "]')
    if element and len(element) > 0:
        aria_label = element[0].attrib.get('aria-label', '')
        price_match = re.search(r'IDR\s+([\d,]+)', aria_label)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            try:
                price = int(price_str)
                return price
            except ValueError:
                return 0
    return price


def getCheckout(htmlCode):
    result = ""
    element = htmlCode.xpath(
        '//div[contains(@data-item-id, "place-info-links:")]')
    if element and len(element) > 0:
        str = element[0].xpath('.//div[2]/div[1]/span/text()')
        result = str.get()
    return result


def getMenu(htmlCode):
    result = ""
    element = htmlCode.xpath(
        '//a[contains(@data-tooltip, "Open menu link")]')
    if element and len(element) > 0:
        valueStr = element[0].xpath('@href').extract_first('')
        result = valueStr
    return result


def extract_price(price_str):
    non_decimal = ''.join(ch for ch in price_str if ch.isdigit())
    try:
        return int(non_decimal)
    except ValueError:
        return 0


def getAboutData():
    price = 0
    star_rating = ""
    all_text = ""

    try:
        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[.//div[contains(text(), "About")]]')))
        if element:
            element.click()
            price_element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="s35xed"]//li[@class="OyY9Kc"]/span')))
            if price_element:
                price = extract_price(price_element.text)
            star_rating_element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(
                (By.XPATH, '//div[@class="s35xed"]//li[@class="OyY9Kc" and contains(., "star hotel")]/span')))
            if star_rating_element:
                star_rating = star_rating_element.text or ""
            text_elements = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
                (By.XPATH, '//div[@class="HeZRrf"]//div[@class="P1LL5e"]')))
            if text_elements:
                all_text = ' '.join([element.text for element in text_elements])
    except TimeoutException:
        print("Timeout for ABOUT Page")
        return (price, star_rating, all_text)
    except Exception as e:
        print("***********************ERROR*************************")
        print("Error about data", e)
        return (price, star_rating, all_text)
        # traceback.print_exc()

    return (price, star_rating, all_text)


def getBookingLink(htmlCode):
    result = ""
    element = htmlCode.xpath(
        '//a[contains(@data-tooltip, "Open booking link")]')
    if element and len(element) > 0:
        valueStr = element[0].xpath('@href').extract_first('')
        result = valueStr
    return result


def getAddress(htmlCode):
    result = ""
    element = htmlCode.xpath(
        '//button[contains(@data-tooltip, "Copy address")]')
    if element and len(element) > 0:
        valueStr = element[0].attrib.get('aria-label', '')
        result = valueStr
    return result


def getCategory(htmlCode):
    result = ""
    element = htmlCode.xpath(
        '//button[contains(@jsaction, "pane.rating.category")]')
    if element and len(element) > 0:
        valueStr = element[0].xpath('string()').get()
        result = valueStr
    return result


def getPhotos():
    result = []

    try:
        element = driver.find_element("xpath",
                                      "//button[contains(@aria-label, 'All')]")
        driver.execute_script("arguments[0].scrollIntoView();", element)
        driver.execute_script("arguments[0].click();", element)
        backButton = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(
            (By.XPATH, "//button[contains(@data-tooltip, 'Back')]")))

        imgElements = driver.find_elements(
            "xpath", "//a[starts-with(@data-photo-index, '')]/div[@role='img']")
        numberOfElements = len(imgElements)
        for i in range(numberOfElements):
            imgEl = driver.find_element("xpath",
                                        "//a[@data-photo-index='" + str(i) + "']/div[@role='img']")

            driver.execute_script("arguments[0].scrollIntoView();", imgEl)
            WebDriverWait(driver, 5).until(
                lambda driver: 'https' in imgEl.get_attribute('style'))
            style = imgEl.get_attribute('style')

            url = style.split('"')[1]
            result.append(url)

        driver.execute_script("arguments[0].click();", backButton)
    except TimeoutException:
        print("Timeout for getPhotos")
    except Exception as e:
        print("***********************ERROR*************************")
        print("Error getPhotos:")
    return result


def getReviews():
    result = {"this_year": [], "previous_years": []}
    num_comments = 20
    try:
        scrollDownLeftMenuOnGoogleMaps(5)

        element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(
            (By.XPATH, "//button[contains(@jsaction, 'pane.reviewChart.moreReviews')]")))
        if element:
            driver.execute_script("arguments[0].click();", element)
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@jsaction, 'mouseover:pane.review.in; mouseout:pane.review.out')]")))
            last_index_processed = 0
            added_elements = 0
            target_string = ""
            while added_elements < num_comments:
                try:
                    target_string += str(added_elements)
                    target_string = target_string[-5:]
                    samecounts = target_string.count(str(added_elements))
                    if samecounts >= 2:
                        break

                    commentElements = driver.find_elements(
                        By.XPATH,
                        "//div[contains(@jsaction, 'mouseover:pane.review.in; mouseout:pane.review.out')]/div[1]/div[4]")
                    for element in commentElements[last_index_processed:]:
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        last_index_processed += 1
                        if element not in result["this_year"] and element not in result["previous_years"]:
                            span_elements = element.find_elements(By.XPATH, './div[2]/div[1]/span')
                            if len(span_elements) == 2:
                                try:
                                    span_elements[1].click()
                                except ElementNotInteractableException:
                                    driver.execute_script("arguments[0].click();", span_elements[1])
                            if span_elements and len(span_elements) > 0:
                                text = span_elements[0].text
                                date_element = element.find_element(By.XPATH, './div[1]/span[2]')
                                date_str = date_element.text
                                if "year" in date_str:
                                    result["previous_years"].append(text)
                                else:
                                    result["this_year"].append(text)
                                added_elements += 1
                    time.sleep(2)
                except StaleElementReferenceException:
                    print("Encountered StaleElementReferenceException in getReviews, retrying...")
                    continue
    except TimeoutException:
        print("Timeout for getReviews")
    except Exception as e:
        print("***********************ERROR*************************")
        print("Error getReviews:", e)
    return result


def getHours(htmlCode, page_content):
    result = []
    try:
        element = htmlCode.xpath(
            '//img[contains(@aria-label, "Hours")]/../../div[2]')
        if element and len(element) > 0:
            valueStr = element[0].xpath('@aria-label').extract_first('')
            if valueStr:
                weekdays = ['Monday', 'Tuesday', 'Wednesday',
                            'Thursday', 'Friday', 'Saturday', 'Sunday']
                lines = valueStr.split(';')

                for line in lines:
                    # Split the line into day and times
                    parts = line.split(',')
                    if len(parts) < 2:
                        continue
                    # Extract day and remove additional info in parentheses
                    day = parts[0].strip()
                    day = day.split(' ')[0]  # New line to handle "Thursday (Pancasila Day)" case
                    times = parts[1].strip()
                    # Split the times into open time and close time
                    if "to" in times:
                        times = times.split(' to ')
                        if len(times) < 2:
                            continue
                        open_time = re.sub(r'[^a-zA-Z0-9 ]', ' ', times[0].strip())
                        close_time = re.sub(
                            r'[^a-zA-Z0-9 ]', ' ', times[1].strip())
                        # Create a dictionary and add it to the list
                        result.append({'day': day, 'open_time': open_time,
                                       'close_time': close_time})
                    if "24" in times:
                        result.append({'day': day, 'open_time': "12:00 AM",
                                       'close_time': "11:59 PM"})

                # Sort the list by day of the week
                result.sort(key=lambda x: weekdays.index(x['day']))

        if not element and "Temporarily closed" in page_content:
            result = []
    except Exception as e:
        print("***********************ERROR*************************")
        print("Error get hours:", e)
        return []
    return result


def getWebsite(htmlCode):
    result = ""
    element = htmlCode.xpath(
        '//a[contains(@data-tooltip, "Open website")]')
    if element and len(element) > 0:
        valueStr = element[0].xpath('@href').extract_first('')
        result = valueStr
    return result


def getPlaceInfo(id):
    # url = "https://www.google.com/maps/place/?hl=en&q=place_id:ChIJj3JXUTtD0i0RzUQZaHJndOs"
    try:
        url = "https://www.google.com/maps/place/?hl=en&q=place_id:" + id
        # print(url)
        driver.get(url)
        page_content = driver.page_source
        response = Selector(page_content)
        # print("- GETTING PHONE")
        phone = getPhone(response)

        # print("- GET PRICE")
        price = getPrice(response)

        # print("- GETTING CATEGORY")
        category = getCategory(response)

        # print("- GETTING MENU")
        menu = getMenu(response)

        # print("- GETTING HOURS")
        hours = getHours(response, page_content)

        # print("- GETTING WEBSITE")
        website = getWebsite(response)

        # print("- GETTING CHECHOUT")
        checkout = getCheckout(response)

        # print("- GETTING ADDRESS")
        address = getAddress(response)

        # print("- GETTING BOOKING LINK")
        bookingLink = getBookingLink(response)

        # print("- GETTING PHOTOS")
        photos = getPhotos()

        # print("- GETTING REVIEWS")
        # reviews = getReviews()

        # print("- GETTING ABOUT DATA")
        # aboutdata = getAboutData()

        data = {
            "url": url,
            "phone": phone,
            "category": category,
            "menu": menu,
            "hours": hours,
            "website": website,
            "checkout": checkout,
            "address": address,
            "bookingLink": bookingLink,
            "photos": photos,
            "price": price,
            # "reviews": {"last_year": reviews["this_year"], "old": reviews["previous_years"]},
            # "price": aboutdata[0],
            # "hotel_stars": aboutdata[1],
            # "description": aboutdata[2],
        }

        return data

    except Exception as e:
        print("***********************GET_INFO_ERROR*************************")
        print(e)
        # traceback.print_exc()
        return None


index = 0
step = 40000


def debug_error():
    try:
        with open('[{}-{}]-error-places.json'.format(index, step)) as f:
            error_data = json.load(f)
        with open('[{}-{}]-places.json'.format(index, step)) as f:
            data = json.load(f)

        errors = error_data[0:1]

        for r in errors:
            print("****************PROCESSING_DEBUGER****************", r["place_id"])
            newData = getPlaceInfo(r["place_id"])
            if newData:
                merged_dict = {**newData, **r}
                # add to main file
                data.append(merged_dict)
                print("Data from google:", newData)
                # remove from errors-file
                error_data = [dict_ for dict_ in arr if dict_ != r]

            else:
                print("******************PLACE_NOT_ADDED_DEBUGER*************", r["place_id"])

    finally:
        with open('[{}-{}]-places.json'.format(index, step), 'w') as f:
            json.dump(data, f, indent=4)
        with open('[{}-{}]-error-places.json'.format(index, step), 'w') as f:
            json.dump(error_data, f, indent=4)
        driver.quit()


# async def process_place(r, loop, updatedData, problem_paces_ids):
#     print(f"****************PROCESSING-****************\n", r["name"])
#     newData = await loop.run_in_executor(executor, getPlaceInfo, r["place_id"])
#     if newData:
#         merged_dict = {**newData, **r}
#         updatedData.append(merged_dict)
#         # print("********************************\n")
#     else:
#         r["url"] = "https://www.google.com/maps/place/?hl=en&q=place_id:{}".format(r["place_id"])
#         problem_paces_ids.append(r)
#         print("******************PLACE_NOT_ADDED*************:", r["name"])


# async def main(index, step):
#     with open('./data/not_closed_points.json') as f:
#         data = json.load(f)

#     arr = data[index:step]
#     start_time = time.time()
#     updatedData = []
#     problem_paces_ids = []

#     loop = asyncio.get_event_loop()
#     for i, r in enumerate(arr):
#         await process_place(r, loop, updatedData, problem_paces_ids)

#     end_time = time.time()  # End time

#     elapsed_time = end_time - start_time
#     print("\n\nElapsed time: ", elapsed_time, "seconds\n\n")
#     with open('[{}-{}]-places.json'.format(index, step), 'w') as f:
#         json.dump(updatedData, f, indent=4)
#     with open('[{}-{}]-error-places.json'.format(index, step), 'w') as f:
#         json.dump(problem_paces_ids, f, indent=4)

# if __name__ == "__main__":
#     try:
#         asyncio.run(main(index, step))
#     except Exception as e:
#         print("****************MAIN_ERROR***************")
#         print(e)


if __name__ == "__main__":

    # debug_error()
    # sys.exit()

    try:
        with open('./data/not_closed_points.json') as f:
            data = json.load(f)

        arr = data[index:step]
        start_time = time.time()
        updatedData = []
        problem_paces_ids = []

        for i, r in enumerate(arr):
            print(f"****************PROCESSING-{i +1}****************\n", r["name"])
            newData = getPlaceInfo(r["place_id"])
            if (newData):
                merged_dict = {**newData, **r}
                updatedData.append(merged_dict)
                print("********************************\n")
            else:
                r["url"] = "https://www.google.com/maps/place/?hl=en&q=place_id:{}".format(r["place_id"])
                problem_paces_ids.append(r)
                print("******************PLACE_NOT_ADDED*************:", r["name"])

        end_time = time.time()  # End time

    except Exception as e:
        print("****************MAIN_ERROR***************")
        print(e)
        # traceback.print_exc()
    finally:
        elapsed_time = end_time - start_time
        print("\n\nElapsed time: ", elapsed_time, "seconds\n\n")
        with open('[{}-{}]-places.json'.format(index, step), 'w') as f:
            json.dump(updatedData, f, indent=4)
        with open('[{}-{}]-error-places.json'.format(index, step), 'w') as f:
            json.dump(problem_paces_ids, f, indent=4)
        driver.quit()


# fix me is Price there always?
# get subname ChIJJ4sGOVE60i0RPoPmS8rrBWw
# photo from reviews?
# checkin
# about labels could be negative
# web results?
