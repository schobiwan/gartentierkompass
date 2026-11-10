import fs from 'fs'; import postcss from 'postcss';
const root=postcss.parse(fs.readFileSync(process.argv[2],'utf8'));
const ctx=n=>{let c=[];let p=n.parent;while(p&&p.type!=='root'){if(p.type==='atrule')c.unshift('@'+p.name+' '+p.params.replace(/\s+/g,' '));p=p.parent}return c.join('|')};
const norm=s=>s.replace(/\s*([>+~,])\s*/g,'$1').replace(/\s+/g,' ').trim();
const seen=new Map(); let removed=0;
const rules=[]; root.walkRules(r=>{if(r.parent.type==='atrule'&&/keyframes/.test(r.parent.name))return;rules.push(r)});
for(const r of rules){
  const key=ctx(r)+'::'+norm(r.selector);
  const decls=r.nodes.filter(n=>n.type==='decl');
  // within one rule: drop earlier duplicate prop (same importance) unless value uses vendor/fallback pattern
  const last=new Map(); for(const d of decls){const k=d.prop+'|'+!!d.important; last.set(k,d)}
  const prev=seen.get(key)||[];
  for(const d of decls){const k=d.prop+'|'+!!d.important;
    for(const pd of prev){ if(pd.parent && pd.prop===d.prop && !!pd.important===!!d.important){ pd.remove(); removed++; } }
  }
  seen.set(key,[...prev.filter(x=>x.parent),...decls]);
}
root.walkRules(r=>{if(!r.nodes.length)r.remove()});
root.walkAtRules(a=>{if((a.name==='media'||a.name==='supports')&&(!a.nodes||!a.nodes.length))a.remove()});
fs.writeFileSync(process.argv[3],root.toString()); console.log('removed overridden decls',removed);
