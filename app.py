from flask import Flask, request, jsonify
import asyncio
import threading
from playwright.async_api import async_playwright
import random
from flask_cors import CORS  # Import the CORS package


app = Flask(__name__)
CORS(app) 



def get_random_proxy():
    with open("proxy.txt", "r") as file:
        proxies = file.readlines()
    proxy = random.choice(proxies).strip()  # Get a random proxy and remove any extra spaces/newlines
    return proxy

class HSW:
    def __init__(self, sitekey, host, link,rqstid):
        self.sitekey = sitekey
        self.host = host
        self.link = link
        self.rqstid = rqstid
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_run, daemon=True).start()
        

    def start_run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.run())
        

    async def run(self):
        async with async_playwright() as p:


            proxy = get_random_proxy()

            # Extract proxy credentials and host from the proxy string
            proxy_parts = proxy.split('@')
            proxy_auth = proxy_parts[0]
            proxy_host = proxy_parts[1]
            
            # Set up Chromium with proxy and additional settings for undetectability
            browser = await p.chromium.launch(
                headless=False,
                proxy={
                    'server': f'http://{proxy_host}',  # Proxy host and port
                    'username': proxy_auth.split(':')[0],  # Proxy username
                    'password': proxy_auth.split(':')[1]   # Proxy password
                }
            )
            # Launch the browser with specific arguments for undetectable.io
            browser = await p.chromium.launch(headless=False)  # Set headless=False to see the browser
            context = await browser.new_context()
            self.page = await context.new_page()

            # Set up the route for the specified link
            await self.page.route(self.link, lambda r: r.fulfill(
            status=200,
            body=open("captcha.html", "r").read()
            .replace("SITEKEYHERE", self.sitekey)          # Replace SITEKEYHERE with the actual sitekey
            .replace("SITEREQUESTID", self.rqstid),    # Replace SITEREQUESTID with the actual siterqstid
            content_type="text/html"
            ))

            # Navigate to the undetectable.io website
            await self.page.goto(self.link)  # Ensure 'link' points to the undetectable.io page
            await self.page.wait_for_load_state('domcontentloaded')

            try:
                # Wait for the iframe to load
                iframe = await self.page.wait_for_selector("xpath=/html/body/center/h1/div/iframe", timeout=600000)
                self.frame = await iframe.content_frame()
                print("Found Frame")
            except Exception as e:
                print("Error:", e)

@app.route('/start', methods=['POST'])
def start_captcha():
    data = request.json
    sitekey = str(data.get('SiteKey', ''))
    host = str(data.get('Host', ''))
    link = str(data.get('Link', ''))
    rqstid = str(data.get('RequestId', ''))

    if not sitekey or not host or not link:
        return jsonify({"error": "Missing parameters"}), 400

    hsw = HSW(sitekey, host, link,rqstid)
    return jsonify({"message": "Captcha process started"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)
