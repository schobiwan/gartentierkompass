import sys; sys.path.insert(0,'.')
import build
from playwright.sync_api import sync_playwright
open('out/_zk.html','w',encoding='utf-8').write(build.zaehlkarte_html())
import os; os.makedirs('out/downloads',exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome");pg=b.new_page()
    pg.goto("http://localhost:8765/_zk.html");pg.wait_for_timeout(800)
    pg.pdf(path="out/downloads/zaehlkarte-insektensommer.pdf",format="A4",print_background=True,prefer_css_page_size=True)
    b.close()
os.remove('out/_zk.html')
