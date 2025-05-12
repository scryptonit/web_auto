import primp
from patchright.sync_api import sync_playwright
import time
import random
import math

def click_random(locator, manual_radius: float = None):
    box = locator.bounding_box()
    if box is None:
        raise Exception("Bounding box not found")
    width, height = box["width"], box["height"]
    cx, cy = width / 2, height / 2
    radius = manual_radius if manual_radius is not None else min(width, height) / 2
    angle = random.uniform(0, 2 * math.pi)
    r = radius * math.sqrt(random.uniform(0, 1))
    rand_x = cx + r * math.cos(angle)
    rand_y = cy + r * math.sin(angle)

    locator.click(position={"x": rand_x, "y": rand_y})


valid_versions = [f"chrome_{v}" for v in range(128, 134) if v != 132]
chosen_version = random.choice(valid_versions)

client = primp.Client(impersonate=chosen_version, impersonate_os="macos") # windows, linux
user_agent = client.headers["user-agent"]

launch_args = [
    "--disable-blink-features=AutomationControlled",
    "--disable-popup-blocking",
    "--disable-default-apps"
]

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=launch_args,
        channel="chrome"
    )
    context = browser.new_context(
        locale="en-US",
        user_agent=user_agent,
        viewport={"width": 1280, "height": 800}
    )


    context.add_init_script("""
            Object.defineProperty(window, 'navigator', {
                value: new Proxy(navigator, {
                    has: (target, key) => key === 'webdriver' ? false : key in target,
                    get: (target, key) =>
                        key === 'webdriver' ? undefined : typeof target[key] === 'function' ? target[key].bind(target) : target[key]
                })
            });
                            
        """)


    page = context.new_page()
    page.goto("https://jspaint.app/")
    time.sleep(5)
    brush = page.locator('xpath=/html/body/div[3]/div/div[3]/div[1]/div/div[1]/div[8]')
    click_random(brush)
    time.sleep(15)
    canvas = page.locator('xpath=/html/body/div[3]/div/div[3]/div[2]/canvas')
    print(canvas.bounding_box())

    for _ in range(1000):
        click_random(canvas)
        time.sleep(0.01)
    print("Done")


    time.sleep(2000)

    browser.close()
