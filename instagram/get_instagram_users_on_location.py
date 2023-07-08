from pyppeteer import executablePath
import asyncio
from pyppeteer import launch
import json
import pyppeteer

# Initialize a set to store the unique usernames
usernames = set()


print(executablePath())


async def main():
    global usernames
    return
    browser = await launch(headless=False)
    # browser.userAgent(userAgent)
    page = await browser.newPage()

    # Set up response interception
    # await page.setRequestInterception(True)
    # page.on('response', lambda res: asyncio.ensure_future(log_and_continue(res)))

    # Navigate to Instagram
    await asyncio.sleep(5)
    print("1")
    # try:
    #     await page.goto('https://www.instagram.com/accounts/login/', timeout=100000)  # set timeout to 10 seconds
    # except pyppeteer.errors.NetworkError as e:
    #     print(f"NetworkError occurred: {e}")

    # Wait for the page to load
    # print("2")
    # await asyncio.sleep(15)

    # # Fill in the username and password
    # await page.type('input[name="username"]', 'duniakripto_ind')
    # await page.type('input[name="password"]', '7895123avA!')
    # await asyncio.sleep(5)
    # # Submit the form
    # await page.click('button[type="submit"]')

    # # Wait for the page to load
    # await asyncio.sleep(20)

    # print("3")

    # Go to the specific location
    # await page.goto('https://www.instagram.com/explore/locations/690774840/')

    # Wait for the page to load
    # await asyncio.sleep(100)

    # Keep scrolling down until we have enough usernames
    # while len(usernames) < 1000:
    #     # Scroll down
    #     await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    #     # Wait for the page to load
    #     await asyncio.sleep(2)

    # # Save the unique usernames to a JSON file
    # with open('usernames.json', 'w') as f:
    #     json.dump(list(usernames), f)

    # Close the browser
    # await browser.close()


async def log_and_continue(res):
    global usernames
    # If the URL of the response matches the API URL, log it
    if 'https://www.instagram.com/api/v1/locations/690774840/sections/' in res.url:
        # Get the response body
        body = await res.text()
        # Parse it as JSON
        data = json.loads(body)
        # Extract the usernames and add them to the list
        for section in data.get('sections', []):
            for media in section.get('layout_content', {}).get('medias', []):
                user = media.get('media', {}).get('user', {})
                username = user.get('username')
                is_private = user.get('is_private')
                if username is not None and not is_private:
                    usernames.add(username)

    # Continue the request
    await res.continue_()

asyncio.run(main())
