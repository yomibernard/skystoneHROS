import re, json
from playwright.sync_api import sync_playwright
import os
U='file://'+os.path.abspath(os.path.join(os.path.dirname(__file__),'..','index.html'))
BAD=re.compile(r'\b(undefined|NaN|Infinity|\[object Object\]|null)\b')
issues=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw,mode in [((1440,900),'desktop'),((390,844),'phone')]:
        pg=b.new_page(viewport={'width':vw[0],'height':vw[1]}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(U); pg.evaluate('localStorage.clear()'); pg.reload(); pg.wait_for_timeout(400); pg.evaluate("__pos.as('employee')"); pg.wait_for_timeout(200)
        roles=pg.evaluate('__pos.roles()')
        for role in roles:
            pg.evaluate(f"__pos.as('{role}')"); pg.wait_for_timeout(150)
            routes=pg.evaluate("Array.from(document.querySelectorAll('#nav a, #bnav a')).map(a=>a.getAttribute('href').slice(1))")
            routes=list(dict.fromkeys(routes))
            if mode=='phone':
                pg.goto(U+'#home'); pg.wait_for_timeout(150)
                routes=pg.evaluate("Array.from(document.querySelectorAll('#nav a')).map(a=>a.getAttribute('href').slice(1))") or routes
            for r in routes:
                pg.goto(U+'#'+r); pg.wait_for_timeout(180)
                def check(where):
                    t=pg.inner_text('main')
                    for mm in BAD.finditer(t):
                        ctx=t[max(0,mm.start()-50):mm.end()+30].replace('\n',' ')
                        issues.append([mode,role,where,'bad text',ctx])
                    d=pg.evaluate("(()=>{const c={};document.querySelectorAll('[id]').forEach(e=>c[e.id]=(c[e.id]||0)+1);return Object.keys(c).filter(k=>c[k]>1)})()")
                    if d: issues.append([mode,role,where,'duplicate ids',','.join(d[:6])])
                    if mode=='phone':
                        sw=pg.evaluate('document.documentElement.scrollWidth')
                        if sw>392: issues.append([mode,role,where,'overflow',str(sw)])
                    if errs: issues.append([mode,role,where,'script error',errs[0][:150]]); errs.clear()
                check(r)
                tabs=pg.evaluate("Array.from(document.querySelectorAll('[data-ptab],[data-ttab]')).map(b=>b.dataset.ptab?'[data-ptab=\"'+b.dataset.ptab+'\"]':'[data-ttab=\"'+b.dataset.ttab+'\"]')")
                for tsel in tabs[1:] if mode=='desktop' else []:
                    try: pg.click(tsel); pg.wait_for_timeout(150); check(r+' '+tsel)
                    except Exception as e: issues.append([mode,role,r,'tab click',str(e)[:80]])
                if mode=='desktop':
                    rows=pg.query_selector_all('main tr.click, main .org')
                    if rows:
                        try:
                            rows[0].click(); pg.wait_for_timeout(200)
                            if pg.evaluate("document.getElementById('drawer').classList.contains('open')"):
                                t=pg.inner_text('#drawer')
                                for mm in BAD.finditer(t): issues.append([mode,role,r+' drawer','bad text',t[max(0,mm.start()-50):mm.end()+30].replace('\n',' ')])
                            if errs: issues.append([mode,role,r+' drawer','script error',errs[0][:150]]); errs.clear()
                            pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
                        except Exception as e: issues.append([mode,role,r,'drawer click',str(e)[:80]])
        pg.close()
seen=set(); out=[]
for i in issues:
    k=(i[0],i[3],i[4][:60])
    if k in seen: continue
    seen.add(k); out.append(i)
for i in out: print(' | '.join(i))
print('TOTAL', len(issues), 'unique', len(out))
