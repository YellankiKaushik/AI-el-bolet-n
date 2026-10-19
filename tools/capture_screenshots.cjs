/* Optional maintainer tool: capture real rendering of tools/demo.py --name screenshots. */
'use strict';
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const {chromium} = require('playwright');
const sharp = require('sharp');

async function main() {
  const root = path.resolve(__dirname, '..');
  const base = 'http://127.0.0.1:8789';
  const credentials = JSON.parse(await fs.readFile(path.join(root, '.tmp/screenshots/credentials.json'), 'utf8'));
  const output = path.join(root, 'docs/screenshots');
  await fs.mkdir(output, {recursive: true});
  const browser = await chromium.launch({headless: true, executablePath: process.env.CHROMIUM_EXECUTABLE || undefined});
  const context = await browser.newContext({viewport: {width:1440,height:900},deviceScaleFactor:1,reducedMotion:'reduce',colorScheme:'light'});
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const manifest = {data:'Fictional demo fixtures only; no real credentials, drafts or subscribers',renderer:'Playwright Chromium',images:[]};
  async function capture(target, name, state) {
    await target.evaluate(() => document.fonts.ready);
    const buffer = await target.screenshot({animations:'disabled'});
    const file = path.join(output, name);
    await sharp(buffer).png({compressionLevel:9,adaptiveFiltering:true}).toFile(file);
    const bytes = await fs.readFile(file);
    const meta = await sharp(bytes).metadata();
    const geometry = await target.evaluate(() => ({viewport:innerWidth,documentWidth:document.documentElement.scrollWidth}));
    assert.ok(geometry.documentWidth <= geometry.viewport, `${name}: horizontal overflow`);
    manifest.images.push({file:name,width:meta.width,height:meta.height,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),state,url:target.url().replace(base,''),cssViewport:target.viewportSize()});
  }
  try {
    await page.goto(base, {waitUntil:'networkidle'});
    await page.getByText('DEMO WORKSPACE', {exact:false}).waitFor();
    await capture(page,'homepage-desktop.png','Homepage with clearly marked fictional published editions');
    await page.goto(base+'/admin');
    await page.getByLabel('Editor password',{exact:true}).fill(credentials.ADMIN_PASSWORD);
    await page.getByRole('button',{name:'Unlock workbench ↗',exact:true}).click();
    await page.getByRole('tab',{name:'Editions',exact:true}).waitFor();
    await page.locator('.studio-top').evaluate(el=>el.scrollIntoView({block:'start'}));
    await capture(page,'editor-dashboard.png','Authenticated edition dashboard; fictional data, email off');
    await page.getByRole('button',{name:/DRAFT Demo: Your next briefing starts here/}).click();
    await page.locator('.editor-header').evaluate(el=>el.scrollIntoView({block:'start'}));
    await page.evaluate(()=>window.scrollBy(0,-24));
    await capture(page,'newsletter-editor.png','Unapproved fictional draft editor; no real news approved');
    await page.locator('.draft-preview > summary').click();
    await page.locator('.draft-preview').evaluate(el=>el.scrollIntoView({block:'start'}));
    await page.evaluate(()=>window.scrollBy(0,-24));
    await capture(page,'newsletter-preview.png','Saved fictional edition preview with source references');
    await page.goto(base+'/archive');
    await page.getByRole('link',{name:/Demo: A quieter kind of AI briefing/}).click();
    await capture(page,'published-edition.png','Fictional published edition on localhost only');
    const mobileContext = await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,reducedMotion:'reduce',colorScheme:'light'});
    const mobile = await mobileContext.newPage();
    mobile.on('pageerror',error=>errors.push(error.message));
    await mobile.goto(base,{waitUntil:'networkidle'});
    await capture(mobile,'homepage-mobile.png','Mobile homepage, 390 CSS pixels at 2x pixel density');
    await mobileContext.close();
    assert.deepEqual(errors, [], 'Browser JavaScript errors');
    manifest.javascriptErrors = errors;
    await fs.writeFile(path.join(output,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
    console.log(JSON.stringify(manifest,null,2));
  } finally {
    await context.close();
    await browser.close();
  }
}
main().catch(error=>{console.error(error.message);process.exitCode=1;});
