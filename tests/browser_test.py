import pathlib, threading, http.server, functools, json
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parent.parent
server=http.server.ThreadingHTTPServer(('127.0.0.1',8087),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT/'public')))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8087');page.screenshot(path='/downloads/friday-desktop.png',full_page=True)
 for width in [390,320]:
  page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.screenshot(path=f'/downloads/friday-mobile-{width}.png',full_page=True)
 page.locator('#commandInput').fill('what can you do?');page.locator('button[type=submit]').first.click();assert 'local demo' in page.locator('#messages').inner_text()
 page.locator('#settingsBtn').click();page.locator('#speakToggle').uncheck();page.locator('#settingsDialog [data-close]').click()
 page.locator('#commandInput').fill('<img src=x onerror=alert(1)>');page.locator('#commandForm button').click();assert page.locator('#messages img').count()==0
 page.locator('#accountBtn').click();assert page.locator('#accountDialog').is_visible();page.locator('#accountDialog [data-close]').click()
 # Stub only recognizer for deterministic timing/state tests; not a real microphone test.
 page.add_init_script('''window.webkitSpeechRecognition=class {start(){setTimeout(()=>this.onstart?.(),0)} abort(){this.onend?.()} stop(){this.onend?.()}};''');page.reload();page.clock.install();page.locator('#micBtn').click();page.clock.fast_forward(12500);assert page.locator('#coreStatus').inner_text()=='STANDBY';assert 'asleep' in page.locator('#messages').inner_text()
 page.locator('#micBtn').click();page.locator('#stopBtn').click();page.clock.fast_forward(13000);assert page.locator('#coreStatus').inner_text()=='STANDBY'
 print(json.dumps({'errors':errors,'layoutWidths':[1280,390,320],'textFallback':True,'escapedUserInput':True,'micTimeoutMock':True,'stopMock':True}));assert not errors
 browser.close()
server.shutdown()
