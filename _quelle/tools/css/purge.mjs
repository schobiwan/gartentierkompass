import fs from 'fs'; import path from 'path';
import postcss from 'postcss'; import sp from 'postcss-selector-parser';
const site=process.argv[2], cssIn=process.argv[3], cssOut=process.argv[4];
const used=new Set(), ids=new Set(), tags=new Set();
function walk(d){for(const f of fs.readdirSync(d)){const p=path.join(d,f);if(fs.statSync(p).isDirectory())walk(p);else if(p.endsWith('.html')){const h=fs.readFileSync(p,'utf8');
 for(const m of h.matchAll(/class="([^"]*)"/g))m[1].split(/\s+/).forEach(c=>c&&used.add(c));
 for(const m of h.matchAll(/id="([^"]*)"/g))ids.add(m[1]);
 for(const m of h.matchAll(/<([a-z][a-z0-9-]*)/g))tags.add(m[1]);}}}
walk(site);
// JS: every word-like token counts as possibly used (class names set via JS)
const js=['assets/app.js','assets/home.js'].map(f=>fs.readFileSync(path.join(site,f),'utf8')).join('\n');
for(const m of js.matchAll(/[A-Za-z][\w-]*/g)){used.add(m[0]);ids.add(m[0]);}
let removedSel=0, removedRules=0;
const root=postcss.parse(fs.readFileSync(cssIn,'utf8'));
root.walkRules(rule=>{
  if(rule.parent && rule.parent.type==='atrule' && /keyframes/.test(rule.parent.name))return;
  const keep=[];
  sp(sels=>{sels.each(sel=>{let ok=true;
    sel.walk(n=>{ if(n.type==='class'&&!used.has(n.value))ok=false; if(n.type==='id'&&!ids.has(n.value))ok=false;
      if(n.type==='tag'&&/^[a-z]/.test(n.value)&&!tags.has(n.value)&&!['html','body','svg','path','circle','rect','line','polyline','polygon','g','use','symbol','i','b','strong','em','span','small','picture','source','img','a','p','ul','ol','li','dl','dt','dd','h1','h2','h3','h4','button','input','select','option','label','form','table','thead','tbody','tr','th','td','details','summary','dialog','nav','main','header','footer','section','article','aside','figure','figcaption','abbr','code','kbd','hr','mark','time','sup','sub','to','from'].includes(n.value)) ok=false;});
    if(ok)keep.push(sel.toString().trim()); else removedSel++;});}).processSync(rule.selector);
  if(!keep.length){rule.remove();removedRules++;} else rule.selector=keep.join(',');
});
root.walkAtRules(a=>{ if(a.name==='media'||a.name==='supports'){ if(!a.nodes||!a.nodes.length)a.remove(); }});
fs.writeFileSync(cssOut,root.toString());
console.log('removed selectors',removedSel,'rules',removedRules);
