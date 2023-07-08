import asyncio
import pyppeteer
import requests
import json


async def handle_response(response):
    url = response.url
    if 'https://www.instagram.com/api/v1/locations/690774840/sections/' in url:
        print(f"Caught response: {url}")
        data = await response.json()  # Parse the JSON response
        with open('response_data.json', 'w') as f:
            json.dump(data, f)


async def main():
    print("Connecting to browser")
    try:
        response = requests.get("http://localhost:9222/json/version")
        ws_url = response.json()['webSocketDebuggerUrl']

        browser = await pyppeteer.connect(browserWSEndpoint=ws_url)
        print("Connected to browser")

        pages = await browser.pages()
        print(f"Found {len(pages)} pages")

        page = pages[0]
        print(f"Page URL: {page.url}")

        page.on('response', handle_response)  # Set up the response handler

        await page.goto('https://www.instagram.com/explore/locations/690774840/')
        await page.waitForSelector('body')  # Replace 'body' with a selector for an element on the page

        # Scroll the page
        for _ in range(10):  # Replace 10 with the number of times you want to scroll
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)  # Wait a bit for the new content to load

    except Exception as e:
        print(f"An error occurred: {e}")

asyncio.run(main())
