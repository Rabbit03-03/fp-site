const { chromium } = require('playwright');
const { spawn } = require('child_process');
const [html, out, T] = [process.argv[2], process.argv[3], +process.argv[4]];
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + html); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(1500);
  const ff = spawn(process.env.FF, ['-y','-f','image2pipe','-framerate','30','-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart', out], { stdio: ['pipe','ignore','inherit'] });
  for (let f = 0; f < T * 30; f++) {
    await p.evaluate(t => render(t), f / 30);
    const buf = await p.screenshot({ type: 'jpeg', quality: 90 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
