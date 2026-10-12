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

# Optional audio regression uses an existing MP3. No provider requests or credits.
import os
if os.environ.get("FRIDAY_TEST_AUDIO"):
 import pathlib,threading,http.server,functools,json
 from playwright.sync_api import sync_playwright
 root=pathlib.Path(__file__).resolve().parent.parent/'public'
 # Generated audio is deliberately not committed. Supply the already-generated MP3.
 blob=pathlib.Path(os.environ["FRIDAY_TEST_AUDIO"]).read_bytes()
 s=http.server.ThreadingHTTPServer(('127.0.0.1',8088),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root)))
 threading.Thread(target=s.serve_forever,daemon=True).start()
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
  page=b.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.route('**/api/config',lambda r:r.fulfill(json={'configured':False,'ttsConfigured':False}))
  page.route('**/api/tts',lambda r:r.fulfill(status=200,content_type='audio/mpeg',body=blob))
  page.goto('http://127.0.0.1:8088');page.locator('#settingsBtn').click();page.locator('#speakToggle').check();page.locator('#settingsDialog [data-close]').click()
  page.evaluate('ttsConfigured=true;authToken="local-test-only";awaitingName=false')
  page.locator('#commandInput').fill('Friday: Godspeed');page.locator('#commandForm button').click()
  page.wait_for_function('audio && audio.readyState>=2');during=page.evaluate('({duration:audio.duration,readyState:audio.readyState,paused:audio.paused})')
  page.wait_for_function('audio===null && document.getElementById("coreStatus").textContent==="STANDBY"')
  # Stalled media metadata must be bounded and call a clearly reported fallback.
  page.evaluate('window.Audio=class {pause(){}load(){} };ttsConfigured=true;authToken="local-test-only"')
  page.clock.install();page.locator('#commandInput').fill('Friday: Godspeed');page.locator('#commandForm button').click();page.wait_for_function('audio!==null');page.clock.fast_forward(8100)
  page.wait_for_function('audio===null');assert 'playback could not start' in page.locator('#messages').inner_text()
  print(json.dumps({'realMP3LocalPlayback':during,'returnsToStandby':True,'metadataTimeoutFallback':True,'pageErrors':errors}));assert not errors
  b.close()
 s.shutdown()
