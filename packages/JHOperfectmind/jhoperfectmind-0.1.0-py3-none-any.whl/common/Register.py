
import asyncio
from playwright.async_api import async_playwright
from common.helpers.Apply_filter import apply_filter  # You will need to rewrite this for Playwright if used
import time
import pyautogui



async def registration_process(event_data):
    userName = "hojustin.1128@gmail.com"
    password = "Starwars=1"


    # CSS selectors for relevant HTML fields
    login_button_selector = ".pm-login-button"
    userName_selector = "#textBoxUsername"
    password_selector = "#textBoxPassword"
    date_row_class = "bm-marker-row"
    register_now_selector = "#bookEventButton"
    justin_bookingID_selector = "input[aria-label='To choose Justin Ho use space or enter buttons']"
    next_button_selector = "a[title='Next']"
    fee_type_selector = "span:text('Drop-In: Fitness Member (Time-Based)')"
    next_button_fee_selector = "span:text('Next')"
    checkout_selector = "#checkoutButton"

    desired_event = event_data['desired_event']
    desired_date = event_data['desired_date']
    desired_time = event_data['desired_time']
    desired_location = event_data['desired_location']

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://vaughan.perfectmind.com/25076/Clients/BookMe4BookingPages/Classes?calendarId=71fe848e-2dbd-4ec5-92fa-7f2d0ad09354&widgetId=dff88c8a-0b78-4a94-9dde-250040385300&embed=False")


        await page.wait_for_selector(login_button_selector)
        await page.click(login_button_selector)

        await page.wait_for_selector(userName_selector)
        await page.fill(userName_selector, userName)
        await page.fill(password_selector, password)
        await page.keyboard.press("Enter")

        await page.wait_for_selector(f".{date_row_class}")

        # TODO: Rewrite apply_filter for Playwright if needed
        await apply_filter(page, desired_location, desired_event)

        # await page.wait_for_timeout(5000)  # 3000ms = 3s

        # # Find session listings using CSS selectors
        # # await asyncio.gather(
        # #     page.wait_for_load_state('load'),  # Full page load
        # #     page.wait_for_selector("table.bm-classes-grid tr")  # Element availability
        # # )
        rows = await page.query_selector_all("table.bm-classes-grid tr")
        current_date = None

        for row in rows:
            class_value = await row.get_attribute("class")
            print("Class value:", class_value)

            # This finds the dates
            if class_value == date_row_class:
                h2_element = await row.query_selector("h2[aria-label]")
                if h2_element:
                    current_date = await h2_element.get_attribute("aria-label")

            # This finds event name, time, and location
            elif class_value == "bm-class-row":
                time_element = await row.query_selector("div.anchor span")
                event_time = await time_element.inner_text() if time_element else None
                location_element = await row.query_selector("div.anchor.location-block span")
                event_location = await location_element.inner_text() if location_element else None
                print("date: " + str(current_date))
                print("time: " + str(event_time))

                print("__________________")
                if (current_date == desired_date):
                    print('date match')
                if (event_time == desired_time):
                    print('time match')

                print("++++++++++++++++")

                # session match
                if (current_date == desired_date and event_time == desired_time):
                    # Click the button
                    try:
                        button = await row.query_selector("input[type='button']")
                        if button:
                            await button.click()
                            print("Successfully clicked the register button.")
                            break
                    except Exception as e:
                        print("Could not click the button:", e)


        await page.wait_for_selector(register_now_selector)
        try:
            await page.click(register_now_selector)
            print("Successfully clicked the register_now button.")
        except Exception as e:
            print("Could not click the register_now button:", e)

        # Clicks Justin ID
        await page.wait_for_selector(justin_bookingID_selector)
        try:
            await page.click(justin_bookingID_selector)
            print("Successfully clicked the justin_bookingID button.")
        except Exception as e:
            print("Could not click the justin_bookingID button:", e)

        # Click first Next button
        await page.wait_for_selector(next_button_selector)
        try:
            await page.click(next_button_selector)
            print("Successfully clicked the first Next button.")
        except Exception as e:
            print("Could not click the first Next button:", e)

        page.wait_for_load_state('load')

        # Click second Next button
        await page.wait_for_selector(next_button_selector)
        try:
            await page.click(next_button_selector)
            print("Successfully clicked the second Next button.")
        except Exception as e:
            print("Could not click the second Next button:", e)

        # Click fee type
        await page.wait_for_selector(fee_type_selector)
        try:
            await page.click(fee_type_selector)
            print("Successfully clicked the fee_type.")
        except Exception as e:
            print("Could not click the fee_type:", e)

        # Click Next on fee page
        await page.wait_for_selector(next_button_fee_selector)
        try:
            await page.click(next_button_fee_selector)
            print("Successfully clicked the Next button on fee page.")
        except Exception as e:
            print("Could not click the button on fee page:", e)

        # Click Checkout
    
        await page.wait_for_selector(checkout_selector)
        try:
            await page.click(checkout_selector, click_count=2, delay=200)

            print("Successfully clicked the Checkout button.")
        except Exception as e:
            print("Could not click the checkout button:", e)


        # If you need to move the mouse to a specific location, use Playwright's mouse API
        # Example: await page.mouse.move(x, y); await page.mouse.click(x, y)
        await page.wait_for_timeout(3000)  # 3000ms = 3s

        page.wait_for_load_state('load')

        # Set your original coordinates
        x, y = 300, 430

        await page.mouse.move(x, y)
        await page.mouse.click(x, y)

        print("Successfully clicked the button at coordinates:", x, y)
            
        # Keep browser open for inspection
        await asyncio.sleep(2)
        await browser.close()



