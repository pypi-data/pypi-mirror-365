from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pyautogui
from common.helpers.Apply_filter import apply_filter

def registration_process_v(event_data):

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    userName = "hojustin.1128@gmail.com"
    password = "Starwars=1"

    # List of relevent HTML fields
    login_button = "pm-login-button"
    userName_html = "textBoxUsername"
    password_html = "textBoxPassword"
    date_HTMl_field = "bm-marker-row"
    register_now_button = "bookEventButton"
    justin_bookingID = ".//input[@aria-label='To choose Justin Ho use space or enter buttons']"
    next_button_default = ".//a[@title='Next']"
    fee_type= "//span[contains(text(), 'Drop-In: Fitness Member (Time-Based)')]"
    next_button_fee_page = "//span[contains(text(), 'Next')]"
    checkout_button = "checkoutButton"


    desired_event = event_data['desired_event']
    desired_date = event_data['desired_date']
    desired_time = event_data['desired_time']
    desired_location = event_data['desired_location']

    driver.get("https://vaughan.perfectmind.com/25076/Clients/BookMe4BookingPages/Classes?calendarId=1d032376-c4bb-4023-80f5-7c3c44de0637&widgetId=dff88c8a-0b78-4a94-9dde-250040385300&embed=False")

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, login_button))
    )

    driver.find_element(By.CLASS_NAME, login_button).click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, userName_html))
    )

    username_field = driver.find_element(By.ID, userName_html)
    username_field.clear()
    username_field.send_keys(userName)

    password_field = driver.find_element(By.ID, password_html)
    password_field.clear()
    password_field.send_keys(password + Keys.ENTER)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, date_HTMl_field))
    )

    apply_filter(driver, desired_location,desired_event)

    #finds the session listings
    rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'bm-classes-grid')]//tr")

    current_date = None

    for row in rows:
        class_value = row.get_attribute("class")

        # This finds the dates
        if class_value == date_HTMl_field:
            h2_element = row.find_element(By.XPATH, ".//h2[@aria-label]")  
            current_date = h2_element.get_attribute("aria-label")

        # This finds event name, time, and location
        elif class_value == "bm-class-row":

            time_element = row.find_element(By.XPATH, ".//div[@class='anchor']//span")
            event_time = time_element.text
            location_element = row.find_element(By.XPATH, ".//div[@class='anchor location-block']//span")
            event_location = location_element.text
            print("date: " + current_date)
            print("time: " + event_time)

            print("__________________")
            if (current_date == desired_date):
                print('date match')
            if (event_time == desired_time):
                print('time match')

            print("++++++++++++++++")

            #session match
            if (current_date == desired_date and
                event_time == desired_time):
                
                # Click the button
                try:
                    button = row.find_element(By.XPATH, ".//input[@type='button']")
                    button.click()
                    print("Successfully clicked the register button.")
                    break
                except Exception as e:
                    print("Could not click the button:", e)


    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, register_now_button))
    )

    try:
        button = driver.find_element(By.ID, register_now_button)
        button.click()
        print("Successfully clicked the register_now button.")
    except Exception as e:
        print("Could not click the register_now button:", e)

    #clicks Justin ID
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, justin_bookingID))
    )

    try:
        button = driver.find_element(By.XPATH, justin_bookingID)
        button.click()
        print("Successfully clicked the justin_bookingID button.")
    except Exception as e:
        print("Could not click the justin_bookingID button:", e)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, next_button_default))
    )

    try:
        button = driver.find_element(By.XPATH, next_button_default)
        button.click()
        print("Successfully clicked the first Next button.")
    except Exception as e:
        print("Could not click the first Next button:", e)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, next_button_default))
    )

    try:
        button = driver.find_element(By.XPATH, next_button_default)
        button.click()
        print("Successfully clicked the second Next button.")
    except Exception as e:
        print("Could not click the second Next button:", e)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, fee_type))
    )

    try:
        button = driver.find_element(By.XPATH, fee_type)
        button.click()
        print("Successfully clicked the fee_type.")
    except Exception as e:
        print("Could not click the fee_type:", e)


    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, next_button_fee_page))
    )

    try:
        button = driver.find_element(By.XPATH, next_button_fee_page)
        button.click()
        print("Successfully clicked the Next button on fee page.")
    except Exception as e:
        print("Could not click the button on fee page:", e)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, checkout_button))
    )

    try:
        button = driver.find_element(By.ID, checkout_button)
        button.click()
        print("Successfully clicked the Checkout button.")
    except Exception as e:
        print("Could not click the checkout button:", e)


    time.sleep(2)

    button_x = 328
    button_y = 586

    pyautogui.moveTo(button_x, button_y, duration=1)
    pyautogui.click()

    time.sleep(2)
    
    driver.close()
