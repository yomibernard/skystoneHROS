"""Finds text that spills out of its box (like figures overlapping in a card) on every screen, for every role, on desktop and phone."""
import os
from playwright.sync_api import sync_playwright
U='file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','index.html'))
JS="""()=>{const out=[];document.querySelectorAll('#view .band .v, #view .band .k, #view .v, #view h1, #view h2, #view .tag, #view .btn, #view td, #view .limitbox strong, #view .okrp, #view .sgrid .v').forEach(el=>{const r=el.getBoundingClientRect();if(!r.width)return;if(el.scrollWidth>el.clientWidth+2&&getComputedStyle(el).overflow==='visible'&&el.tagName!=='TD')out.push(el.className+': '+el.textContent.trim().slice(0,40));});
document.querySelectorAll('#view .band').forEach(b=>{const vs=[...b.querySelectorAll('.v')].map(v=>v.getBoundingClientRect());for(let i=1;i<vs.length;i++){if(Math.abs(vs[i].top-vs[i-1].top)<4&&vs[i].left<vs[i-1].right-2)out.push('band overlap: '+b.textContent.trim().slice(0,60));}});return out;}"""
res=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw in [(1366,768),(1024,768),(390,844)]:
        pg=b.new_page(viewport={'width':vw[0],'height':vw[1]}); pg.goto(U); pg.evaluate('localStorage.clear()'); pg.reload(); pg.wait_for_timeout(300)
        pg.evaluate("__pos.as('hr')"); pg.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('skystone-people-os-v1'));Object.values({a:1}).forEach(()=>{});['employee','manager','hr','hoh','payroll','finance','md','admin','talent','audit'].forEach(k=>{});localStorage.setItem('x','1');})()")
        ids=pg.evaluate("__pos.roles().map(r=>{__pos.as(r);return JSON.parse(localStorage.getItem('skystone-people-os-v1')).uid;})")
        pg.evaluate("(ids)=>{const s=JSON.parse(localStorage.getItem('skystone-people-os-v1'));ids.forEach((id,i)=>{s.pay.loans[id]={type:'Staff loan',principal:2660000+i*111111,balance:2660000+i*111111,monthly:222200,start:'2026-11-16'};});localStorage.setItem('skystone-people-os-v1',JSON.stringify(s));}",ids); pg.reload(); pg.wait_for_timeout(300)
        for role in pg.evaluate('__pos.roles()'):
            pg.evaluate(f"__pos.as('{role}')"); pg.wait_for_timeout(100)
            for r in list(dict.fromkeys(pg.evaluate("Array.from(document.querySelectorAll('#nav a')).map(a=>a.getAttribute('href').slice(1))"))):
                pg.goto(U+'#'+r); pg.wait_for_timeout(120)
                for x in pg.evaluate(JS): res.append((vw[0],role,r,x))
    seen=set()
    for x in res:
        k=(x[0],x[2],x[3])
        if k in seen: continue
        seen.add(k); print(x)
    print('TOTAL',len(seen))
