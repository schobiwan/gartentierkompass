import sys, asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        errs=[]
        for path, name, w, full in [(a.split('|')[0], a.split('|')[1], int(a.split('|')[2]), a.split('|')[3]=='1') for a in sys.argv[1:]]:
            pg = await b.new_page(viewport={"width": w, "height": 900})
            pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
            pg.on("pageerror", lambda ex: errs.append(str(ex)))
            await pg.goto("http://localhost:8765/"+path, wait_until="networkidle")
            await pg.wait_for_timeout(600)
            await pg.screenshot(path=name, full_page=full)
            await pg.close()
        print("errors:", errs)
        await b.close()
asyncio.run(main())
