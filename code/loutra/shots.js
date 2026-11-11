// Λήψεις του 3D μοντέλου για τα φύλλα του PDF: node shots.js <σελίδα.html> <φάκελος> '<json λήψεων>'
const { chromium } = require('playwright');
const [, , page, outdir, spec] = process.argv;
(async () => {
  const shots = JSON.parse(spec);
  const b = await chromium.launch();
  for (const s of shots) {
    const ctx = await b.newContext({ viewport: { width: s.w, height: s.h }, deviceScaleFactor: s.scale || 2 });
    const p = await ctx.newPage();
    p.on('pageerror', (e) => console.log('PAGE ERROR', e.message));
    p.on('console', (m) => { if (m.type() === 'error') console.log('CONSOLE', m.text()); });
    await p.goto('file://' + page + '#shot-' + s.room + '-' + s.view + '-' + (s.night ? 'night' : 'day') + '-' + (s.tags ? 1 : 0), { waitUntil: 'domcontentloaded' });
    await p.waitForFunction(() => window.__frames > 0, null, { timeout: 90000 });
    await p.evaluate(() => document.fonts && document.fonts.ready);
    await p.evaluate(([r, v, n, t]) => window.__shot(r, v, n, t), [s.room, s.view, !!s.night, !!s.tags]);
    await p.waitForTimeout(700);
    await p.screenshot({ path: outdir + '/' + s.name + '.jpg', type: 'jpeg', quality: s.q || 86 });
    console.log('ok', s.name);
    await ctx.close();
  }
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
