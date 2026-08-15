import asyncio, sys
from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8765"
SHOTS = [
    ("/works/lunch/#demo", "assets/shots/lunch.png", 1280, 800, 1),
    ("/works/radar/#feed", "assets/shots/radar.png", 1280, 800, 1),
    ("/works/rice/#tool", "assets/shots/rice.png", 1280, 800, 1),
]

async def main():
    errors = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for path, out, w, h, scale in SHOTS:
            pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
            msgs = []
            pg.on("console", lambda m: msgs.append((m.type, m.text)))
            await pg.goto(BASE + path, wait_until="networkidle")
            await pg.wait_for_timeout(2500)
            await pg.screenshot(path=out)
            bad = [m for m in msgs if m[0] == "error"]
            print(out, "ok", "console_errors:", bad[:3])
            errors += bad
            await pg.close()
        # full page check of home
        pg = await b.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
        await pg.goto(BASE + "/", wait_until="networkidle")
        await pg.wait_for_timeout(1500)
        await pg.screenshot(path="/tmp/home_full.png", full_page=True)
        print("home full ok")
        await b.close()
    print("total console errors:", len(errors))

asyncio.run(main())
