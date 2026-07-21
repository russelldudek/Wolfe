from pathlib import Path
from playwright.sync_api import sync_playwright
import base64, json, re

ROOT=Path(__file__).resolve().parent
DOCS=['resume.html','cover-letter.html','interview-brief.html','120-day-plan.html','data-use-card.html']
VIEWPORTS=[('laptop',1280,800),('tablet',768,1024),('mobile',390,844),('narrow',320,800)]
logo=base64.b64encode((ROOT/'assets/brand/wolfe-logo.png').read_bytes()).decode()
tokens=(ROOT/'brand-tokens.css').read_text()
doc_css=(ROOT/'documents.css').read_text().replace("@import url('./brand-tokens.css');",'')
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for doc in DOCS:
        raw=(ROOT/doc).read_text()
        html=re.sub(r'<link rel="stylesheet" href="documents.css">',f'<style>{tokens}\n{doc_css}</style>',raw)
        html=html.replace('assets/brand/wolfe-logo.png',f'data:image/png;base64,{logo}')
        for name,w,h in VIEWPORTS:
            page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
            page.set_content(html,wait_until='load')
            page.wait_for_timeout(100)
            data=page.evaluate('''() => {
              const root=document.documentElement;
              const sheet=document.querySelector('.doc-sheet, .document-sheet, main');
              const footer=document.querySelector('.doc-footer, footer');
              const bodyRect=document.body.getBoundingClientRect();
              const footerRect=footer ? footer.getBoundingClientRect() : null;
              const controls=[...document.querySelectorAll('a,button')].filter(x=>getComputedStyle(x).display!=='none');
              return {
                overflow: root.scrollWidth-root.clientWidth,
                bodyHeight: Math.round(bodyRect.height),
                viewportHeight: root.clientHeight,
                footerTop: footerRect ? Math.round(footerRect.top) : null,
                visibleControls: controls.map(x=>x.textContent.trim()).filter(Boolean),
                h1: document.querySelector('h1')?.textContent.trim() || null,
                logo: !!document.querySelector('img[alt*="Wolfe"]')
              };
            }''')
            results.append({'document':doc,'viewport':name,'width':w,'height':h,**data})
            page.close()
    browser.close()
(ROOT/'qa/document-browser-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
