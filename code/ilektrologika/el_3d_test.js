// Λειτουργικός έλεγχος της σελίδας 3D (el_3d_template.html): node el_3d_test.js <σελίδα από «el_3d.py --test»> [desk|phone]
// Για ΚΑΘΕ χώρο: κάθε σημείο της λίστας επιλέγεται → ανοίγει η κάρτα του και η ετικέτα του φαίνεται μέσα στην οθόνη (η κάμερα γυρίζει μόνη της αν ο τοίχος
// του είναι κομμένος)· κάθε τοίχος της λίστας «από πού έρχεται το καλώδιο» ανοίγει την εξήγησή του· όλες οι όψεις πατιούνται· καμία ετικέτα πάνω σε άλλη·
// κανένα σφάλμα στην κονσόλα. Έξοδος 1 αν κάτι αποτύχει. Θέλει node + playwright (headless Chromium με λογισμικό WebGL – αργό: ≈ 3 λεπτά ανά μέγεθος).
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const errs = [], bad = [];
  const vp = process.argv[3] === 'phone' ? { width: 390, height: 780 } : { width: 1500, height: 900 };
  const p = await b.newPage({ viewport: vp, reducedMotion: 'reduce' });
  p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  p.on('pageerror', (e) => errs.push(String(e)));
  await p.goto('file://' + require('path').resolve(process.argv[2]));
  await p.waitForTimeout(2000);
  const rooms = await p.$$eval('#rooms button', (bs) => bs.map((x) => x.textContent));
  let total = 0;
  for (let r = 1; r < rooms.length; r++) {
    await p.evaluate((r) => { document.querySelector('#rooms button:nth-child(' + (r + 1) + ')').click(); }, r);
    await p.waitForTimeout(800);
    const us = await p.$$eval('#pts .row', (rs) => rs.map((x) => x.dataset.u));
    let ok = 0;
    for (const u of us) {
      await p.evaluate((u) => { document.querySelector('.row[data-u="' + CSS.escape(u) + '"]').click(); }, u);
      await p.waitForTimeout(450);
      const st = await p.evaluate((u) => {
        const l = document.querySelector('.lb[data-u="' + CSS.escape(u) + '"]'), c = document.getElementById('card'), q = l.getBoundingClientRect();
        const vis = [...document.querySelectorAll('.lb:not(.off)')].map((x) => x.getBoundingClientRect());
        let over = 0;
        for (let i = 0; i < vis.length; i++) for (let j = i + 1; j < vis.length; j++) if (vis[i].left < vis[j].right && vis[i].right > vis[j].left && vis[i].top < vis[j].bottom && vis[i].bottom > vis[j].top) over++;
        return { sel: l.classList.contains('sel'), off: l.classList.contains('off'), card: !c.hidden, x: Math.round(q.left), y: Math.round(q.top), w: innerWidth, h: innerHeight, over };
      }, u);
      if (st.sel && !st.off && st.card && st.x > -5 && st.y > -5 && st.x < st.w && st.y < st.h && !st.over) ok++; else bad.push(rooms[r] + ' ' + u + ' ' + JSON.stringify(st));
    }
    const gs = await p.$$eval('#how .how', (rs) => rs.map((x) => x.dataset.g));
    for (const g of gs) {
      await p.evaluate((g) => { document.querySelector('.how[data-g="' + CSS.escape(g) + '"]').click(); }, g);
      await p.waitForTimeout(200);
      if (!(await p.evaluate(() => !document.getElementById('card').hidden && document.getElementById('cb').textContent.length > 40))) bad.push(rooms[r] + ' τοίχος ' + g);
    }
    const nv = await p.$$eval('#views button', (bs) => bs.length);
    for (let i = 1; i <= nv; i++) { await p.evaluate((i) => { document.querySelector('#views button:nth-child(' + i + ')').click(); }, i); await p.waitForTimeout(150); }
    total += us.length;
    console.log(rooms[r].padEnd(12), 'σημεία', String(us.length).padStart(2), 'ok', String(ok).padStart(2), '· τοίχοι', gs.length, '· όψεις', nv);
  }
  await b.close();
  console.log('σφάλματα κονσόλας:', errs.length, errs.slice(0, 5).join(' | '));
  console.log('ΕΛΕΓΧΟΣ 3D (' + vp.width + ' px): ' + total + ' επιλογές · ' + (bad.length + errs.length) + ' ΛΑΘΟΣ');
  if (bad.length) console.log(bad.slice(0, 30).join('\n'));
  process.exit(bad.length + errs.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
