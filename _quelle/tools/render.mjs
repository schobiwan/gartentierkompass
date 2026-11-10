import { Resvg } from '@resvg/resvg-js';
import fs from 'fs';
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const fontFiles = ['ttf/YoungSerif.ttf','ttf/Atkinson-700.ttf','ttf/Atkinson-400.ttf'];
for (const j of jobs) {
  const r = new Resvg(j.svg, { fitTo: { mode: 'width', value: j.width }, font: { fontFiles, loadSystemFonts: false, defaultFontFamily: 'Atkinson Hyperlegible Next' } });
  fs.writeFileSync(j.out, r.render().asPng());
}
console.log('rendered', jobs.length);
