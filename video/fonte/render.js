// usage: node render.js stills t1,t2,...   |  node render.js video out.mp4 [fps]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
(async () => {
  const [mode, arg, fpsArg] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const errs = [];
  p.on('pageerror', e => errs.push(e.message)); p.on('console', m => m.type()==='error' && errs.push(m.text()));
  await p.goto('file://' + path.join(__dirname, 'motion.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  if (errs.length) console.log('ERRORS', errs);
  const dur = await p.evaluate(() => TL.duration());
  console.log('duration', dur);
  if (mode === 'stills') {
    for (const t of arg.split(',').map(Number)) {
      await p.evaluate(t => { for (let f = 0; f <= Math.round(t*30); f++) TL.seek(f/30, false); }, t);
      await p.screenshot({ path: path.join(__dirname, 'stills', `t${String(t).padStart(6,'0')}.png`) });
    }
  } else {
    const fps = Number(fpsArg || 30), n = Math.round(dur * fps);
    const ff = spawn('ffmpeg', ['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-',
      '-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium','-movflags','+faststart', arg], { stdio: ['pipe','inherit','inherit'] });
    for (let i = 0; i < n; i++) {
      await p.evaluate(t => { TL.seek(t, false); }, i / fps);
      const buf = await p.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 300 === 0) console.log('frame', i, '/', n);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    console.log('done');
  }
  await b.close();
})();
