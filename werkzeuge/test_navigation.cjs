const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
 const browser = await chromium.launch({headless:true});
 const page = await browser.newPage();
 for (const width of [375,1440]) {
  await page.setViewportSize({width,height:900});
  await page.goto('http://localhost:8765/');
  const result = await page.evaluate(() => ({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,nav:[...document.querySelectorAll('header nav a')].map(a=>a.textContent)}));
  assert.ok(result.scrollWidth <= width);
  assert.deepEqual(result.nav,['Einstieg','Werkbank','Methode','Guard','Mit sitelook','Kontakt']);
  console.log(JSON.stringify(result));
  await page.locator('#einstieg a[href="#mit-sitelook"]').click();
  assert.equal(new URL(page.url()).hash,'#mit-sitelook');
  assert.equal(await page.locator('#mit-sitelook a[href^="mailto:"]').getAttribute('href'),'mailto:info@sitelook.gmbh?subject=Einführung%20Leitplanken');
  assert.equal(await page.locator('#kontakt a[href^="mailto:"]').count(),0);
  assert.equal(await page.locator('#kontakt a').count(),2);
  assert.equal(await page.locator('#einordnung').count(),1);
  assert.equal(await page.locator('#offen').count(),1);
  await page.goto('http://localhost:8765/');
 }
 for (const path of ['impressum.html','datenschutz.html','404.html','methode/index.html','methode/01-sprintplan-und-write-scope.html']) {
  await page.goto('http://localhost:8765/'+path);
  assert.equal(await page.locator('footer a[href="/#mit-sitelook"]').count(),1);
  assert.equal(await page.locator('footer a[href="/#kontakt"]').count(),1);
  if (['impressum.html','datenschutz.html'].includes(path)) assert.equal(await page.locator('meta[property="og:image"]').getAttribute('content'),'https://wirkarchitektur.de/og-wirkarchitektur.png');
 }
 console.log('Sprungziel, CTA, Kontakt, erhaltene Abschnitte, Unterseiten-Fußzeilen und OG: OK');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
