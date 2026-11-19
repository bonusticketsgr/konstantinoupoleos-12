// Λειτουργικός έλεγχος της σελίδας 3D (el_3d_template.html): node el_3d_test.js <σελίδα από «el_3d.py --test»> [desk|phone] [orbit|walk]
// (α) ΑΠΟ ΕΞΩ, για ΚΑΘΕ χώρο: κάθε σημείο της λίστας επιλέγεται → ανοίγει η κάρτα του και η ετικέτα του φαίνεται μέσα στην οθόνη (η κάμερα γυρίζει μόνη της αν
//     ο τοίχος του είναι κομμένος)· κάθε τοίχος της λίστας «από πού έρχεται το καλώδιο» ανοίγει την εξήγησή του· όλες οι όψεις πατιούνται· καμία ετικέτα πάνω σε άλλη.
// (β) ΠΕΡΙΗΓΗΣΗ (περπάτημα μέσα στο σπίτι): μπαίνει από την πόρτα· περπατά με τα πλήκτρα χωρίς ΠΟΤΕ να βρεθεί μέσα σε τοίχο / κολόνα / έπιπλο· κάθε χώρος
//     φτάνεται από το κουμπί του· κάθε σημείο της λίστας σε πάει μπροστά του και η ετικέτα του φαίνεται (όχι κάτω από πλαίσιο / κάρτα / χάρτη)· πάτημα στο
//     πάτωμα, στον χάρτη και στον μοχλό· διάφανοι / κλειστοί τοίχοι· έξοδος· άνοιγμα κατευθείαν μέσα με #mesa.
// Κανένα σφάλμα στην κονσόλα. Έξοδος 1 αν κάτι αποτύχει. Θέλει node + playwright (headless Chromium με λογισμικό WebGL – αργό: λίγα λεπτά ανά μέγεθος).
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const errs = [], bad = [];
  const phone = process.argv[3] === 'phone', only = process.argv[4] || '';
  const vp = phone ? { width: 390, height: 780 } : { width: 1500, height: 900 };
  const url = 'file://' + require('path').resolve(process.argv[2]);
  const open = async (hash) => {
    const p = await b.newPage({ viewport: vp, reducedMotion: 'reduce' });
    p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
    p.on('pageerror', (e) => errs.push(String(e)));
    await p.goto(url + (hash ? '#' + hash : ''));
    await p.waitForTimeout(2000);
    return p;
  };
  const labelState = (p, u) => p.evaluate((u) => {
    const l = document.querySelector('.lb[data-u="' + CSS.escape(u) + '"]'), c = document.getElementById('card'), q = l.getBoundingClientRect();
    const vis = [...document.querySelectorAll('.lb:not(.off)')].map((x) => x.getBoundingClientRect());
    let over = 0;
    for (let i = 0; i < vis.length; i++) for (let j = i + 1; j < vis.length; j++) if (vis[i].left < vis[j].right && vis[i].right > vis[j].left && vis[i].top < vis[j].bottom && vis[i].bottom > vis[j].top) over++;
    let under = 0;                                 // ετικέτα κάτω από κάτι που σκεπάζει την εικόνα
    const cx = (q.left + q.right) / 2, cy = (q.top + q.bottom) / 2;
    ['ui', 'card', 'mm', 'joy'].forEach((k) => { const e = document.getElementById(k); if (e.hidden) return; const r = e.getBoundingClientRect(); if (cx > r.left && cx < r.right && cy > r.top && cy < r.bottom) under++; });
    return { sel: l.classList.contains('sel'), off: l.classList.contains('off'), card: !c.hidden, x: Math.round(q.left), y: Math.round(q.top), w: innerWidth, h: innerHeight, over, under };
  }, u);
  const goodLabel = (st) => st.sel && !st.off && st.card && st.x > -5 && st.y > -5 && st.x < st.w && st.y < st.h && !st.over && !st.under;
  let total = 0, wtotal = 0;

  // ---------------------------------------------------------------- (α) από έξω
  if (only !== 'walk') {
    const p = await open('');
    const rooms = await p.$$eval('#rooms button', (bs) => bs.map((x) => x.textContent));
    for (let r = 1; r < rooms.length; r++) {
      await p.evaluate((r) => { document.querySelector('#rooms button:nth-child(' + (r + 1) + ')').click(); }, r);
      await p.waitForTimeout(800);
      const us = await p.$$eval('#pts .row', (rs) => rs.map((x) => x.dataset.u));
      let ok = 0;
      for (const u of us) {
        await p.evaluate((u) => { document.querySelector('.row[data-u="' + CSS.escape(u) + '"]').click(); }, u);
        await p.waitForTimeout(450);
        const st = await labelState(p, u);
        if (goodLabel(st)) ok++; else bad.push(rooms[r] + ' ' + u + ' ' + JSON.stringify(st));
      }
      const gs = await p.$$eval('#how .how', (rs) => rs.map((x) => x.dataset.g));
      for (const g of gs) {
        await p.evaluate((g) => { document.querySelector('.how[data-g="' + CSS.escape(g) + '"]').click(); }, g);
        await p.waitForTimeout(200);
        if (!(await p.evaluate(() => !document.getElementById('card').hidden && document.getElementById('cb').textContent.length > 40))) bad.push(rooms[r] + ' τοίχος ' + g);
      }
      const nv = await p.$$eval('#views button:not(.pri)', (bs) => bs.length);
      for (let i = 0; i < nv; i++) { await p.evaluate((i) => { document.querySelectorAll('#views button:not(.pri)')[i].click(); }, i); await p.waitForTimeout(150); }
      if (await p.evaluate(() => window.__k12.s.wk)) bad.push(rooms[r] + ': μια όψη άνοιξε την περιήγηση');
      total += us.length;
      console.log(rooms[r].padEnd(12), 'σημεία', String(us.length).padStart(2), 'ok', String(ok).padStart(2), '· τοίχοι', gs.length, '· όψεις', nv);
    }
    await p.close();
  }

  // ---------------------------------------------------------------- (β) περιήγηση
  if (only !== 'orbit') {
    const p = await open('');
    const S = () => p.evaluate(() => window.__k12.s);
    const idle = async () => { for (let i = 0; i < 120; i++) { const s = await S(); if (!s.busy) return s; await p.waitForTimeout(50); } bad.push('περιήγηση: δεν σταμάτησε'); return S(); };
    const isFree = (s) => p.evaluate(([x, y]) => window.__k12.free(x, y), [s.x, s.y]);
    const chip = (box, txt) => p.evaluate(([box, txt]) => { const q = [...document.querySelectorAll(box + ' button')].find((x) => x.textContent.indexOf(txt) >= 0); if (q) q.click(); return !!q; }, [box, txt]);
    const need = (c, msg) => { if (!c) bad.push('περιήγηση: ' + msg); };
    const calls0 = (await S()).calls;
    // 1. είσοδος από «όλο το σπίτι»
    await p.evaluate(() => document.querySelector('#views button.pri').click()); await p.waitForTimeout(600);
    let s = await idle();
    need(s.wk && s.room === 'saloni' && (await isFree(s)), 'δεν μπήκε από την πόρτα εισόδου ' + JSON.stringify(s));
    need((await p.evaluate(() => location.hash)) === '#mesa', 'η διεύθυνση δεν έγινε #mesa');
    need(await p.evaluate(() => !document.getElementById('mm').hidden && document.body.classList.contains('wk')), 'ο χάρτης δεν φαίνεται');
    need((await p.evaluate(() => document.getElementById('joy').hidden)) === !phone, 'ο μοχλός: λάθος εμφάνιση για αυτή την οθόνη');
    console.log('σχεδιάσεις ανά εικόνα (draw calls): από έξω', calls0, '· μέσα', s.calls);
    // 2. περπάτημα με τα πλήκτρα: ποτέ μέσα σε τοίχο
    let walked = 0, inwall = 0, n = 0, last = s, rng = 7;
    const rnd = () => (rng = (rng * 1103515245 + 12345) % 2147483648) / 2147483648;
    const moves = [['KeyW'], ['KeyW', 'ArrowLeft'], ['KeyW', 'ArrowRight'], ['KeyW', 'KeyD'], ['KeyW', 'KeyA'], ['KeyS'], ['ArrowRight'], ['ArrowLeft'], ['KeyW', 'ShiftLeft'], ['KeyW', 'ShiftLeft', 'ArrowRight']];
    for (let k = 0; k < 46; k++) {
      const mv = moves[Math.floor(rnd() * moves.length)];
      for (const c of mv) await p.keyboard.down(c);
      for (let t = 0; t < 4 + Math.floor(rnd() * 6); t++) { await p.waitForTimeout(90); s = await S(); n++; if (!(await isFree(s))) inwall++; walked += Math.hypot(s.x - last.x, s.y - last.y); last = s; }
      for (const c of mv) await p.keyboard.up(c);
    }
    s = await idle();
    need(inwall === 0, 'με τα πλήκτρα βρέθηκε ' + inwall + ' φορές μέσα σε τοίχο / έπιπλο');
    need(walked > 6, 'με τα πλήκτρα περπάτησε μόνο ' + walked.toFixed(1) + ' m');
    console.log('πλήκτρα: ' + walked.toFixed(1) + ' m σε ' + n + ' δείγματα · μέσα σε τοίχο ' + inwall + ' · κατέληξε: ' + s.room);
    // 3. σύρσιμο = βλέμμα
    const mx = phone ? 200 : 900, my = phone ? 560 : 500;
    await chip('#rooms', 'Σαλόνι'); s = await idle(); const y1 = s.yaw, x1 = [s.x, s.y];
    await p.mouse.move(mx, my); await p.mouse.down(); await p.mouse.move(mx + 150, my + 30, { steps: 8 }); await p.mouse.up(); await p.waitForTimeout(150);
    s = await S(); need(Math.abs(s.yaw - y1) > 0.15 && s.pit > 0 && s.x === x1[0] && s.y === x1[1], 'το σύρσιμο δεν γύρισε το βλέμμα ' + JSON.stringify([y1, s.yaw, s.pit]));
    // 4. κάθε χώρος από το κουμπί του, και κάθε σημείο της λίστας του
    const rooms = await p.$$eval('#rooms button', (bs) => bs.map((x) => x.textContent));
    const ids = await p.evaluate(() => D.rooms3.map((r) => [r.id, r.short, r.name]));
    for (const [id, short, name] of ids) {
      need(await chip('#rooms', short), 'λείπει το κουμπί ' + short);
      s = await idle(); await p.waitForTimeout(120);
      const st = await p.evaluate((id) => window.__k12.stand(id), id);
      need(s.room === id && Math.hypot(s.x - st[0], s.y - st[1]) < 0.05, short + ': δεν έφτασε στη θέση του ' + JSON.stringify([s.room, s.x, s.y]));
      need((await p.evaluate(() => document.getElementById('ttl').textContent)) === name, short + ': λάθος τίτλος');
      const us = await p.$$eval('#pts .row', (rs) => rs.map((x) => x.dataset.u));
      let ok = 0;
      let out = 0;
      for (const u of us) {
        await p.evaluate((u) => { document.querySelector('.row[data-u="' + CSS.escape(u) + '"]').click(); }, u);
        s = await idle(); await p.waitForTimeout(140);
        const ls = await labelState(p, u), its = await p.evaluate((u) => D.items.find((i) => i.u === u).rooms, u);
        if (goodLabel(ls) && s.sel === u && its.indexOf(s.room) >= 0 && (await isFree(s))) ok++; else bad.push('περιήγηση ' + short + ' ' + u + ' ' + JSON.stringify(ls) + ' ' + JSON.stringify([s.x.toFixed(2), s.y.toFixed(2), s.room, s.sel]));
        if (s.room !== id) { out++; await chip('#rooms', short); await idle(); }      // σημείο της εξωτερικής παρειάς: σε βγάζει στον εξώστη για να το δεις – γύρνα πίσω για το επόμενο
      }
      const gs = await p.$$eval('#how .how', (rs) => rs.map((x) => x.dataset.g));
      for (const g of gs) {
        await p.evaluate((g) => { document.querySelector('.how[data-g="' + CSS.escape(g) + '"]').click(); }, g);
        s = await idle(); await p.waitForTimeout(100);
        if (!(await p.evaluate(() => !document.getElementById('card').hidden && document.getElementById('cb').textContent.length > 40)) || !(await isFree(s))) bad.push('περιήγηση ' + short + ' τοίχος ' + g);
        if (s.room !== id) { out++; await chip('#rooms', short); await idle(); }
      }
      wtotal += us.length;
      console.log('μέσα:', short.padEnd(12), 'σημεία', String(us.length).padStart(2), 'ok', String(ok).padStart(2), '· τοίχοι', gs.length, out ? '· ' + out + ' σε πήγαν στον διπλανό χώρο / εξώστη' : '');
    }
    // 5. διάφανοι / κλειστοί τοίχοι
    await p.evaluate(() => document.getElementById('cx').click()); await p.waitForTimeout(100);
    need(await chip('#views', 'Διάφανοι'), 'λείπει το κουμπί «Διάφανοι»'); await p.waitForTimeout(250); need((await S()).solid === false, 'δεν έγιναν διάφανοι οι τοίχοι');
    need(await chip('#views', 'Κλειστοί'), 'λείπει το κουμπί «Κλειστοί»'); await p.waitForTimeout(250); need((await S()).solid === true, 'δεν έκλεισαν οι τοίχοι');
    // 6. χάρτης: πάτημα στην κουζίνα → πάει εκεί
    await chip('#rooms', 'Σαλόνι'); await idle();
    const kst = await p.evaluate(() => { const t = window.__k12.stand('kouzina'); return window.__k12.map(t[0] + 1.2, t[1]); });
    await p.mouse.click(kst[0], kst[1]); s = await idle();
    need(s.room === 'kouzina' && (await isFree(s)), 'χάρτης: δεν πήγε στην κουζίνα ' + JSON.stringify([s.room, s.x, s.y]));
    // 7. πάτημα στο πάτωμα: πάει εκεί (από το σαλόνι, κοιτώντας μέσα)
    await chip('#rooms', 'Σαλόνι'); s = await idle(); await p.waitForTimeout(150);
    const fx = phone ? 195 : 930, fy = phone ? 600 : 760, b0 = s;
    await p.mouse.click(fx, fy); await p.waitForTimeout(80); s = await idle();
    need(Math.hypot(s.x - b0.x, s.y - b0.y) > 0.4 && (await isFree(s)), 'πάτημα στο πάτωμα: δεν περπάτησε ' + JSON.stringify([b0.x, b0.y, s.x, s.y]));
    // 8. μοχλός (οθόνες αφής / στενές): σπρώξιμο μπροστά
    if (phone) {
      await chip('#rooms', 'Σαλόνι'); s = await idle(); const j0 = s;
      const jr = await p.evaluate(() => { const r = document.getElementById('joy').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2, r.height / 2]; });
      await p.mouse.move(jr[0], jr[1]); await p.mouse.down(); await p.mouse.move(jr[0], jr[1] - jr[2] * 0.9, { steps: 4 }); await p.waitForTimeout(900);
      const mid = await S(); await p.mouse.up(); s = await idle();
      need(Math.hypot(mid.x - j0.x, mid.y - j0.y) > 0.5 && (await isFree(s)), 'μοχλός: δεν περπάτησε ' + JSON.stringify([j0.x, j0.y, mid.x, mid.y]));
    }
    // 9. έξοδος → ο χώρος από έξω· 10. άνοιγμα κατευθείαν μέσα
    need(await chip('#views', 'Βγες'), 'λείπει το κουμπί «Βγες έξω»'); await p.waitForTimeout(500); s = await S();
    need(!s.wk && (await p.evaluate(() => document.getElementById('mm').hidden && !document.body.classList.contains('wk') && location.hash !== '#mesa')), 'δεν βγήκε από την περιήγηση');
    await p.close();
    const p2 = await open('mesa');
    need(await p2.evaluate(() => window.__k12.s.wk && window.__k12.s.room === 'saloni'), 'το #mesa δεν άνοιξε μέσα στο σπίτι');
    await p2.close();
  }

  await b.close();
  console.log('σφάλματα κονσόλας:', errs.length, errs.slice(0, 5).join(' | '));
  console.log('ΕΛΕΓΧΟΣ 3D (' + vp.width + ' px): ' + total + ' επιλογές από έξω · ' + wtotal + ' στην περιήγηση · ' + (bad.length + errs.length) + ' ΛΑΘΟΣ');
  if (bad.length) console.log(bad.slice(0, 40).join('\n'));
  process.exit(bad.length + errs.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
