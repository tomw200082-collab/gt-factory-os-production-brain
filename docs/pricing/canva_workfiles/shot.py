import asyncio,sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        pg=await b.new_page(viewport={"width":1080,"height":1920},device_scale_factor=1)
        await pg.goto("file://"+__file__.rsplit("/",1)[0]+"/pricelist.html")
        await pg.wait_for_timeout(1200)
        await pg.pdf(path="GT-Price-List-Drinks-SUMMER2026.pdf",width="1080px",height="1920px",
                     print_background=True,margin={"top":"0","bottom":"0","left":"0","right":"0"})
        # per-page PNG for QA
        n=await pg.evaluate("document.querySelectorAll('.page').length")
        for i in range(n):
            el=await pg.query_selector(f".page:nth-of-type({i+1})")
            await el.screenshot(path=f"p{i+1}.png")
        await b.close()
        print("pages",n)
asyncio.run(main())
