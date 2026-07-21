from pathlib import Path
from playwright.sync_api import sync_playwright
import base64, json, re

ROOT=Path(__file__).resolve().parent
html=(ROOT/'index.html').read_text()
css=(ROOT/'brand-tokens.css').read_text()+"\n"+(ROOT/'styles.css').read_text().replace("@import url('./brand-tokens.css');",'')
js=(ROOT/'app.js').read_text()
logo=base64.b64encode((ROOT/'assets/brand/wolfe-logo.png').read_bytes()).decode()
html=re.sub(r'<link rel="stylesheet" href="styles.css">',f'<style>{css}</style>',html)
html=re.sub(r'<script defer src="app.js"></script>','',html)
html=re.sub(r'<link rel="preconnect"[^>]+>','',html)
html=re.sub(r'<link href="https://fonts.googleapis.com[^>]+>','',html)
html=html.replace('assets/brand/wolfe-logo.png',f'data:image/png;base64,{logo}')
html=html.replace('</body>',f'<script>{js}</script></body>')

viewports=[('desktop',1440,900),('laptop',1280,800),('tablet',768,1024),('mobile',390,844),('narrow',320,800)]
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for name,w,h in viewports:
        page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
        errors=[]
        page.on('console', lambda msg: errors.append(f'console:{msg.type}:{msg.text}') if msg.type=='error' else None)
        page.on('pageerror', lambda exc: errors.append(f'pageerror:{exc}'))
        page.set_content(html,wait_until='load')
        page.wait_for_timeout(1500)
        dims=page.evaluate('''() => {
          const card=document.querySelector('.hero-data-card');
          const theater=document.querySelector('.issuance-theater');
          const cardRect=card?.getBoundingClientRect();
          const theaterRect=theater?.getBoundingClientRect();
          return {
            sw:document.documentElement.scrollWidth,
            cw:document.documentElement.clientWidth,
            logo:!!document.querySelector('.brand-lockup img'),
            h1:document.querySelector('h1')?.innerText,
            revealRemaining:[...document.querySelectorAll('.reveal:not(.is-visible)')].length,
            cardInside: !!cardRect && !!theaterRect && cardRect.left >= theaterRect.left-2 && cardRect.right <= theaterRect.right+2,
            cardAnimation:getComputedStyle(card).animationName,
            navVisible:getComputedStyle(document.querySelector('.site-nav')).display,
            docs:[...document.querySelectorAll('.document-links a')].length
          }
        }''')
        page.screenshot(path=str(ROOT/f'qa/site-{name}-viewport.png'),full_page=False)
        page.screenshot(path=str(ROOT/f'qa/site-{name}.png'),full_page=True)
        results.append({'viewport':name,'width':w,'height':h,'overflow':dims['sw']-dims['cw'],'logo':dims['logo'],'h1':dims['h1'],'card_inside_theater':dims['cardInside'],'card_animation':dims['cardAnimation'],'document_links':dims['docs'],'errors':errors})
        page.close()

    page=browser.new_page(viewport={'width':1280,'height':800})
    page.set_content(html,wait_until='load')
    page.wait_for_timeout(180)
    intermediate=page.evaluate('''() => ({
      heroCardTransform:getComputedStyle(document.querySelector('.hero-data-card')).transform,
      scanOpacity:getComputedStyle(document.querySelector('.scan-head')).opacity,
      heroCardAnimation:getComputedStyle(document.querySelector('.hero-data-card')).animationName
    })''')
    page.screenshot(path=str(ROOT/'qa/site-motion-intermediate.png'),full_page=False)
    page.wait_for_timeout(1350)
    page.locator('[data-scenario="support"]').click()
    page.wait_for_timeout(1200)
    support=page.evaluate('''() => ({dataset:document.querySelector('#card-dataset').textContent,posture:document.querySelector('#posture-label').textContent,pressed:document.querySelector('[data-scenario="support"]').getAttribute('aria-pressed'),status:document.querySelector('#issuance-studio').dataset.status,processing:document.querySelector('#issuance-studio').classList.contains('is-processing')})''')
    page.locator('[data-scenario="transactions"]').click()
    page.locator('[data-scenario="fulfillment"]').click()
    page.locator('[data-scenario="catalog"]').click()
    page.wait_for_timeout(1200)
    rapid=page.evaluate('''() => ({dataset:document.querySelector('#card-dataset').textContent,posture:document.querySelector('#posture-label').textContent,pressed:document.querySelector('[data-scenario="catalog"]').getAttribute('aria-pressed'),status:document.querySelector('#issuance-studio').dataset.status,processing:document.querySelector('#issuance-studio').classList.contains('is-processing')})''')
    page.screenshot(path=str(ROOT/'qa/site-interaction-catalog.png'),full_page=False)
    results.append({'motion_intermediate':intermediate,'interaction_support':support,'rapid_final_state':rapid})
    page.close()

    page=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
    page.set_content(html,wait_until='load')
    page.wait_for_timeout(100)
    reduced=page.evaluate('''() => ({
      revealRemaining:[...document.querySelectorAll('.reveal:not(.is-visible)')].length,
      heroAnimation:getComputedStyle(document.querySelector('.hero-data-card')).animationDuration,
      sourceAnimation:getComputedStyle(document.querySelector('.source-stream::after') || document.querySelector('.source-stream')).animationDuration,
      overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
      scenarioStatus:document.querySelector('#issuance-studio').dataset.status
    })''')
    page.screenshot(path=str(ROOT/'qa/site-reduced-motion.png'),full_page=True)
    results.append({'reduced_motion':reduced})
    page.close()
    browser.close()

(ROOT/'qa/browser-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
